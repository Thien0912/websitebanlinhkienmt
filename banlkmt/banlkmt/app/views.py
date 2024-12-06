import imp
from itertools import product
from multiprocessing import context
from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import CheckoutInfoForm

# Create your views here.

def success(request):
    context = {}
    return render(request, 'app/success.html', context)

def detail(request):
    categories= Category.objects.all()
    active_category= request.GET.get('category','')
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
    else:
        user_not_login = "show"
        user_login = "hidden"
    id = request.GET.get('id', '')
    products = Product.objects.filter(id=id)
    if active_category:
        products= Product.objects.filter(category__slug = active_category)
    context={'categories':categories, 'active_category': active_category, 'products': products, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request,'app/detail.html',context)

def search(request):
    categories= Category.objects.all()
    active_category= request.GET.get('category','')
    if request.method == "POST":
        searched= request.POST["searched"]
        keys= Product.objects.filter(name__contains = searched)
    if request.user.is_authenticated:
        customer= request.user
        order, created= Order.objects.get_or_create(customer =customer, paid =False)
        items= order.orderdetail_set.all()
        user_not_login = "hidden"
        user_login = "show"
    else:
        order= {'get_cart_items': 0, 'get_cart_total': 0}
        items= []
        user_not_login = "show"
        user_login = "hidden"
    products= Product.objects.all()
    if active_category:
        products= Product.objects.filter(category__slug = active_category)
    return render(request,'app/search.html',{'categories':categories, 'active_category': active_category, 'searched': searched, 'keys': keys, 'products': products, 'items': items, 'user_not_login': user_not_login, 'user_login': user_login})

def category(request):
    categories= Category.objects.all()
    active_category= request.GET.get('category','')
    if request.user.is_authenticated:
        user_not_login = "hidden"
        user_login = "show"
    else:
        user_not_login = "show"
        user_login = "hidden"
    if active_category:
        products= Product.objects.filter(category__slug = active_category)
    context= {'categories':categories, 'active_category': active_category,  'products': products, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request,'app/category.html',context)

def register(request):
    form= CreateUser()
    if request.method == "POST":
        form = CreateUser(request.POST)
        if form.is_valid:
            form.save()
            return redirect('login')
    context= {'form':form}
    return render(request,'app/register.html',context)

def loginForm(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username= request.POST.get('username')
        password= request.POST.get('password')
        user= authenticate(request,username= username, password= password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Tài khoản hoặc mật khẩu không đúng')
    context= {}
    return render(request,'app/login.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        customer= request.user
        order, created= Order.objects.get_or_create(customer =customer, paid =False)
        items= order.orderdetail_set.all()
        user_not_login = "hidden"
        user_login = "show"
    else:
        order= {'get_cart_items': 0, 'get_cart_total': 0}
        items= []
        user_not_login = "show"
        user_login = "hidden"
    categories= Category.objects.all()
    products= Product.objects.all()
    context={'categories':categories, 'products': products, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request,'app/home.html',context)

def cart(request):
    categories= Category.objects.all()
    active_category= request.GET.get('category','')
    if request.user.is_authenticated:
        customer= request.user
        order, created= Order.objects.get_or_create(customer =customer, paid =False)
        items= order.orderdetail_set.all()
        user_not_login = "hidden"
        user_login = "show"
    else:
        order= {'get_cart_items': 0, 'get_cart_total': 0}
        items= []
        user_not_login = "show"
        user_login = "hidden"
    categories= Category.objects.all()
    context={'categories':categories, 'active_category': active_category, 'items':items, 'order':order, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request,'app/cart.html',context)

def checkout(request):
    categories= Category.objects.all()
    active_category= request.GET.get('category','')
    c_form = CheckoutInfoForm()

    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.filter(customer=customer, paid=False).first()
        if not order:
            order = Order.objects.create(customer=customer, paid=False)

        items = order.orderdetail_set.all()
        user_not_login = "hidden"
        user_login = "show"

        if request.method == 'POST':
            c_form = CheckoutInfoForm(request.POST)
            if c_form.is_valid():
                checkout_info = c_form.save(commit=False)
                checkout_info.order = order
                checkout_info.save()
                order.paid = True
                order.save()
                return redirect('success')

    else:
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        items = []
        user_not_login = "show"
        user_login = "hidden"

    categories = Category.objects.all()
    context = {'c_form': c_form, 'categories':categories, 'active_category': active_category, 'items': items, 'order': order, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/checkout.html', context)

def updateOrder(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id=productId)
    order, created= Order.objects.get_or_create(customer =customer, paid =False)
    orderDetail, created= OrderDetail.objects.get_or_create(order =order, product =product)
    if action == 'add':
        orderDetail.quantity += 1
    elif action == 'remove':
        orderDetail.quantity -= 1
    orderDetail.save()
    if orderDetail.quantity <= 0:
        orderDetail.delete()
    order.total = order.get_cart_total()
    order.save()
    return JsonResponse('added', safe= False)
