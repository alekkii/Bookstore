from django.conf.urls import url 
from . import views 

app_name = 'store'

urlpatterns =[
    url(r'^$', views.store, name='store'),

    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/', views.logout_user, name='logout_user'),

    url(r'^book/(\d+)',   views.book_details, name='detail'),
    url(r'^add/(\d+)',    views.add_to_cart, name='add_to_cart'),
    url(r'^remove/(\d+)', views.remove_from_cart, name='remove_from_cart'),
    url(r'^cart/$',       views.cart, name='cart'),
    
    url(r'^checkout/(\w+)', views.checkout, name='checkout'),
    url(r'^process/(\w+)', views.process_order, name='process_order'),
    url(r'^order_error/', views.order_error, name='order_error'),
    url(r'^complete_order/(\w+)', views.complete_order, name='complete_order'),
    #url(r'^store/', views.store , name='store'),
    
    #url(r'^book/(\d+)',views.book_details, name='book_details'),
    #url(r'^$', views.home, name = 'home'),
]
#url(r'^store/', views.store , name='store'),
