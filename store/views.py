from django.shortcuts import render,redirect,reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Book ,Cart,BookOrder,Author,Review
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout,login
from .forms import  UserForm
# from . import urls
from django.db.models import Q
#from django.core.urlresolvers import reverse
from django.utils import timezone
import paypalrestsdk
# Create your views here.

def index(request):
    return render(request,'template.html')

def store(request):
    books = Book.objects.all()
    context = {'books': books,}
    assert isinstance(request, object)
    return render(request,'base.html',context)  

def book_details(request, book_id):
    context ={'book':Book.objects.get(pk=book_id),}
        
    return render(request,'store/detail.html', context)

#def home(request):
    #return render(request,'home.html')

def add_to_cart(request, book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                cart = Cart.objects.get(user=request.user, active=True)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(
                    user = request.user
                )
                cart.save()
                cart.add_to_cart(book_id)
        return render(request, 'store/cart.html')
    else:
        return redirect('index')

def remove_from_cart(request, book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            cart = Cart.objects.get(user=request.user, active=True)
            cart.remove_from_cart(book_id)
        return render(request, 'store/cart.html')
    else:
        return redirect('index')

def cart(request):
    if request.user.is_authenticated():
        cart = Cart.objects.filter(user=request.user.id, active=True)
        orders= BookOrder.objects.filter(cart=cart)
        total = 0
        count = 0
        for order in orders:
            assert isinstance(order, object)
            total += (order.book.price * order.quantity)
            count += order.quantity
        context={
            'cart':orders,
            'total':total,
            'count':count
        }
        return render(request, 'store/cart.html', context)
    else:
        return render ('store/cart.html')




def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'store/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                book = Book.objects.filter(user=request.user)
                return render(request, 'store/detail.html', {'book': book})
            else:
                return render(request, 'store/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'store/login.html', {'error_message': 'Invalid login'})
    return render(request, 'store/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                book = Book.objects.filter(user=request.user)
                return render(request, 'store/cart.html')
    context = {
        "form": form,
    }
    return render(request, 'store/register.html', context)



#paypal view inteagration
def checkout(request, processor):
    if request.user.is_authenticated():
        cart = Cart.objects.filter(user=request.user.id,active=True)
        orders = BookOrder.objects.filter(cart=cart)
        if processor == "paypal":
            redirect_url = checkout_paypal(cart,orders)
            return redirect(redirect_url)
        else:
            return redirect('store:index')#########check for error during running

def checkout_paypal(request,cart, orders):
    if request.user.is_authenticated():
        items = []
        total = 0
        for order in orders:
            total += (order.book.price + order.quantity)
            book = order.book_id
            item ={
                'name': book.title,
                'sku': book.id,
                'price': str(book.price),
                'currency': 'USD',
                'quantity': order.quantity
            }
            items.append(item)
        paypalrestsdk.configure({
            "mode":"sandbox",
            "client_id": "AR61TBPPjrw3fufvlHKp8iPaMG4MkpkMkcsUT0ZV42ke3nojymEVzK93KnO4YI4g5K75zJy7po8a1Jo3",
            "client_secret":"EBPhLb3suPxQc6YZCPdptFP0t0t0NYvHRx8RbBkWxV44kuon2LuMo7peeMzjfJapWSB4rIkIAF0kWL7t",
            })
        payment = paypalrestsdk.Payment({
        
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://127.0.0.1:8000/store/process/paypal",
                "cancel_url": "http://127.0.0.1:8000/store"},
            "transactions": ({
                "items_list":{
                    "items": items},
                "amount":{
                    "total": str(total),
                    "currency": "USD"},
                "description": "Mystery Books order,"})})
        if payment.create():        
            cart_instance = cart.get()
            cart_instance.payment_id = payment_id
            cart_instance.save()
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_urls = str(link.href)
                    return redirect_urls
            else:
                return reverse('order_error')
        else:
            return redirect('index')

def order_error(request):
    if request.user.is_authenticated():
        return render(request, 'store/order_error.html')
    else:
        return redirect('index')

def process_order(request, processor):
    if request.user.is_authenticated():
        if processor == "paypal":
            payment_id = request.GET.get('paymentId')
            cart = Cart.objects.filter(cart=cart)
            orders = BookOrder.objects.filter(cart=cart)
            total = 0
            for order in orders:
                total += (order.book.price + order.quantity)
                context={
                'cart': orders,
                'total': total,
            }
            return render(request, 'store/process_order.html', context)
#else:
    #return redirect('index')


def complete_order(request, processor):
    if request.user.is_authenticated():
        cart = Cart.objects.get(user=request.user.id, active=True)
        if processor == 'paypal':
            payment = paypalrestsdk.Payment.find(cart.payment_id)
            if payment.execute({"payer_id": payment.payer_info.payer_id}):
                message = "Success! Your order has been completed, and is being processed. Payment ID: %s" %(payment_id)
                cart.active = False
                cart.order_date = timezone.now()
                cart.save()
            else:
                message = "Thare was aproblem with the transaction. Error: %s " %(payment.error.message)

                context = {
                'message': message,
            }
            return render(request, 'store/order_complete.html', context)
#else:
    #return redirect('index')