from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus, SkateSessionPaymentSchedule, Invoice, PaymentError
from mwd import settings

class Command(BaseCommand):
    help = "Attempt to charge credit cards for people who have autopay setup."

    def handle(self, *args, **options):

        skaters = Skater.objects.filter(automatic_billing__exact=1).filter(balance__gt=0)

        for skater in skaters:
            
            balance = skater.balance

            try:
                skater.charge_credit_card("AutoPay - " + skater.get_unpaid_invoices_description())
                self.stdout.write( "OK\t" + str(skater) + "\t$" +  str(balance))
            except PaymentError, e:
                self.stdout.write( "PROBLEM\t" + str(skater) + "\t" + str(skater.email) + "\t" +  str(e.value) )

