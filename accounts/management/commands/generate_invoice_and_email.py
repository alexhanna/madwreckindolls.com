from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus, SkateSessionPaymentSchedule, Invoice, generate_scheduled_invoice
from mwd import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from mwd.utilities import get_pronounceable_password

class Command(BaseCommand):
    help = "Generate an invoice for the selected period and email them."

    def handle(self, *args, **options):

        month_name = "February"
        billing_period = 25
        limit = 200
        count = 0

        schedule = SkateSessionPaymentSchedule.objects.get(pk=billing_period)

        #skaters = Skater.objects.all()
        skaters = Skater.objects.exclude(status=2)
        #skaters = Skater.objects.filter(pk=1)

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

                generate_scheduled_invoice(skater, schedule)

                sk = Skater.objects.get(id=skater.id)
                self.stdout.write( "$" + str(skater.balance) + "\t" + sk.get_short_name() )


                html = render_to_string('emails/new_invoice.html',
                            {
                                'skater' : sk,
                                'skater_short_name': sk.get_short_name(),
                            }
                )

                msg = EmailMultiAlternatives(
                            "Mad Wreckin' Dolls " + month_name + " Dues",
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
                
                count = count + 1
                if count >= limit:
                     return

