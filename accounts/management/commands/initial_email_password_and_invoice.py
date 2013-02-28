from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus, SkateSessionPaymentSchedule, Invoice, generate_scheduled_invoice
from mwd import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from mwd.utilities import get_pronounceable_password

class Command(BaseCommand):
    help = "Send initial email containing a new invoice and a fresh password."

    def handle(self, *args, **options):

        billing_period = 2
        limit = 1
        count = 0

        schedule = SkateSessionPaymentSchedule.objects.get(pk=billing_period)

        #skaters = Skater.objects.all()
        skaters = Skater.objects.filter(pk=1)

        for skater in skaters:
            
            invoiced = False

            "Check if we've already generated an invoice for this user"
            try:
                invoice = Invoice.objects.get(skater=skater, schedule=schedule)
                invoiced = True
            except Invoice.DoesNotExist:
                pass

            if invoiced:
                self.stdout.write( "ALREADY INVOICED - " + skater.get_short_name() )
            else:

                new_password = get_pronounceable_password()
                
                skater.set_password(new_password)
                skater.save()

                generate_scheduled_invoice(skater, schedule)

                sk = Skater.objects.get(id=skater.id)

                self.stdout.write( "$" + str(skater.balance) + "\t" + sk.get_short_name() + "\t" + new_password )


                html = render_to_string('emails/march-dues.html',
                            {
                                'skater' : sk,
                                'skater_short_name': sk.get_short_name(),
                                'new_password': new_password,
                            }
                )

                msg = EmailMultiAlternatives(
                            "Mad Wreckin' Dolls March Dues",
                            html,
                            settings.FROM_EMAIL,
                            # [ skater.email ],
                            [ "dan@silvers.net" ],
                            [ settings.FROM_EMAIL ],
                            headers = {
                                'Reply-To' : settings.FROM_EMAIL,
                                'CC' : "finance@madwreckindolls.com",
                                'Content-Type' : 'text/html'
                            },
                )
                
                msg.content_subtype = "html"
                msg.send(fail_silently = False)
                
                count = count + 1
                if count >= limit:
                     return

