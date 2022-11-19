import math
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import *
from .filters import *
import csv
import tablib
import pandas as pd
import datetime as dt
import os
from .form import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from phonenumber_field.phonenumber import PhoneNumber
from datetime import datetime
from django.db.models import Q
# Create your views here.
from datetime import datetime

today = datetime.today()

year = today.year
month = today.month
day = today.day


 
@login_required
def home(request):
    medicine_list = Stock_Product.objects.all()
    cart_items = Sale_Item.objects.filter(is_checkouted = False).count()
    
    #about to expire
    medicines = Medicine.objects.all()
    medicine_count = Medicine.objects.all().count()
    
    expire_medicines  = Stock_Product.objects.all()
    out_of_stock = Medicine.objects.filter(quantity_instock__lte = 2).count()
    print(medicines)
    
    try:
        #today sales
        today_sales = Sales.objects.filter(sold_date__day=day)
        today_sales_amt = sum(sale.get_total_money for sale in today_sales)
        
        #this month sales
        this_month_sales = Sales.objects.filter(sold_date__month=month)
        this_month_sales_amt = sum(sale.get_total_money for sale in this_month_sales)
        
        #this year sales
        this_year_sales = Sales.objects.filter(sold_date__year=year)
        this_year_sales_amt = sum(sale.get_total_money for sale in this_year_sales)
    except:
        today_sales_amt = 0
        this_month_sales_amt = 0
        this_year_sales_amt = 0
    
    if request.method == "POST":
        obj = request.POST['obj']
        md= Medicine.objects.get(medicine_id=obj)
        print(obj)
        cart_obj = Cart.objects.create(medicine=md)
        cart_obj.save()
        url = 'sale_medicine/'+ str(cart_obj.id)
        return redirect(url)
    context = {
        "medicine_list":medicine_list, "cart_items":cart_items, 'today_sales_amt':today_sales_amt,
        "this_month_sales_amt":this_month_sales_amt, "this_year_sales_amt":this_year_sales_amt,
        'out_of_stock':out_of_stock, 'medicines':medicines, "expire_medicines":expire_medicines, 
        'medicine_count':medicine_count
    }
    return render(request, "home.html", context)

def signin(request):
    #user = User.objects.create(phone="+255747151890")
    #user.set_password("1926")
    #user.save()
    
    if request.method == "POST":
        password = request.POST['password']
        username = request.POST['phone']
        try:
           phone_number = PhoneNumber.from_string(username, region="TZ")
        except:
            phone_number = ' '
            messages.error(request, "Number Ya Simu Sio sahihi")
            return redirect(signin)
            print(phone, password)
        
           
           
        #role = request.POST['options']
        
        user = authenticate(phone=phone_number, password=password)
        if user is not None:
            login(request, user)
            return redirect(home)
        else:
            messages.error(request, "Wrong Details")
            return redirect(signin)
    context = {
        
    }
    return render(request, "login.html", context)

@login_required
def sales(request):
    filter = SalesFilter(request.GET, queryset=Sales.objects.all())
    if request.method == "GET" or None:
        filter = SalesFilter(request.GET, queryset=Sales.objects.all())
        sales_list = filter.qs
    else:
        sales_list  = Sales.objects.all()

    
    context = {
        'sales_list':sales_list, 'filter':filter
    }
    return render(request, "sales.html", context)


@login_required
def stock(request):
    if request.user.is_superuser == False:
        return redirect(home)
    stock_list = Stock.objects.all()
    form = StockForm()

    ##add new stock
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.added_by = request.user
            data.save()
            return redirect(stock)



    context = {
        'stock_list': stock_list, 'form':form
    }
    return render(request, "stock.html", context)

