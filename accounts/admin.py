from django.contrib import admin
from .models import CustomUser, VendorProfile, TravelerProfile, OTP

admin.site.register(CustomUser)
admin.site.register(VendorProfile)
admin.site.register(TravelerProfile)
admin.site.register(OTP)