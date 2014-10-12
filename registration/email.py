from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from mwd import settings

def send_registration_email(session, skater):

    if skater.balance != 0:
        intro = """
<br>        
You are almost done registering to skate. Once we receive your dues payment registration will be complete. <br>
<br>
Dues payment of $""" + str(skater.balance) + " must be paid by " + settings.REGISTRATION_DEADLINE + """<br>
<br>
<b>Here's how to pay:</b><br>
<br>
""" + settings.REGISTRATION_MAIL_INSTRUCTIONS + """<br>
<br>

"""
    else:
	intro = """
<br>
You are all done registering to skate!"""


    html = render_to_string('emails/registration.html', 
                {
                    'intro' : intro,
                    'skater' : skater,
                    'session' : session,
                    'skater_short_name': skater.get_short_name(),
                }
           )


    subject = "Mad Wreckin' Dolls " + session.name + " Registration [#" + str(skater.id) + "]"

    msg = EmailMultiAlternatives(
            subject,
            html,
            settings.FROM_EMAIL,
            [ skater.email ],
            [ settings.FROM_EMAIL ],
            headers = { 
                'Reply-To' : settings.FROM_EMAIL, 
                'CC' : settings.FROM_EMAIL,
            },
    )

    msg.content_subtype = "html"
    msg.send(fail_silently = False)
    



