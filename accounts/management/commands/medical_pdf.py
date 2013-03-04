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
        
        for skater in skaters:
            
            pdf.add_page()
            pdf.ln(20)

            pdf.set_font('Arial','',16)
            pdf.cell(40,40,'Derby Name:')
            pdf.set_font('Arial','B',48)
            pdf.cell(40,40, skater.derby_name)
            pdf.ln(20)

            pdf.set_font('Arial','',16)
            pdf.cell(40,40,'Real Name:')
            pdf.set_font('Arial','B',24)
            pdf.cell(40,40, skater.first_name + " " + skater.last_name)
            pdf.ln(20)
            
            pdf.set_font('Arial','',16)
            pdf.cell(60,40,'Emergency Contact:')
            pdf.set_font('Arial','B',24)
            pdf.cell(0,40, skater.emergency_contact)
            pdf.ln(10)
            pdf.cell(60,40,'')
            pdf.set_font('Arial','B',24)
            pdf.cell(0,40, skater.emergency_phone)
            pdf.ln(10)
            pdf.cell(60,40,'')
            pdf.set_font('Arial','B',24)
            pdf.cell(0,40, skater.emergency_relationship)
            pdf.ln(25)
            
            pdf.set_font('Arial','',16)
            pdf.cell(60,40,'Insurance Provider:')
            pdf.set_font('Arial','B',24)
            pdf.cell(0,40, "insurance insurance provider blah") #skater.insurance_provider)
            pdf.ln(15)
            
            pdf.set_font('Arial','',16)
            pdf.cell(60,40,'Hosptial Preference:')
            pdf.set_font('Arial','B',24)
            pdf.cell(0,40, skater.hospital)
            pdf.ln(15)
            
            pdf.set_font('Arial','',16)
            pdf.multi_cell(0,40,'Medical Conditions:')
            pdf.set_font('Arial','B',16)
            pdf.ln(1)
            if skater.medical_details == "":
                details = "<none>"
            else:
                details = skater.medical_details
            details = """something about something yes okay sure whatever alright.

oh yeah.

that too."""
            pdf.write(4, details)
            pdf.ln(25)

            pdf.set_font('Courier','',7)
            pdf.write(4, 'MWD #' + str(skater.id) + " | " + skater.email + " | WFTDA #" + str(skater.wftda_number) + " | generated on " + strftime("%Y-%m-%d", gmtime()))


        pdf.output('test.pdf','F')
