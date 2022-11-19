from django.db import models
import pyotp
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from shortuuid.django_fields import ShortUUIDField
from datetime import datetime

today = datetime.today()

year = today.year
month = today.month
day = today.day


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, phone, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not phone:
            raise ValueError(_('The Phone Number must be set'))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    username = None
    full_name = models.CharField(
        ("Full Name"), max_length=250, blank=True, null=True)
    phone = PhoneNumberField(
        _('Phone Number'), blank=True, region="TZ", unique=True)
    email = models.EmailField(
        _('Email Address'), unique=True, blank=True, null=True)
    is_cashier = models.BooleanField(_("Cashier"), default=False)
    is_verified = models.BooleanField(_("Verified"), default=False)
    key = models.CharField(max_length=200, blank=True,
                           null=True, default=pyotp.random_base32())

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    @property
    def user_key():
        key = pyotp.random_base32()
        return key

    objects = CustomUserManager()

    def __str__(self):
        return str(self.phone)


# Create your models here.


class Phamacy(models.Model):
    phamacy_id = ShortUUIDField(
        length=4,
        max_length=4,
        alphabet="1234567490",
        unique=True,
        primary_key=True

    )
    name = models.CharField(("Supplier Name"), null=True,
                            blank=True, max_length=200)
    phone = PhoneNumberField(('Phone Number'), blank=True, region="TZ")
    location = models.TextField(("Location"), blank=True)
    tin_number = models.CharField(
        ("TIN NUMBER"), null=True, blank=True, max_length=200)

    class Meta:

        def __str__(self):
            return self.name


class Stock(models.Model):
    added_by = models.ForeignKey('User', null=True,   on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=250, blank=True, null=True)
    supplier = models.ForeignKey(
        "Supplier", null=True,  on_delete=models.CASCADE)
    invoice_number = models.CharField(
        ("Invoice Number"), max_length=250, blank=True, null=True)
    payment_mode = models.ForeignKey(
        ("PaymentMethod"), null=True,  on_delete=models.CASCADE)
    entry_date = models.DateField(("Entry Date"), auto_now=True)
    stock_id = ShortUUIDField(
        length=4,
        max_length=5,
        alphabet="1234567490",
        primary_key=True,
        unique=True,
    )

    class Meta:
        verbose_name = ("Stock")
        verbose_name_plural = ("Stocks")

    def __str__(self):
        return self.stock_name

    @property
    def get_total_price(self):
        total = 0
        products = self.stock_product_set.all()
        for product in products:
            total = total + product.get_amount
        return total


class Medicine(models.Model):
    medicine_id = ShortUUIDField(
        length=5,
        max_length=5,
        alphabet="1234567490",
        primary_key=True,
        unique=True,
    )
    medicine_name = models.CharField(max_length=250, blank=True, null=True)
    retail_price = models.IntegerField(("Retail Price"), default=0)
    wholesale_price = models.IntegerField(("Wholesale Price"), default=0)
    buying_price = models.IntegerField(("Price"),  null=True,  default=0)
    quantity_instock = models.IntegerField(
        ("Quantity In Stock"), null=True, blank=True, default=0)

    @property
    def is_out_of_stock(self):
        if self.quantity_instock < 3:
            return True

    class Meta:
        verbose_name = ("Medicine")
        verbose_name_plural = ("Medicine")

    def __str__(self):
        return self.medicine_name


