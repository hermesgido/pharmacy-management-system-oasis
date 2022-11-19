from django.urls import path
from .import views


urlpatterns = [
    path('users/', views.users, name="users"),
    path('logout_user', views.logout_user, name="logout_user"),
    path('', views.home, name="home"),
    path('stock/', views.stock, name="stock"),
    path('sales/', views.sales, name="sales"),
    path('checkout_retail/', views.checkout_retail, name="checkout_retail"),
    path('checkout_wholesale/', views.checkout_wholesale, name="checkout_wholesale"),
    path('costomers/', views.costomers, name="costomers"),
    path('suppliers/', views.suppliers, name="suppliers"),
    path('medicines/', views.medicines, name="medicines"),
    path('edit_supplier/<str:id>/', views.edit_supplier, name="edit_supplier"),
    path('edit_costomer/<str:id>/', views.edit_costomer, name="edit_costomer"),
    path('settings/', views.settings, name="settings"),
    path('sale_medicine/', views.sale_medicine, name="sale_medicine"),
    path('stock_products/<str:id>/', views.stock_products, name="stock_products"),
    path('invoice/<str:id>/', views.invoice, name="invoice"),
    path('signin/', views.signin, name="sigin"),
    path('edit_medicine/<str:id>/', views.edit_medicine, name='edit_medicine'),
]
