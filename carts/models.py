from django.db import models
from django.conf import settings
from product.models import Vairation
from django.urls import reverse
from django.db.models.signals import pre_save,post_save,post_delete
from decimal import Decimal

# Create your models here.


class CartItem(models.Model):
    cart            = models.ForeignKey('Cart',on_delete=models.CASCADE,null=True)
    item            = models.ForeignKey(Vairation,on_delete=models.CASCADE,blank=True,null=True, related_name='cart_item')
    quantity        = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return self.item.title  
    
    def remove(self):
        return self.item.remove_to_cart()


def cart_item_pre_save_receiver(sender,instance,*args,**kwargs):
    qty = instance.quantity
    if int(qty) >= 1:
        price = instance.item.getprice()
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total

pre_save.connect(cart_item_pre_save_receiver,sender=CartItem)


def cart_item_post_save_receiver(sender,instance,*args,**kwargs):
    instance.cart.update_subtotal()

post_save.connect(cart_item_post_save_receiver,sender=CartItem)

post_delete.connect(cart_item_post_save_receiver,sender=CartItem)
    


class Cart(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.CASCADE)
    items           = models.ManyToManyField(Vairation,through=CartItem)
    timestamp       = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    subtotal        = models.DecimalField(max_digits=50,decimal_places=2, default=0.00)
    tax_percentage  = models.DecimalField(max_digits=10,decimal_places=5, default=0.085)
    tax_total       = models.DecimalField(max_digits=50,decimal_places=2, default=0.00)
    total           = models.DecimalField(max_digits=50,decimal_places=2, default=0.00)
    # discount
    # shipping

    def __str__(self):
        return str(self.id)
    
    def update_subtotal(self):
        subtotal = 0
        items = self.cartitem_set.all()
        for item in items:
            subtotal += item.line_item_total
        self.subtotal = "%.2f" %(subtotal)
        self.save()
    

def do_tax_and_total_receiver(sender,instance,*args,**kwargs):
    subtotal            = Decimal(instance.subtotal)
    tax_total           = round(subtotal * Decimal(instance.tax_percentage),2)
    total               = round(subtotal + Decimal(tax_total),2)
    instance.tax_total  = "%.2f" %(tax_total)
    instance.total      = "%.2f" %(total)
    # instance.save()


pre_save.connect(do_tax_and_total_receiver,sender=Cart)
