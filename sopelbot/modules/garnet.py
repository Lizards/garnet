import re
import sys
import os
import datetime
import calendar
import random

import django
from django.db import IntegrityError

from sopel import module
from sopel.tools import OutputRedirect

# Make Django work
sys.path.append(os.path.dirname('{}/djangobot'.format(os.getcwd())))
sys.path.append(os.path.dirname('{}/djangobot/djangobot'.format(os.getcwd())))
sys.path.append(os.path.dirname('{}/djangobot/personality'.format(os.getcwd())))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangobot.settings")

try:
    django.setup()
except RuntimeError as e:
    pass # Raises this error when module is reloaded on the fly from IRC command

from django.core.cache import cache
from django.db import connection
from djangobot.models import Jerk
from personality.models import Personality, Category, Keyword, Quote

PERSONALITY = Personality.objects.get(slug=os.environ.get('BOT_PERSONALITY'))
INTERVAL_TIMEOUT = int(os.environ.get('INTERVAL_TIMEOUT')) # Seconds before a quote becomes usable again
TIMEOUT = int(os.environ.get('TIMEOUT')) # Seconds between quotes
JERKS = [jerk.nick.lower() for jerk in Jerk.objects.all()] # List of nicknames to thwart


# Execute on module load
def setup(bot):
    bot.memory['garnet'] = DumbAI(bot, personality=PERSONALITY, timeout=TIMEOUT, interval_timeout=INTERVAL_TIMEOUT, jerks=JERKS)


# React to everything said in channel or message
@module.rule('.*')
def react(bot, trigger):

    instance = bot.memory.get('garnet')
    maybe_bot_nick = trigger.group().split()[0]
    instance.logger.write(trigger.group())

    # A command issued to the bot
    if maybe_bot_nick.lower().startswith(bot.nick.lower()):
        instance.manage_quotes(bot, trigger)
    else:
        # Conversation
        if instance.running and not trigger.sender.is_nick():
            instance.react(bot, trigger)


