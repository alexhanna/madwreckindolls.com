from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from mwd import settings

def send_registration_email(session, skater):

    intro = ""

    if skater.balance != 0:
        intro = """
<br>        
Your paperwork is now complete. Once we receive payment, your registration will be complete.<br>
<br>
Dues payment of $%s must be paid by %s<br>
<br>
Here's how to pay:<br>
<br>
1. With a credit card online: https://madwreckindolls.com/dues<br>
<br>
2. Find The Auditor or Trueblood in person and hand them cash, check, credit cards and sweaty hugs.<br>
<br>
3.  %s<br>
<br>

""" % (session.name, skater.balance, settings.REGISTRATION_DEADLINE, settings.REGISTRATION_MAIL_INSTRUCTIONS)

    html = render_to_string('emails/registration.html', 
                {
                    'intro' : intro,
                    'skater' : skater,
                    'session' : session,
                    'skater_short_name': skater.get_short_name(),
                }
           )


    msg = EmailMultiAlternatives(
            "Mad Wreckin' Dolls " + session.name + " Registration Confirmation",
            html,
            settings.FROM_EMAIL,
            [ skater.email ],
            [ settings.FROM_EMAIL ],
            headers = { 
                'Reply-To' : settings.FROM_EMAIL, 
                'CC' : settings.FROM_EMAIL,
                'Content-Type' : 'text/html' 
            },
    )

    msg.send(fail_silently = False)
    



