from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus
import csv
from mwd import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

"""

Fields in CSV:

0           1           2           3               4           5       6       7    8       9      10
first_name  last_name   email       


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
                    email = row[2]
                    try:
                        skater = Skater.objects.get(email__exact = email)
                        self.stdout.write( str(count) + " EXISTS ALREADY " + email )
                    except Skater.DoesNotExist:
                        skater = False
                    
                    if skater is False:
                        try:
                            skater = Skater.objects.create_user(email, Skater.objects.make_random_password())
                            skater.status = SkaterStatus.objects.get(name__exact = settings.REGISTRATION_INACTIVE_STATUS)

                            skater.first_name = row[1]
                            skater.last_name = row[0]

                            skater.save()
                            self.stdout.write( str(count) + " CREATED ACCOUNT " + email )

                        except:
                            skater = False
                            self.stdout.write( str(count) + "OH CRAP ----- Problem importing row: " + email )


                    if skater:

                        html = render_to_string('emails/pre-reg-invite.html',
                            {
                                'skater' : skater,
                                'skater_short_name': skater.get_short_name(),
                            }
                        )

                        msg = EmailMultiAlternatives(
                            "Mad Wreckin' Dolls Registration Invite",
                            html,
                            settings.FROM_EMAIL,
                            [ skater.email ],
                            [ settings.FROM_EMAIL ],
                            headers = {
                                'Reply-To' : settings.FROM_EMAIL,
                                'CC' : "finance@madwreckindolls.com",
                                'Content-Type' : 'text/html'
                            },
                        )

                        msg.content_subtype = "html"
                        msg.send(fail_silently = False)

                        self.stdout.write( str(count) + "\t OK! " + email )

