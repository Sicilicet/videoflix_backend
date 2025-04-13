from django.contrib import admin

from watch_history_app.models import WatchHistory


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    fields = ['user', 'video', 'timestamp', 'last_watched']
    readonly_fields = ['last_watched']
