from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater
import csv
from mwd import settings


"""

Fields in CSV:

0           
email

"""

class Command(BaseCommand):
    args = "<path to csv file>"
    help = "Activate summer skaters"

    def handle(self, *args, **options):
        count = 0
        for file in args:
          with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                count = count + 1
                if count != 1:
                    email = row[0]

                    if row[0] != "":

                        try:
                            skater = Skater.objects.get(email=email)
                        except Skater.DoesNotExist:
                            skater = False
                            self.stdout.write( str(count) + " !!!!!!!!!!!!!!! No match for " + email)

                        if skater:
                            skater.status_id = 1
                            skater.save()
                            
                            self.stdout.write( str(count) + " OK! " + email)

