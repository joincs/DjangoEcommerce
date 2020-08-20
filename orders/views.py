from django.shortcuts import render,redirect
from django.views.generic.edit import FormView
from .forms import AdressForm,UserAddressForm
from .models import UserAddress,UserCheckout, Order
from django.urls import reverse
from django.views.generic import CreateView,ListView,DetailView
from django.contrib import messages
from .mixins import CartOrderMixin,LoginRequiredMixin
from django.http import Http404
# Create your views here.



class OrderDetail(LoginRequiredMixin,DetailView):
    model = Order
    template_name = 'orders/order_detail.html'

    def dispatch(self,request,*args,**kwargs):
        try:
            user_check_id = self.request.session.get("user_checkout_id")
            user_checkout = UserCheckout.objects.get(id=user_check_id)
        except UserCheckout.DoesNotExist:
            user_checkout = UserCheckout.objects.get(user=request.user)
        except:
            user_checkout = None

       
        obj = self.get_object()
        if obj.user == user_checkout and user_checkout is not None:
            return super(OrderDetail,self).dispatch(request,*args,**kwargs)
        else:
            raise Http404
    



class OrderListView(LoginRequiredMixin,ListView):
    queryset = Order.objects.all()
    template_name = 'orders/order_list.html'

    def get_queryset(self):
        user_check_id = self.request.user.id
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        return super(OrderListView,self).get_queryset().filter(user=user_checkout)



class UserAddressCreateView(CreateView):
    form_class = UserAddressForm
    template_name = "orders/form.html"
    success_url = "/checkout/address/"

    def get_checkout_user(self):
        user_check_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        return user_checkout
    
    def form_valid(self,form,*args,**kwargs):
        form.instance.user = self.get_checkout_user()
        return super(UserAddressCreateView,self).form_valid(form,*args,**kwargs) 
    
    

class AddressSelectFormView(CartOrderMixin,FormView):
    form_class = AdressForm
    template_name = 'orders/address_select.html'
    success_url = "/checkout/"

    def dispatch(self,*args,**kwargs):
        b_address,s_address = self.get_address()

        if b_address.count() == 0:
            messages.success(self.request, "Please add a billing address before continuing")
            return redirect("user_address_create")
        elif s_address.count() == 0:
            messages.success(self.request, "Please also add a Shipping address before continuing")
            return redirect("user_address_create")
        else:
            return super(AddressSelectFormView,self).dispatch(*args,**kwargs)

    def get_address(self,*args,**kwargs):
        user_check_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_check_id)
        b_address = UserAddress.objects.filter(
            user = user_checkout,
            bill_type="billing"
        )
        s_address = UserAddress.objects.filter(
            user = user_checkout,
            bill_type="shipping"
        )
        
        return b_address,s_address

    

    def get_form(self,*args,**kwargs):
        form = super(AddressSelectFormView,self).get_form(*args,**kwargs)
        b_address,s_address = self.get_address()
        form.fields['billing_address'].queryset = b_address
        form.fields['shipping_address'].queryset = s_address
        return form
    

    def form_valid(self,form,*args,**kwargs):
        billing_address = form.cleaned_data.get("billing_address")
        shipping_address = form.cleaned_data.get("shipping_address")
        order = self.get_order()
        order.billing_address = billing_address
        order.shipping_address = shipping_address
        order.save()
        return super(AddressSelectFormView,self).form_valid(form,*args,**kwargs)
    
    
    

