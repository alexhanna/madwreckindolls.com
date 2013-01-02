from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus
import csv
from mwd import settings


"""

Fields in CSV:

0           1           2           3               4           5       6       7    8       9      10
first_name  last_name   derby_name  derby_number    address1    city    state   zip phone   email   date_of_birth

"""

class Command(BaseCommand):
    args = "<path to csv file>"
    help = "Import pre registration skaters"

    def handle(self, *args, **options):
        count = 0
        for file in args:
          with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                count = count + 1
                if count != 1:
                    email = row[9]
                    try:
                        skater = Skater.objects.create_user(email, Skater.objects.make_random_password())
                        skater.status = SkaterStatus.objects.get(name__exact = settings.REGISTRATION_INACTIVE_STATUS)

                        skater.first_name = row[0]
                        skater.last_name = row[1]
                        skater.derby_name = row[2]
                        skater.derby_number = row[3]
                        skater.address1 = row[4]
                        skater.city = row[5]
                        skater.state = row[6]
                        skater.zip = row[7]
                        skater.phone = row[8]
                        if row[10] == "":
                            row[10] = None
                        skater.dob = row[10]

                        skater.save()
                        self.stdout.write( str(count) + " OK! " + email )
                    except:
                        self.stdout.write( str(count) + " OH CRAP ----- Problem importing row: " + email )
