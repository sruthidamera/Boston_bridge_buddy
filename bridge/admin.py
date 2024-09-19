from django.contrib import admin
from bridge.models import Event, Violation, Discount

# Register your models here.

admin.site.register(Event)
admin.site.register(Violation)
admin.site.register(Discount)
