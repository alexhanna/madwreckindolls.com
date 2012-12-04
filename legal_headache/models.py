from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.contrib import admin

# A binder of all the versions of a certain legal document
class LegalDocumentBinder(models.Model):
    document_name = models.CharField("Document", max_length=50)

    def __unicode__(self):
        return self.document_name

    # Returns the active version of the legal document
    def get_active_version(self):
        document = LegalDocument.objects.filter(document_group__exact = self.id).filter(active=True)
        if len(document) == 1:
            return document[0]

        if len(document) > 1:
            error = "WARNING: Multiple active versions of documents specified for " + self.document_name
        else:
            error = "WARNING: No active document for " + self.document_name

        document = LegalDocument()
        document.document_group = self
        document.text = error
        return document



# The actual legal document (version and text)
class LegalDocument(models.Model):
    document_group = models.ForeignKey(LegalDocumentBinder) 
    version = models.DateField("Document Version Date")
    text = models.TextField("Document Text")
    active = models.BooleanField("Active Version in Registration")

    def __unicode__(self):
        doc_name = self.document_group.document_name + ' - '
        if self.version:
            doc_name += str(self.version)
        if self.active:
            doc_name += " (ACTIVE)"
        return doc_name


# Tracks the "I agree" clicks of a user through different versions of a document
class LegalDocumentSignature(models.Model):
    document = models.ForeignKey(LegalDocument)
    user = models.ForeignKey(User)
    datestamp = models.DateTimeField(auto_now_add = True)


admin.site.register(LegalDocument)
admin.site.register(LegalDocumentBinder)
