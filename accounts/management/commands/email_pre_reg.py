from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus
import csv
from mwd import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class Command(BaseCommand):
    args = "<path user id>"
    help = "Email pre registration skaters"

    def handle(self, *args, **options):
        count = 0
        for file in args:
          with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                    email = row[0]

                    if email != "":

                        try:
                            skater = Skater.objects.get(email__exact=email)
                        except Skater.DoesNotExist:
                            skater = False
                            self.stdout.write( str(count) + " !!!!!!!!!!!!!!! OH CRAP ----- Problem with: " + email)

                    if skater:

                        #if row[2] != "" and row[2] != skater.derby_name:
                        #    skater.derby_name = row[2]
                        #    skater.save()
                        #if row[3] != "" and row[3] != skater.derby_number:
                        #    skater.derby_number = row[3]
                        #    skater.save()


                        html = render_to_string('emails/pre-reg-invite-simple.html',
                            {
                                'skater' : skater,
                                'skater_short_name': skater.get_short_name(),
                            }
                        )

                        msg = EmailMultiAlternatives(
                                "Mad Wreckin' Dolls Fall 2014 Registration",
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
                	    
                        self.stdout.write( str(count) + " OK! " + skater.email )
                        count = count + 1

