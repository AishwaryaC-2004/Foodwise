from django.contrib import admin
from .models import NGO, NGORequirement
from .models import DonationMatch

admin.site.register(NGO)
admin.site.register(NGORequirement)
admin.site.register(DonationMatch)