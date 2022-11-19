from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Stock)
admin.site.register(Stock_Product)
admin.site.register(Sales)
admin.site.register(Medicine)
admin.site.register(Sale_Item)
admin.site.register(Costomer)
admin.site.register(Supplier)
admin.site.register(Unit)
admin.site.register(PaymentMethod)
