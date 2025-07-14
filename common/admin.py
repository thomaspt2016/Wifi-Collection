from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Building)
admin.site.register(InternetPlan)
admin.site.register(WifiCodeUpload)
admin.site.register(CodePoool)
admin.site.register(Billgeneration)
admin.site.register(Payment)
admin.site.register(Ticket)
admin.site.register(Profile)

# Register your models here.
