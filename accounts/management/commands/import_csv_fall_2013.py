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

                    last_name = row[0]
                    first_name = row[1]
                    derby_name = row[2]
                    derby_number = row[3]
                    email = row[4]
                    level = row[5]
                    wftda = row[6]

                    if email != "":
                        

                        try:
                            skater = Skater.objects.get(email__exact=email)
                        except Skater.DoesNotExist:
                            skater = False
                            self.stdout.write( str(count) + " !!!!!!!!!!!!!!! OH CRAP ----- Problem with: " + first_name + " " + last_name  + " email #" + email)

                        if skater:
                            skater.first_name = first_name
                            skater.last_name = last_name
                            skater.derby_name = derby_name
                            skater.derby_number = derby_number
                            skater.wftda_number = wftda
                            if str(level) != "INJ":
                              skater.last_level = level
                            skater.save()
                            
                            self.stdout.write( str(count) + " OK! " + skater.email + " (" + skater.first_name + " " + skater.last_name + ")" )

