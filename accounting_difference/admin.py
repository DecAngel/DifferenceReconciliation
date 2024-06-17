from django.contrib import admin

from .models import (
    Difference, Subject, SDRelationship, Document, DocumentEntry, DocumentDifference
)

# Register your models here.
for m in [
    Difference, Subject, SDRelationship, Document, DocumentEntry, DocumentDifference
]:
    admin.site.register(m)
