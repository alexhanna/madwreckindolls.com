"""
" Django Admin settings
"""


class SkateSessionPaymentAmountInline(admin.TabularInline):
    model = SkateSessionPaymentAmount

class SkateSessionPaymentScheduleAdmin(admin.ModelAdmin):
    inlines = (SkateSessionPaymentAmountInline,)


admin.site.register(SkaterStatus)
admin.site.register(SkateSessionPaymentSchedule, SkateSessionPaymentScheduleAdmin)
admin.site.register(SkateSession)