@login_required
def stock_products(request, id):
    if request.user.is_superuser == False:
        return redirect(home)
    stock_id = Stock.objects.get(stock_id=id)
    stock_products = Stock_Product.objects.filter(stock=stock_id)
    try:
        if request.method == "POST" and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            excel_file = uploaded_file_url
            empexceldata = pd.read_csv("."+excel_file,  engine ='python')
            dbframe = empexceldata
            for dbframe in dbframe.itertuples():
             
                    medicine_id = math.trunc(dbframe.medicine_id)
                    print(medicine_id)
                    
                    medicine = Medicine.objects.get(medicine_id=medicine_id)
                    print(medicine)
                  
                    quantity = dbframe.quantity
                    buying_price = dbframe.buying_price
                    batch_no = dbframe.batch_no
                    manufacture_date = dbframe.manufacture_date
                    expire_date = dbframe.expire_date
                    d = datetime.strptime(str(manufacture_date), '%d/%m/%Y')
                    manufacture_date =  d.strftime('%Y-%m-%d')
                  
                    d = datetime.strptime(str(expire_date), '%d/%m/%Y')
                    expire_date =  d.strftime('%Y-%m-%d')
                  
                    
                                             
                    
                    obj = Stock_Product.objects.create(
                    medicine=medicine,  stock=stock_id,  quantity=quantity, manufacture_date=manufacture_date,
                    expire_date=expire_date, buying_price=buying_price, batch_no=batch_no
                    )
                    obj.save()  
                    # udate stock amount
                    medicine.quantity_instock = int(medicine.quantity_instock) + int(quantity)
                    medicine.buying_price = buying_price
                    medicine.save()
    
    
    except Exception as identifier: 
        print(identifier)
        messages.error(request, "Error Occured:" + str(identifier))    
    context = {
        'stock': stock_id, 'stock_products':stock_products
    }

    return render(request, "stock_product.html", context)

@login_required
def sale_medicine(request):
    formset = SaleFormSet()
    form = SaleForm()
    if request.method == "POST":
         formset = SaleFormSet(request.POST or None, prefix='images')
         form = SaleForm(request.POST)
         if form.is_valid() and formset.is_valid():
            data = form.save(commit=False)
            data.save()
            for fm in formset:
                 dt = fm.save(commit=False)
                 dt.sale = data
                 dt.save()
            return redirect(sales)
    
    context = {
        'form':form, 'formset':formset
    }
    return render(request, "sale_medicine.html", context)

@login_required
def checkout_retail(request):
    items = Sale_Item.objects.filter(is_checkouted=False)
    sale_form = SaleForm()
    products = Stock_Product.objects.all()
    if request.method == "POST" and 'add' in request.POST:
        med_id = request.POST['med_id']
        quantity = request.POST['quantity']
        obj = Stock_Product.objects.get(id=med_id)
        med_quantity = obj.in_stock_now
        if int(quantity) > int(med_quantity):
            messages.error(request, "Only " + str(med_quantity) + " Units Available")
            return redirect(checkout_retail)
        obj = Stock_Product.objects.get(id=med_id)
        sale_item = Sale_Item.objects.create(
            medicine_stock=obj, quantity=quantity
        )
        sale_item.save()
        obj.quantity_sold = int(obj.quantity_sold) + int(quantity)
        obj.save()
        medx = obj.medicine
        medx.quantity_instock = (int(obj.medicine.quantity_instock) - int(quantity))
        medx.save()
        return redirect(checkout_retail)
    if request.method == "POST" and 'delete' in request.POST:
        
        id =  request.POST['id']
        item = Sale_Item.objects.get(id=id)
        item.delete()
        messages.info(request, "Deleted Sucessfull")
        return redirect(checkout_wholesale)
        
    #assign costomer 
    if request.method == "POST" and 'confirm' in request.POST:
            
        costomer = Costomer.objects.get(costomer_id=1111)
        sale, created = Sales.objects.get_or_create(complited=False, costomer=costomer, is_wholesale=False)
        if created:
            sale.sold_by = request.user
            sale.save()
            print("created")
        for item in Sale_Item.objects.filter(is_checkouted=False):
                item.sale =  sale
                item.save()
        sale = Sales.objects.filter(complited=False, is_wholesale=False)[0]
        items = sale.sale_item_set.all()
        for item in items:
            item.is_checkouted = True
            
            
            item.save()
        sale.complited = True
        sale.save()
        return redirect(sales)

    context = {
        'items': items, 'products':products, "sale_form":sale_form
    }
    return render(request, "checkout_retail.html", context)

