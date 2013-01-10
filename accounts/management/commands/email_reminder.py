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

        for file in args:
          with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            count = 1
            for row in reader:
                email = row[0]
                try:
                    skater = Skater.objects.get(email__exact=email)

                    html = render_to_string('emails/pre-reg-reminder.html',
                        {
                            'skater' : skater,
                            'skater_short_name': skater.get_short_name(),
                        }
                    )

                    msg = EmailMultiAlternatives(
                        "Reminder - Mad Wreckin' Dolls 2013 Spring Registration",
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
                    self.stdout.write(str(count) + " OKAY " + skater.email)


                except Skater.DoesNotExist:
	                self.stdout.write( str(count) + " NOT FOUND ------- " + skater.email )

                count = count + 1