class DumbAI(object):
    def __init__(self, bot, personality, timeout, interval_timeout, jerks, jerk_protection=True, bot_log='bot.log'):

        self.logger = OutputRedirect(f'{bot.config.core.logdir}/{bot_log}', stderr=True, quiet=True)
        sys.stdout = self.logger
        sys.stderr = self.logger

        self.running = True
        self.timeout = timeout
        self.interval_timeout = interval_timeout
        self.personality = personality

        # Protect against abuse from Jerks
        self.last_reacted = { 'user': None, 'timestamp': None }
        self.jerk_protection = jerk_protection
        self.jerks = jerks

        # Store a list of all methods that begin with _action_
        self.actions = sorted(method[8:] for method in dir(self) if method[:8] == '_action_')
        
        # Populate self.keywords and self.categories
        self._populate_trigger_cache(bot)

    def check_for_django_updates(self, bot):
        if cache.get('refresh_triggers'): # Keywords or Categories have been updated in Django, so refresh bot's local cache
            cache.delete('refresh_triggers')
            self.logger.write('Django update detected')
            self._populate_trigger_cache(bot)

    def react(self, bot, trigger):
        ''' Say an appropirate quote according to first keyword found in message '''

        if self._throttle_jerks(bot, trigger):
            return

        self.check_for_django_updates(bot)

        forced = trigger.group().lower() == "summon garnet"

        timestamp_now = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        if forced or not self.last_reacted['timestamp'] or timestamp_now - self.last_reacted['timestamp'] > (self.timeout):
            result = re.search(self.trigger_regex, trigger)
            if result:
                connection.close() # https://code.djangoproject.com/ticket/21597#comment:29
                timeout_threshhold = datetime.datetime.utcnow() - datetime.timedelta(seconds=self.interval_timeout)
                if forced:
                    potential_quotes = Quote.objects.filter(last_used__lt=timeout_threshhold, category__personality=personality)
                else:
                    category = self.keywords[result.group().lower()].category
                    potential_quotes = Quote.objects.filter(category=category).filter(last_used__lt=timeout_threshhold)
                if len(potential_quotes):
                    rand_quote_result = random.choice(potential_quotes)
                    getattr(bot, rand_quote_result.action)(rand_quote_result.quote_text)

                    rand_quote_result.save() # Bump 'last_used' timestamp
                    self.last_reacted['timestamp'] = timestamp_now
                    self.last_reacted['user'] = trigger.nick

    def manage_quotes(self, bot, trigger):
        """ Manage quote database via IRC messages to the bot. """
        self.check_for_django_updates(bot)

        text = trigger.group().split()
        if (len(text) < 2 or text[1] not in self.actions):
            self._generic_help(bot, trigger)
            return
        getattr(self, '_action_{}'.format(text[1]))(bot, trigger)

    def _populate_trigger_cache(self, bot):
        """ Store categories and keywords in module instance, so we do not need to ask the db every time. """
        connection.close() # https://code.djangoproject.com/ticket/21597#comment:29

        self.keywords = {} # Local cache of keyword list from DB
        self.categories = {} # Local cache of category list from DB

        # Cache all Keyword objects in a dict by keyword.name
        keywords = Keyword.objects.filter(category__personality=self.personality)
        for keyword in keywords:
            self.keywords[keyword.name] = keyword

        # Cache all Category objects in a dict by category.name
        categories = Category.objects.filter(personality=self.personality)
        for category in categories:
            self.categories[category.name] = category

        # Create a simple regex to match on all keywords.  The bot uses this to react to statements.
        keyword_list = list((r'\b%s\b' % key) for key in self.keywords)
        self.trigger_regex = re.compile('|'.join(keyword_list), flags=re.IGNORECASE)
        self.logger.write('Repopulated trigger cache')

    def _throttle_jerks(self, bot, trigger):
        if self.last_reacted['user'] and self.jerk_protection:
            if trigger.nick == self.last_reacted['user'] and trigger.nick.lower() in self.jerks:
                return True
        return False

    def _action_add(self, bot, trigger):
        """ add <keyword|category|quote> category:<category_name> <value> """
        text = trigger.group().split()
        if len(text) < 2:
            return
        if text[2] in ['keyword', 'category', 'quote', 'action']:
            connection.close() # https://code.djangoproject.com/ticket/21597#comment:29
            getattr(self, '_add_{}'.format(text[2]))(bot, trigger)
        else:
            bot.notice(f'The command "{text[2]}" is invalid', trigger.nick)

    def _action_list(self, bot, trigger):
        """ List available categories, or keywords by category
            list categories
            list keywords category:<category_name>
        """
        text = trigger.group().split()
        if len(text) < 3:
            return
        if text[2] in ['categories', 'keywords']:
            getattr(self, '_list_{}'.format(text[2]))(bot, trigger)
        else:
            bot.notice(f'The command "{text[2]}" is invalid', trigger.nick)

    def _add_keyword(self, bot, trigger):
        ''' add keyword category:<category_name> <keyword> '''
        text = trigger.group().split()
        try:
            if re.match(r'category:', text[3]):
                category_name = text[3].split(":")[1].lower()
                if category_name not in self.categories.keys():
                    bot.notice('That category is invalid', trigger.nick)
                    return
            else:
                bot.notice("Category is required to add a keyword.  I'll send you the list.", trigger.nick)
                self._list_categories(bot, trigger)
                return

            keyword = self._strip_quotes(" ".join(text[4:])).lower()
            if keyword in self.keywords:
                bot.reply("no")
                return

        except IndexError:
            return

        try:
            new_keyword = Keyword(name=keyword, category=self.categories[category_name])
            new_keyword.save()
        except IntegrityError as e:
            bot.reply(f'no: {str(e)}')
            return

        self._populate_trigger_cache(bot)
        self.logger.write(f'User {trigger.nick} added keyword: {keyword}\n')
        bot.reply(f'Added keyword "{keyword}" to category "{category_name}"')

    def _list_keywords(self, bot, trigger):
        ''' list keywords category:<category_name> '''
        text = trigger.group().split()
        if (len(text) < 4 or not re.match(r'category:', text[3])):
            self._show_doc(bot, 'list', trigger.nick)
            return
        category = self.categories.get(text[3].split(":")[1])
        if category:
            bot.notice("Keywords in category {}: {}".format(
                category.name,
                ', '.join(keyword for keyword in self.keywords if self.keywords[keyword].category.name == category.name)
            ), trigger.nick)

    def _add_category(self, bot, trigger):
        ''' add category <category_name> '''
        text = trigger.group().split()
        try:
            category = self._strip_quotes(text[3]).lower()
            if category in self.categories:
                bot.reply("no")
                return
        except IndexError:
            return

        try:
            new_category = Category(name=category, personality=self.personality)
            new_category.save()
        except IntegrityError as e:
            bot.reply("no: {}".format(str(e)))
            return

        self._populate_trigger_cache(bot)
        self.logger.write("user {} added category: {}\n".format(trigger.nick, category))
        bot.reply('Added category "{}"'.format(category))

    def _list_categories(self, bot, trigger):
        ''' BotName: list categories '''
        bot.notice("Available categories: {}".format(
            ', '.join(self.categories[key].name for key in self.categories)),
        trigger.nick)

    def _add_action(self, bot, trigger):
        ''' BotName: add action category:<category_name> <quote text> '''
        self._add_quote(bot, trigger, action='action')

    def _add_quote(self, bot, trigger, action='say'):
        ''' BotName: add quote category:<category_name> <quote text> '''
        text = trigger.group().split()
        try:
            position = 3
            if re.match(r'category:', text[3]):
                category_name = text[3].split(":")[1].lower()
                position = 4
                if category_name not in self.categories.keys():
                    bot.reply('That category is invalid')
                    return
            else:
                category_name = 'default'
        except IndexError:
            return

        quote = self._strip_quotes(" ".join(text[position:]))

        try:
            new_quote = Quote(quote_text=quote, action=action, category=self.categories[category_name])
            new_quote.save()
        except IntegrityError as e:
            bot.reply("no: {}".format(str(e)))
            return

        self.logger.write("user {} added quote: {} {}\n".format(trigger.nick, category_name, quote))
        bot.reply('Added {} "{}" to category "{}"'.format("action" if action == "action" else "quote", quote, category_name))

    def _action_start(self, bot, trigger):
        """ Start responding (ops only). """
        if trigger.owner or trigger.isop:
            bot.reply("I'm willing to have the conversation" if not self.running else
                      "I'm not disagreeing")
            self.running = True

    def _action_stop(self, bot, trigger):
        """ Stop responding (ops only). """
        if trigger.owner or trigger.isop:
            bot.reply("I am no longer willing to have the conversation" if self.running else
                      "afk, dead")
            self.running = False

    def _action_help(self, bot, trigger):
        """ Get help """
        text = trigger.group().split()
        try:
            self._show_doc(bot, text[2], trigger.nick)
        except Exception:
            self._generic_help(bot, trigger)

    def _generic_help(self, bot, trigger):
        bot.notice(f"Available commands: {', '.join(self.actions)}", trigger.nick)
        bot.notice(f"Type '{bot.nick}: help <command>' for more", trigger.nick)

    def _strip_quotes(self, text):
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text

    def _show_doc(self, bot, command, recipient):
        """Given a command, say the docstring for the corresponding method."""
        for line in getattr(self, '_action_{}'.format(command)).__doc__.split('\n'):
            line = line.strip()
            if line:
                bot.notice(line.replace(r'BotName', bot.nick), recipient)
