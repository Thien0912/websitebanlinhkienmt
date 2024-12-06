from dataclasses import field
from email.policy import default
from enum import unique
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Category(models.Model):
    name= models.CharField(max_length= 250)
    create= models.DateTimeField(auto_now_add= True)
    update= models.DateTimeField(auto_now= True)
    slug = models.SlugField(max_length= 250, unique= True, null= False)

    def __str__(self):
        return f"{self.name}"

class Manufacturer(models.Model):
    name= models.CharField(max_length= 250)
    create= models.DateTimeField(auto_now_add= True)
    update= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    name= models.CharField(max_length= 250)
    detail= models.TextField(null= True, blank= True)
    price= models.IntegerField(null= False)
    quantity= models.IntegerField(null= True)
    image= models.ImageField(null= True, blank= True)
    category= models.ForeignKey(Category, on_delete= models.CASCADE, related_name= 'product')
    manufacturer= models.ForeignKey(Manufacturer, on_delete= models.CASCADE)
    create= models.DateTimeField(auto_now_add= True)
    update= models.DateTimeField(auto_now= True)
    
    def __str__(self):
        return f"{self.name}, {self.price}, {self.quantity}"
    @property
    def ImageURL(self):
        try:
            url= self.image.url
        except:
            url= ''
        return url
    
class Order(models.Model):
    customer= models.ForeignKey(User, on_delete= models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add = True)
    paid= models.BooleanField(default= False, null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.id}"
    
    @property
    def get_cart_items(self):
        orderdetails= self.orderdetail_set.all()
        total= sum([item.quantity for item in orderdetails])
        return total
    
    @property
    def get_cart_total(self):
        orderdetails= self.orderdetail_set.all()
        total= sum([item.get_total for item in orderdetails])
        return (total)
    
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default= 0, null= True, blank=True)
    
    @property
    def get_total(self):
        total= self.product.price * self.quantity
        return (total)
    
class CheckoutInfo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null= True, blank= True)
    name= models.CharField(max_length= 250)
    number= models.CharField(max_length= 10)
    city= models.CharField(max_length= 250)
    district= models.CharField(max_length= 250, null= True, blank= True)
    town= models.CharField(max_length= 250, null= True, blank= True)
    hamlet= models.CharField(max_length= 250, null= True, blank= True)
    bank= models.CharField(max_length= 250, null= True, blank= True)
    card_number= models.CharField(max_length= 250, null= True, blank= True)

    def __str__(self):
        return f"{self.name}"

    
class CheckoutInfoForm(forms.ModelForm):
    class Meta:
        model = CheckoutInfo
        fields = ['name', 'number', 'city',  'district', 'town', 'hamlet', 'bank', 'card_number']

class CreateUser(UserCreationForm):
    class Meta:
        model= User
        fields= ['username','email','first_name','last_name','password1','password2']