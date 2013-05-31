from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, Receipt
from mwd import settings
from datetime import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):

        skaters = Skater.objects.all()

        self.stdout.write("".ljust(35) + "STATUS\tCURRENT BAL\tADJUSTMENT\tFIXED BALANCE")

        for skater in skaters:
            
            if skater.status.name == "active":
                fix = 17
            elif skater.status.name == "injured" or skater.status.name == "social":
                fix = 10
            else:
                fix = 0
            

            self.stdout.write(skater.get_short_name().ljust(35) + skater.status.name + "\t" + str(skater.balance) + "\t" + str(fix) + "\t" + str(skater.balance - fix))

            receipt = Receipt(
                    skater = skater,
                    amount = float(fix),
                    fee = 0,
                    method = "cash",
                    method_detail = "Partial May Dues - Credit",
                    date = datetime.now(),
            )
            receipt.save()

            skater.balance = skater.balance - fix
            skater.save()
