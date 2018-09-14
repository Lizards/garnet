from django.contrib import admin

from personality.models import Personality, Category, Keyword, Quote


class PersonalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    exclude = ('slug',)


class KeywordInline(admin.TabularInline):
    model = Keyword


class QuoteInline(admin.TabularInline):
    model = Quote


class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        KeywordInline,
        QuoteInline,
    ]
    list_filter = ('personality',)


class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'category',)
    list_filter = ('category',)


class QuoteAdmin(admin.ModelAdmin):
    search_fields = ['quote_text']
    list_display = ('action', 'quote_text', 'category', 'last_used',)
    list_display_links = ('quote_text',)
    list_filter = ('category', 'action',)


admin.site.register(Personality, PersonalityAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Quote, QuoteAdmin)
