from django_filters import DateRangeFilter,NumberFilter, DateFilter
from .models import *
import django_filters 
from django import forms


class MedicineFilter(django_filters.FilterSet):
    medicine_name = django_filters.CharFilter(lookup_expr='icontains')
    quantity_instock = django_filters.NumberFilter(field_name='quantity_instock', lookup_expr='lt')
    class Meta:
        model = Medicine
        fields = ['medicine_id', 'medicine_name', 'quantity_instock']
        

class SalesFilter(django_filters.FilterSet):
    date = DateRangeFilter(field_name='sold_date', )
    start_date = DateFilter(field_name='sold_date', label='Start Date:',  lookup_expr='gte', widget=forms.DateInput(
            attrs={
                'id': 'datepicker',
                'type': 'date'
            }
        ))
    end_date = DateFilter(field_name='sold_date', label="End Date: ", lookup_expr='lte', widget=forms.DateInput(
            attrs={
                'id': 'datepicker',
                'type': 'date'
            }
        ))
    
    quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='lt')
    class Meta:
        model = Sales
        fields = ['costomer', 'sold_by']
