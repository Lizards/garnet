# Garnet

Garnet is a Sopel IRC quote bot with a Django backend.  It reacts contextually to channel conversation.

A version of this bot has been running on IRC for a couple years, collecting quotes from my colleagues.  Its original "personality" is based on an amalgamation of various people we know.

For this demo I created a "conspiracy theorist" personality for the bot.

# Setup

__Docker Compose__ is the only pre-requisite to running the demo.  Clone this repo and start the applications using `docker-compose up`.

Five containers will start:
- An IRC server on port `6667`
- A MySQL server
- The Django development server, exposing the Django admin tool on port `8000`
- The bot, automatically connecting to the the IRC server
- An IRC web client (Kiwi) on port `7778`

Django migrations will run automatically and the database will be populated with fixture data.  Note that it will mount a volume in `$HOME/.garnet` for persistent MySQL data.

Navigate to `http://0.0.0.0:8000` and use credentials `admin:admin` to browse the Django admin tool.  The values in `Keywords` will get a response from the bot on IRC.

# Interacting with the bot

You can connect to IRC through your own client (e.g. Hexchat, irssi) at `0.0.0.0:6667`, or you can use the Kiwi web client at `http://0.0.0.0:7778/` with server settings:

- Server: `ircd`
- Port: `6667`
- Leave `SSL` unchecked

Join channel __#chat__ to talk to Garnet.

```
[03:20:19] <amanda> I need to get lunch
[03:20:19] <Garnet> Enjoy your GMOs!
[03:20:46] <amanda> This bot is annoying
[03:20:46] * Garnet filed off his fingerprints in '96
[03:21:06] <amanda> I heard something about that yesterday
[03:21:06] <Garnet> That idea was implanted by the reptilians to make you addicted to your iPhone
```

Also try private messaging the bot for help: `Garnet: help`

The help menu will explain how to add categories, keywords, and quotes through IRC.

```
[03:13:30] <amanda> Garnet: add category testing
[03:13:30] <Garnet> amanda: Added category "testing"
[03:13:55] <amanda> Garnet: add keyword category:testing shut up
[03:13:55] <Garnet> amanda: Added keyword "shut up" to category "testing"
[03:14:19] <amanda> Garnet: add quote category:testing sit down
[03:14:19] <Garnet> amanda: Added quote "sit down" to category "testing"
[03:15:20] <amanda> shut up
[03:15:20] <Garnet> sit down
```
