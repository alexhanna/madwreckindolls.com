from accounts.models import SkaterStatus, SkateSession, SkateSessionPaymentSchedule, SkateSessionPaymentAmount
from django.contrib import admin


class SkateSessionPaymentAmountInline(admin.TabularInline):
    model = SkateSessionPaymentAmount

class SkateSessionPaymentScheduleAdmin(admin.ModelAdmin):
    inlines = (SkateSessionPaymentAmountInline,)


admin.site.register(SkaterStatus)
admin.site.register(SkateSessionPaymentSchedule, SkateSessionPaymentScheduleAdmin)
admin.site.register(SkateSession)
