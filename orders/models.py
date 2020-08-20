from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save,post_save
from decimal import Decimal

from carts.models import Cart,CartItem
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

# Create your models here.
class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    email = models.EmailField(unique=True)
    braintree_id = models.CharField(max_length=120,null=True,blank=True)

    # merhcant_id

    def __str__(self):
        return self.email
    
    @property
    def get_braintree_id(self):
        instance = self
        if not instance.braintree_id:
            result = gateway.customer.create({
                "email": instance.email,
            })
            if result.is_success:
                # print(result.customer.id)
                instance.braintree_id = result.customer.id
                instance.save()
        return instance.braintree_id
            
    def get_client_token(self):
        customer_id = self.get_braintree_id
        if customer_id:
            client_token = gateway.client_token.generate({
                "customer_id": customer_id
            })
            return client_token
        return None

        

def update_braintree_id(sender,instance,*args,**kwargs):
    if not instance.braintree_id:
        instance.get_braintree_id
post_save.connect(update_braintree_id,sender=UserCheckout)

ADDRESS_TYPE = (
    ("billing",'Billing'),
    ('shipping','Shipping'),
)

class UserAddress(models.Model):
    user = models.ForeignKey(UserCheckout,on_delete=models.CASCADE)
    bill_type = models.CharField(max_length=120,choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __str__(self):
        return self.street
    
    def get_address(self):
        return "{street},{city},{country},{zipcode}".format(street=self.street,city=self.city,country=self.country,zipcode=self.zipcode)

ORDER_STATUS_CHOICES = (
    ("created",'Created'),
    ("paid",'Paid'),
    ("shipped",'Shipped'),
)

class Order(models.Model):
    status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default="created")
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    user = models.ForeignKey(UserCheckout,on_delete=models.CASCADE,null=True)
    shipping_address = models.ForeignKey(UserAddress,related_name='shipping_address', on_delete=models.CASCADE,null=True)
    billing_address = models.ForeignKey(UserAddress,related_name='billing_address', on_delete=models.CASCADE,null=True)
    shipping_total_price = models.DecimalField(decimal_places=2,max_digits=50,default=5.99)
    order_total = models.DecimalField(decimal_places=2,max_digits=50)
    order_id = models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return str(self.cart.id)
    
    def mark_completed(self,order_id=None):
        self.status = "paid"
        if order_id and not self.order_id:
            self.order_id = order_id
        self.save()




def order_pre_save(sender,instance,*args,**kwargs):
    shipping_total_price = instance.shipping_total_price
    cart_total = instance.cart.total
    order_total = Decimal(shipping_total_price) + Decimal(cart_total)
    instance.order_total = order_total


pre_save.connect(order_pre_save,sender=Order)