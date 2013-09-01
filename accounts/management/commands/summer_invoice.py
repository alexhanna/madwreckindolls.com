from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus, SkateSessionPaymentSchedule, Invoice, generate_scheduled_invoice
from mwd import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import csv

class Command(BaseCommand):
    args = "<csv file>"
    help = "Generate an invoice for the selected period and email them."

    def handle(self, *args, **options):
        
        month_name = "Summer Session (August)"
        due_date = "Thursday, August 8th"

        # 6 - June
        # 7 - July
        # 8 - Aug
        billing_period = 8

        schedule = SkateSessionPaymentSchedule.objects.get(pk=billing_period)

        count = 0
        for file in args:
          with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                    count = count + 1                    
                    name = row[0]
                    email = row[1]
                    amount = row[2]

                    try:
                        skater = Skater.objects.get(email__exact=email)
                    except Skater.DoesNotExist:
                        skater = False
                        self.stdout.write( str(count) + "\t==== NOT FOUND, NOT INVOICED: " + email)

                    if skater:

                        invoiced = False

                        "Check if we've already generated an invoice for this user"
                        try:
                            invoice = Invoice.objects.get(skater=skater, schedule=schedule)
                            invoiced = True
                        except Invoice.DoesNotExist:
                            pass

                        if invoiced:
                            self.stdout.write( str(count) + "\t~~~~ ALREADY INVOICED - " + email + " / " + skater.get_short_name() )
                        else:
                            generate_scheduled_invoice(skater, schedule, False, amount)
                            self.stdout.write( str(count) + "\tOK - " + skater.get_short_name() + "\t" + email + "\t" + str(amount))

                            sk = Skater.objects.get(id=skater.id)


                            html = render_to_string('emails/summer_invoice.html',
                                {
                                    'skater' : sk,
                                    'skater_short_name': sk.get_short_name(),
                                    'due_date' : due_date,
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
                