class Stock_Product(models.Model):
    stock = models.ForeignKey("Stock", null=True,  on_delete=models.CASCADE)
    medicine = models.ForeignKey(
        "Medicine", null=True,  on_delete=models.CASCADE)
    unit = models.ForeignKey(
        "Unit", null=True, blank=True,  on_delete=models.CASCADE)
    quantity = models.IntegerField(("Quantity"), default=0)
    buying_price = models.IntegerField(("Buying Price"), default=0)
    manufacture_date = models.DateField(("Manufacture Date"))
    expire_date = models.DateField(("Expire Date"))
    entry_date = models.DateField(("Entry Date"), auto_now=True)
    batch_no = models.CharField(
        ("Batch Number"), max_length=250, blank=True, null=True)
    quantity_sold = models.IntegerField(("Quantity Sold"), default=0)

    @property
    def about_to_expire(self):
        if self.expire_date.month == month and self.expire_date.year == year:
            return True

    @property
    def is_out_of_stock(self):
        if self.quantity_sold == self.quantity:
            return True

    @property
    def in_stock_now(self):
        amt = self.quantity - self.quantity_sold
        return amt

    @property
    def get_amount(self):
        amount = self.quantity * self.buying_price
        return amount

    class Meta:
        verbose_name = ("Stock Product")
        verbose_name_plural = ("Stock Product")

    def __str__(self):
        return self.medicine.medicine_name


class Sales(models.Model):
    sold_by = models.ForeignKey('User', null=True,  on_delete=models.CASCADE)
    sold_date = models.DateField(("Sold Date"), auto_now=True)
    costomer = models.ForeignKey('Costomer',   on_delete=models.CASCADE)
    complited = models.BooleanField(default=False)
    is_wholesale = models.BooleanField(default=False)
    sale_id = ShortUUIDField(
        length=4,
        max_length=4,
        alphabet="1234567490",
        unique=True,
        primary_key=True
    )
    invoice_number = ShortUUIDField(
        length=6,
        max_length=6,
        alphabet="1234567490",

    )

    @property
    def get_total_money(self):
        items = self.sale_item_set.all()
        if self.is_wholesale == False:
            for item in items:
                amt = sum(item.get_retail for item in items)
                return amt
        for item in items:
            amt = sum(item.get_wholesale for item in items)
            return amt


class Sale_Item(models.Model):
    sale = models.ForeignKey(
        'Sales', null=True, blank=True,   on_delete=models.CASCADE)
    medicine_stock = models.ForeignKey(
        'Stock_Product', null=True,  on_delete=models.CASCADE)
    quantity = models.IntegerField(("Quantity"))
    sold_date = models.DateField(("Sold Date"), auto_now=True)
    batch_no = models.CharField(
        ("Batch Number"), null=True, blank=True, max_length=200)
    is_checkouted = models.BooleanField(default=False)

    @property
    def get_wholesale(self):
        dt = int(self.quantity * self.medicine_stock.medicine.wholesale_price)
        return self.quantity * self.medicine_stock.medicine.wholesale_price

    @property
    def get_retail(self):
        dt = int(self.quantity * self.medicine_stock.medicine.retail_price)
        return self.quantity * self.medicine_stock.medicine.retail_price


class Cart(models.Model):
    medicine = models.ForeignKey('Medicine',   on_delete=models.CASCADE)


class Supplier(models.Model):
    name = models.CharField(("Supplier Name"), null=True,
                            blank=True, max_length=200)
    phone = PhoneNumberField(('Phone Number'), blank=True, region="TZ")
    location = models.TextField(("Location"), blank=True)
    supplier_id = ShortUUIDField(
        length=4,
        max_length=4,
        alphabet="1234567490",
        unique=True,
        primary_key=True

    )
    created_date = models.DateField(_("Created date"), auto_now=True,)

    def __str__(self):
        return self.name


class Costomer(models.Model):
    name = models.CharField(("Costomer Name"), null=True,
                            blank=True, max_length=200)
    phone = PhoneNumberField(('Phone Number'), blank=True, region="TZ")
    location = models.TextField(("Location"), blank=True)
    created_date = models.DateField(_("Created date"), auto_now=True,)

    costomer_id = ShortUUIDField(
        length=4,
        max_length=4,
        alphabet="1234567490",
        unique=True,
        primary_key=True

    )

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(("Account Name"), null=True,
                            blank=True, max_length=200)
    type_of = models.CharField(("Type"), null=True, blank=True, max_length=200)
    account_no = models.CharField(
        ("Account Number"), null=True, blank=True, max_length=200)
    created_date = models.DateField(_("Created date"), auto_now=True,)

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(("Unit Name"), null=True,
                            blank=True, max_length=200)

    def __str__(self):
        return self.name
