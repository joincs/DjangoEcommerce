import braintree
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import View,DetailView
from django.http import HttpResponseRedirect,Http404, JsonResponse
from product.models import Vairation
from .models import CartItem,Cart
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from orders.models import UserCheckout,Order,UserAddress
from orders.forms import GuestCheckoutForm
from django.views.generic.edit import FormMixin
from orders.mixins import CartOrderMixin
from django.contrib import messages
from django.conf import settings
 
 
# Create your views here.
import braintree

if settings.DEBUG:
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            environment=braintree.Environment.Sandbox,
            merchant_id=settings.BRAINTREE_MERCHANT_ID,
            public_key=settings.BRAINTREE_PUBLIC,
            private_key=settings.BRAINTREE_PRIVATE
        )
    )




class ItemCountView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get("cart_id")
            if cart_id == None:
                count = 0
            else:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()

            request.session["cart_item_count"]:count
            return JsonResponse({"count": count})
        else:
            raise Http404



class CartView(SingleObjectMixin,View):
    model = Cart
    template_name = 'cart/view.html'
    def get_object(self,*args,**kwargs):
        self.request.session.set_expiry(0) #5minutes
        cart_id = self.request.session.get("cart_id")
        if cart_id == None:
            cart = Cart()
            cart.save()
            cart_id = cart.id
            self.request.session['cart_id'] = cart_id
        cart = Cart.objects.get(id=cart_id)
        if self.request.user.is_authenticated:
            cart.user = self.request.user
            cart.save()
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        item_id = request.GET.get('item')
        delete_item = request.GET.get("delete", False)
        flash_message = ""
        item_added = False
        if item_id:
            item_instance = get_object_or_404(Vairation,id=item_id)
            qty  = request.GET.get('qty',1)
            try:
                if int(qty) < 1:
                    delete_item = True
            except:
                raise Http404
            cart_item,created = CartItem.objects.get_or_create(cart=cart,item=item_instance)
            if created:
                flash_message = "Item successfully added to the cart"
                item_added = True
            if delete_item:
                flash_message = "Item removed successfully"
                cart_item.delete()
            else:
                if not created:
                    flash_message = "Quantity has been updated succssfully"
                cart_item.quantity = qty
                cart_item.save()
            if not request.is_ajax():
                return HttpResponseRedirect(reverse("cart"))


        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total = None
            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None
            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None
            try:
                cart_total = cart_item.cart.total
            except:
                cart_total = None
            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0
            data = {
                "deleted":delete_item,
                "item_added":item_added,
                "line_total":total,
                "subtotal":subtotal,
                "tax_total":tax_total,
                "cart_total":cart_total,
                "flash_message":flash_message,
                "total_items":total_items
            }
            return JsonResponse(data)

        context = {
            "object":self.get_object()
        }
        template = self.template_name
        return render(request,template,context)





class CheckoutView(CartOrderMixin,FormMixin, DetailView):
    model = Cart
    template_name = "cart/checkout_view.html"
    form_class = GuestCheckoutForm

    def get_object(self,*args,**kwargs):
        cart = self.get_cart()
        if cart == None:
            return None
        return cart
    
    def get_context_data(self,*args,**kwargs):
        context = super(CheckoutView,self).get_context_data(*args,**kwargs)
        user_can_continue = False
        user_checkout_id = self.request.session.get("user_checkout_id")
        if self.request.user.is_authenticated:
            user_can_continue = True
            user_checkout,created = UserCheckout.objects.get_or_create(email=self.request.user.email)
            user_checkout.user = self.request.user
            user_checkout.save()
            context["client_token"] = user_checkout.get_client_token()
            self.request.session["user_checkout_id"] = user_checkout.id
        elif not self.request.user.is_authenticated and user_checkout_id == None:
            context['login_form'] = AuthenticationForm()
            context['next_url']  = self.request.build_absolute_uri()
        else:
            pass

        if user_checkout_id != None:
            user_can_continue = True
            if not self.request.user.is_authenticated:
                user_checkout_2 = UserCheckout.objects.get(id=user_checkout_id)
                context["client_token"] = user_checkout_2.get_client_token()

        
        context['order'] = self.get_order()
        context['user_can_continue'] = user_can_continue
        context['form'] = self.get_form()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object() 
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user_checkout, created = UserCheckout.objects.get_or_create(email=email)
            request.session["user_checkout_id"] = user_checkout.id
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse("checkout")
    
    def get(self,request,*args,**kwargs):
        get_data = super(CheckoutView,self).get(request,*args,**kwargs)
        cart = self.get_object()
        if cart == None:
            return redirect("cart")
        new_order = self.get_order()
        user_checkout_id = request.session.get("user_checkout_id")
        if user_checkout_id != None:
            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            if new_order.billing_address == None or new_order.shipping_address == None:
                return redirect("order_address")   
            new_order.user = user_checkout
            new_order.save()
        return get_data



class CheckoutFinalView(CartOrderMixin,View):
    def post(self,request,*args,**kwargs):
        order = self.get_order()
        order_total = order.order_total
        nonce = request.POST.get("payment_method_nonce")
        if nonce:
            result = gateway.transaction.sale({
                "amount": order_total,
                "payment_method_nonce": nonce,
                "billing": {
                    "postal_code": "{zipcode}".format(zipcode=order.billing_address.zipcode),
                },
                "options": {
                    "submit_for_settlement": True
                }
            })
            if result.is_success:
                order.mark_completed(order_id = result.transaction.id)
                messages.success(request,'Thank you for your order.')
                del request.session["cart_id"]
                del request.session['order_id']
            else:
                messages.success(request,'{}'.format(message=result.message))
                return redirect("checkout")

            return redirect("orders_detail", pk=order.pk)
           
    
    def get(self,request,*args,**kwargs):
        return redirect("checkout")



