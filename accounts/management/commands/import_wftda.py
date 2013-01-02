from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater
import csv
from mwd import settings


"""

Fields in CSV:

0           1           2           
first_name  last_name   wftda       

"""

class Command(BaseCommand):
    args = "<path to csv file>"
    help = "Import WFTDA numbers"

    def handle(self, *args, **options):
        count = 0
        for file in args:
          with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                count = count + 1
                if count != 1:
                    first_name = row[0]
                    last_name = row[1]

                    if row[2] != "":

                        try:
                            skater = Skater.objects.get(first_name__exact=first_name, last_name__exact=last_name)
                        except Skater.DoesNotExist:
                            skater = False
                            self.stdout.write( str(count) + " !!!!!!!!!!!!!!! OH CRAP ----- Problem with: " + first_name + " " + last_name  + " WFTDA #" + row[2])

                        if skater:
                            skater.wftda_number = row[2]
                            skater.save()
                            
                            self.stdout.write( str(count) + " OK! WFTDA: " + row[2] + " -- " + skater.email + " (" + skater.first_name + " " + skater.last_name + ")" )

