from django.contrib import admin

from djangobot.models import Jerk


class JerkAdmin(admin.ModelAdmin):
    model = Jerk


admin.site.register(Jerk, JerkAdmin)
