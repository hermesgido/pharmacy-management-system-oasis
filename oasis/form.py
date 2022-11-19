from django import forms
from .models import *
from django.forms import inlineformset_factory


class MainForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super(MainForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['col'] = '10'
            field.widget.attrs['rows'] = '10'

class Sale_ItemForm(MainForm):

    class Meta:
       
        model = Sale_Item
        fields = '__all__'
        exclude = ['sale', 'medicine', 'batch_no', 'is_checkouted']

class SaleForm(MainForm):

    class Meta:
       
        model = Sales
        fields = '__all__'
        exclude = ['sale_id', 'invoice_number','is_wholesale','complited','sold_by']
            
class MedicineForm(MainForm):
    quantity_instock = forms.CharField(widget=forms.TextInput(attrs={'min':1}))

    class Meta:
       
        model = Medicine
        fields = '__all__'
        exclude = ['medicine_id']

class StockForm(MainForm):
    class Meta:
       
        model = Stock
        fields = '__all__'
        exclude = ['stock_id']

class SupplierForm(MainForm):
    location = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 5}))
    class Meta:
       
        model = Supplier
        fields = '__all__'
        exclude = ['supplier_id']
class CostomerForm(MainForm):
    class Meta:
       
        model = Costomer
        fields = '__all__'
        exclude = ['costomer_id']
        
class UnitForm(MainForm):
    class Meta:
       
        model = Unit
        fields = '__all__'
        exclude = []

class PaymentMethodForm(MainForm):
    class Meta:
       
        model = PaymentMethod
        fields = '__all__'
        exclude = []
        
class StockProductForm(MainForm):
    class Meta:
       
        model = Stock_Product
        fields = '__all__'
        exclude = []

SaleFormSet = inlineformset_factory(
    Sales, Sale_Item, form=Sale_ItemForm,
    extra=1, can_delete=True, can_delete_extra=True
)