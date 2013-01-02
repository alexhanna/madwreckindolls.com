from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from mwd import settings

def send_receipt_email(receipt):

    html = render_to_string('emails/receipt.html',
                {
                    'skater' : receipt.skater,
                    'receipt' : receipt,
                    'skater_full_name': receipt.skater.get_full_name(),
                }
           )


    msg = EmailMultiAlternatives(
            "Mad Wreckin' Dolls Payment Receipt #" + str(receipt.id),
            html,
            settings.FROM_EMAIL,
            [ receipt.skater.email ],
            [ settings.FROM_EMAIL ],
            headers = { 
                'Reply-To' : settings.FROM_EMAIL,
                'CC' : settings.FROM_EMAIL,
                'Content-Type' : 'text/html' 
            },
    )

    msg.content_subtype = "html"
    msg.send(fail_silently = False)

