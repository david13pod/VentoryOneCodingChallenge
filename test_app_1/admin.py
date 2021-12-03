from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(SKU)
admin.site.register(Warehouse)
admin.site.register(Purchase_Order)
admin.site.register(Plain_Carton_Line_Item)
admin.site.register(Fba)