@login_required
def checkout_wholesale(request):
    items = Sale_Item.objects.filter(is_checkouted=False)
    sale_form = SaleForm()
    products = Stock_Product.objects.all()
    if request.method == "POST" and 'add' in request.POST:
        med_id = request.POST['med_id']
        quantity = request.POST['quantity']
        obj = Stock_Product.objects.get(id=med_id)
        med_quantity = obj.in_stock_now
        if int(quantity) > int(med_quantity):
            messages.error(request, "Only " + str(med_quantity) + " Units Available")
            return redirect(checkout_wholesale)
        obj = Stock_Product.objects.get(id=med_id)
        sale_item = Sale_Item.objects.create(
            medicine_stock=obj, quantity=quantity
        )
        sale_item.save()
        obj.quantity_sold = int(obj.quantity_sold) + int(quantity)
        obj.save()
        medx = obj.medicine
        medx.quantity_instock = (int(obj.medicine.quantity_instock) - int(quantity))
        medx.save()
        return redirect(checkout_wholesale)
    if request.method == "POST" and 'delete' in request.POST:
        
        id =  request.POST['id']
        item = Sale_Item.objects.get(id=id)
        item.delete()
        messages.info(request, "Deleted Sucessfull")
        return redirect(checkout_wholesale)
        
    #assign costomer 
    if request.method == "POST" and 'costomerx' in request.POST:
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            
            data = sale_form.cleaned_data['costomer']
            sale, created = Sales.objects.get_or_create(complited=False, costomer=data, is_wholesale=True)
            if created:
                sale.sold_by = request.user
                sale.save()
            for item in Sale_Item.objects.filter(is_checkouted=False):
                item.sale =  sale
                item.save()
                
            
        
    
    if request.method == "POST" and 'confirm' in request.POST:
        try:
           sale = Sales.objects.filter(complited=False)[0]
        except:
            messages.error(request, "Please Confirm SALE to continue")
            return redirect(checkout_wholesale)
        items = sale.sale_item_set.all()
        for item in items:
            item.is_checkouted = True
            item.save()
        sale.complited = True
        sale.save()
        return redirect(sales)

    context = {
        'items': items, 'products':products, "sale_form":sale_form
    }
    return render(request, "checkout.html", context)



@login_required
def invoice(request, id):
    medicines= Medicine.objects.all() 
 
    sale = Sales.objects.get(sale_id=id)
    
    
    context = {
       "sale":sale 
    }
    return render(request, "invoice.html", context)
@login_required
def medicines(request):
    form = MedicineForm()
    filter = MedicineFilter(request.GET, queryset=Medicine.objects.all())

    if request.method == "GET":
       filter = MedicineFilter(request.GET, queryset=Medicine.objects.all())
       medicine_list = filter.qs
    else:
       medicine_list = Medicine.objects.all()
       ##add medicne
    
    if request.method == "POST" and 'addmedicine' in request.POST:
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(medicines)
        
        
    if request.method == "POST" and 'delete_medicine' in request.POST:
        medicine_id = request.POST['medicineid']
        obj = Medicine.objects.get(medicine_id=medicine_id)
        obj.delete()
        return redirect(medicines)
   
    
    try:
        if request.method == "POST" and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            excel_file = uploaded_file_url
            print(excel_file)
            empexceldata = pd.read_csv("."+excel_file,  engine ='python', keep_default_na=True)
            print(type(empexceldata))
            dbframe = empexceldata
            for dbframe in dbframe.itertuples():
             
                    medicine_name = dbframe.medicine_name
                    quantity_instock = dbframe.quantity_instock
                    buying_price = dbframe.buying_price
                    wholesale_price = dbframe.wholesale_price
                    retail_price = dbframe.retail_price
                    

                    obj = Medicine.objects.create(
                    medicine_name=medicine_name,  quantity_instock=quantity_instock,
                    buying_price=buying_price, wholesale_price=wholesale_price,retail_price=retail_price
                    )
    
                    print(obj)
                    obj.save()
            return redirect(medicines)  
    
    
    except Exception as identifier: 
        print(identifier)
        messages.error(request, "Error Occured:" + str(identifier)) 
    
    
    
    
    context = {
       "medicine_list":medicine_list , 'form':form, 'filter':filter
    }
    return render(request, "medicines.html", context)

