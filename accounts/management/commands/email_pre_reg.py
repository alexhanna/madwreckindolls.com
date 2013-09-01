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

        count = 1

        skaters = Skater.objects.filter(pk=1)
        #skaters = Skater.objects.all()

        for skater in skaters:

            html = render_to_string('emails/pre-reg-invite.html',
                    {
                        'skater' : skater,
                        'skater_short_name': skater.get_short_name(),
                    }
                )

            msg = EmailMultiAlternatives(
                "Mad Wreckin' Dolls Fall 2013 Registration",
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

