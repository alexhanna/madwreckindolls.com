from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from mwd import settings

def send_registration_email(session, skater):

    if skater.balance != 0:
        intro = """
<br>        
You are almost done registering to skate. Once we receive payment and a signed waiver, your registration will be complete. <b>If you don't have a printer, we'll have copies of the waiver form at the rink.</b><br>
<br>
Dues payment of $""" + str(skater.balance) + " must be paid by " + settings.REGISTRATION_DEADLINE + """<br>
<br>
<b>Here's how to pay:</b><br>
<br>
1. Find The Auditor (aka. Audi) in person and hand them cash, check, credit cards and sweaty hugs.<br>
<br>
2.  """ + settings.REGISTRATION_MAIL_INSTRUCTIONS + """<br>
<br>

"""
    else:
	intro = """
<br>
You are almost done registering to skate. Once we receive your signed waiver (attached!), your registration will be complete. <b>If you don't have a printer, we'll have copies of the waiver at the rink.</b>"""


    html = render_to_string('emails/registration.html', 
                {
                    'intro' : intro,
                    'skater' : skater,
                    'session' : session,
                    'skater_short_name': skater.get_short_name(),
                }
           )


    subject = "Mad Wreckin' Dolls " + session.name + " Registration - Action Required [#" + str(skater.id) + "]"

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

    msg.attach_file(settings.LEGAL_FILES_DIR + 'ReleaseandWaiverofLiability-01-01-2013.pdf')

    msg.content_subtype = "html"
    msg.send(fail_silently = False)
    



