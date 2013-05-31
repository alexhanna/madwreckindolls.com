from fpdf import FPDF

from django.core.management.base import BaseCommand, CommandError
from accounts.models import Skater, SkaterStatus, SkateSessionPaymentSchedule, Invoice, PaymentError
from mwd import settings
from time import gmtime, strftime

class Command(BaseCommand):
    help = "Generate a emergency medical info PDF"

    def handle(self, *args, **options):
    
        skaters = Skater.objects.exclude(status__name="inactive").order_by("derby_name")

        pdf=FPDF()
        pdf.add_font('DejaVu','','/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansCondensed.ttf',uni=True)
        
        for skater in skaters:
            
            pdf.add_page()
            pdf.set_margins(16, 2)
            pdf.ln(20)

            pdf.set_font('DejaVu','',16)
            pdf.cell(40,40,'Derby Name:')
            pdf.set_font('DejaVu','',48)
            pdf.cell(40,40, skater.derby_name)
            pdf.ln(20)

            pdf.set_font('DejaVu','',16)
            pdf.cell(40,40,'Real Name:')
            pdf.set_font('DejaVu','',24)
            pdf.cell(40,40, skater.first_name + " " + skater.last_name)
            pdf.ln(20)
            
            pdf.set_font('DejaVu','',16)
            pdf.cell(60,40,'Emergency Contact:')
            pdf.set_font('DejaVu','',24)
            pdf.cell(0,40, skater.emergency_contact)
            pdf.ln(10)
            pdf.cell(60,40,'')
            pdf.set_font('DejaVu','',24)
            pdf.cell(0,40, skater.emergency_phone)
            pdf.ln(10)
            pdf.cell(60,40,'')
            pdf.set_font('DejaVu','',24)
            pdf.cell(0,40, skater.emergency_relationship)
            pdf.ln(15)
            
            pdf.set_font('DejaVu','',16)
            pdf.cell(60,40,'Insurance Provider:')
            pdf.set_font('DejaVu','',24)
            pdf.cell(0,40, skater.insurance_provider)
            pdf.ln(15)
            
            pdf.set_font('DejaVu','',16)
            pdf.cell(60,40,'Hosptial Preference:')
            pdf.set_font('DejaVu','',24)
            pdf.cell(0,40, skater.hospital)
            pdf.ln(15)
            
            pdf.set_font('DejaVu','',12)
            pdf.multi_cell(0,40,'Medical Conditions:')
            pdf.ln(-15)
            pdf.set_font('DejaVu','',24)
            if skater.medical_details == "":
                details = "<none>"
            else:
                details = skater.medical_details
            
            pdf.write(12, details)
            pdf.ln(25)

            wftda = ""
            try:
                wftda = int(skater.wftda_number)
            except:
                pass

            pdf.set_font('Courier','',7)
            pdf.write(4, 'MWD #' + str(skater.id) + " | " + str(skater.email) + " | WFTDA #" + str(wftda) + " | generated on " + strftime("%Y-%m-%d", gmtime()))


        pdf.output('test.pdf','F')
