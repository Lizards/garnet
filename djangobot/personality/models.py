from django.db import models
from django.core.cache import cache
from django.utils.text import slugify


class PersonalityManager(models.Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Personality(models.Model):

    objects = PersonalityManager()

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = "personalities"

    def natural_key(self):
        return (self.slug,)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Personality, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class CategoryManager(models.Manager):

    def get_by_natural_key(self, name, personality_slug):
        return self.get(name=name, personality__slug=personality_slug)


class Category(models.Model):

    class Meta:
        verbose_name_plural = "categories"
        unique_together = (("name", "personality"),)

    objects = CategoryManager()

    name = models.CharField(max_length=128)
    personality = models.ForeignKey(Personality, on_delete=models.CASCADE)

    def natural_key(self):
        return (self.name, self.personality.slug)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        cache.set('refresh_triggers', True)

    def delete(self, *args, **kwargs):
        super(Category, self).delete(*args, **kwargs)
        cache.set('refresh_triggers', True)

    def __str__(self):
        return self.name


class KeywordManager(models.Manager):

    def get_by_natural_key(self, name, category):
        return self.get(name=name, category=category)


class Keyword(models.Model):

    class Meta:
        unique_together = (("name", "category"),)

    objects = KeywordManager()

    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def natural_key(self):
        return (self.name, self.category)

    def save(self, *args, **kwargs):
        super(Keyword, self).save(*args, **kwargs)
        cache.set('refresh_triggers', True)

    def delete(self, *args, **kwargs):
        super(Keyword, self).delete(*args, **kwargs)
        cache.set('refresh_triggers', True)

    def __str__(self):
        return self.name


class Quote(models.Model):

    class Meta:
        unique_together = (("quote_text", "category"),)

    quote_text = models.CharField(max_length=255)
    action = models.CharField(max_length=10, choices=(('action', '/me'), ('say', 'say'),), default='say')
    added = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.quote_text