@login_required
def edit_medicine(request, id):
    if request.user.is_superuser == False:
        return redirect(home)
    medicine = Medicine.objects.get(medicine_id=id)
    form = MedicineForm(instance=medicine)
    
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect(medicines)
        
        
    context = {
      'form':form, "tname": "Medicine"
    }
    return render(request, "edit.html", context)

@login_required   
def users(request):
    if request.user.is_superuser == False:
        return redirect(home)
    users_list = User.objects.all()
           ##delete user
    if request.method == "POST" and 'deletebtn' in request.POST: 
            user_id = request.POST['user_id']
            print(user_id)
            user = User.objects.get(phone=user_id)
            user.delete()
            return redirect(users)
        
    if request.method == "POST" and 'adduser' in request.POST:
        password = request.POST['password']
        username = request.POST['phone']
        role = int(request.POST['role'])
        full_name = request.POST['full_name']
        try:
           phone_number = PhoneNumber.from_string(username, region="TZ")
        except:
            phone_number = ' '
            messages.error(request, "Number Ya Simu Sio sahihi")
            return redirect(users)
        if User.objects.filter(phone=phone_number).exists():
            messages.error(request, "User Already Exist")
            return redirect(users)
        if role ==  1:
           user = User.objects.create(phone=phone_number , password = password, full_name=full_name, is_superuser=True)
        if role == 2:
            user = User.objects.create(phone=phone_number,password = password,  full_name=full_name, is_cashier=True)
        else:
            messages.error(request, "Select Role Of The User")
            return redirect(users)
        
 
    context = {
        'users_list':users_list
        }
    return render(request, "users.html", context)

@login_required
def suppliers(request):
    if request.user.is_superuser == False:
        return redirect(home)
    suppliers_list = Supplier.objects.all()
    form  = SupplierForm()
    if request.method == "POST" and 'add'in request.POST:
        form = SupplierForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect(suppliers)
        form = SupplierForm()
       
    if request.method == "POST" and 'delete'in request.POST:
        id= request.POST['id']
        obj= Supplier.objects.get(supplier_id=id)
        obj.delete()
        return redirect(suppliers)
     
    
    
    context = {
        'suppliers_list':suppliers_list, "form" : form       }
    return render(request, "suppliers.html", context)


@login_required
def edit_supplier(request, id):
    if request.user.is_superuser == False:
        return redirect(home)
    obj= Supplier.objects.get(supplier_id=id)
    form = SupplierForm(instance=obj)
    if request.method == "POST":
        obj= Supplier.objects.get(supplier_id=id)
        form = SupplierForm(request.POST, instance=obj)
        if form.is_valid():
                obj.save()
                return redirect(suppliers)
        
    
    context = {
                "form" : form , "tname": "Supplier"
                }
    return render(request, "edit.html", context)
    


@login_required
def costomers(request):
    costomer_list = Costomer.objects.all()
    form  = CostomerForm()
    if request.method == "POST" and 'add'in request.POST:
        form = CostomerForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect(costomers)
        form = CostomerForm()
       
    if request.method == "POST" and 'delete'in request.POST:
        id= request.POST['id']
        obj= Costomer.objects.get(supplier_id=id)
        obj.delete()
        return redirect(costomers)
     
    
    
    context = {
        'costomer_list':costomer_list, "form" : form       }
    return render(request, "costomers.html", context)

@login_required
def edit_costomer(request, id):
    obj= Costomer.objects.get(supplier_id=id)
    form = CostomerForm(request.POST, instance=obj)
    if form.is_valid():
            obj.save()
            return redirect(costomers)
        
    
    context = {
                "form" : form , "tname": "Costomer"
                }
    return render(request, "edit.html", context)

@login_required
def settings(request):
    if request.user.is_superuser == False:
        return redirect(home)
    context = {
                "form" : form , "tname": "Costomer"
                }
    return render(request, "settings.html", context) 

def logout_user(request):
    logout(request)
    return redirect(home)