from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import post_save,pre_save

# Create your models here.

class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def all(self, *args, **kwargs):
        return self.get_queryset().active()
    
    def get_related(self, instance):
        products_one = self.get_queryset().filter(categories__in=instance().categories.all())
        product_two = self.get_queryset().filter(default=instance().default)
        qs = (products_one | product_two).exclude(id=instance().id).distinct()
        return qs


class Product(models.Model):
    title        = models.CharField(max_length=120)
    description  = models.TextField(null=True,blank=True)
    price        = models.DecimalField(decimal_places=2, max_digits=20)
    active       = models.BooleanField(default=True)
    categories   = models.ManyToManyField('Category', related_name='product_category',blank=True)
    default      = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='default_category', null=True,blank=True)
    # slug
    # inventory

    objects = ProductManager()

    class Meta:
        ordering = ['-title']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('products:product_detail',kwargs={'pk':self.pk})
    
    def get_image_url(self):
        img = self.product_image.first()
        if img:
            return img.image.url
        return img



class Vairation(models.Model):
    product      = models.ForeignKey(Product,on_delete=models.CASCADE, related_name='product_variation')
    title        = models.CharField(max_length=120)
    price        = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price        = models.DecimalField(decimal_places=2, max_digits=20,null=True, blank=True)
    active       = models.BooleanField(default=True)
    inventory    = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title + "(" + str(self.product)+ ")"

    def getprice(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price
    
    def get_html_price(self):
        if self.sale_price is not None:
            html_text = "<span class='sale-price'>{sale_price}</span> <span style='color:red;text-decoration:line-through;'>{price}</span>".format(sale_price=self.sale_price, price=self.price)
        else:
            html_text = "<span class='price'>{price}</span>".format(price=self.price)
        return html_text

    def get_absolute_url(self):
        return self.product.get_absolute_url()
    
    def add_to_cart(self):
        return '{cart}?item={item_id}&qty=1'.format(cart=reverse("cart"), item_id=self.id,)

    def remove_to_cart(self):
        return '{cart}?item={item_id}&qty=1&delete=True'.format(cart=reverse("cart"), item_id=self.id)
    
    def get_title(self):
        return "{title}({variation_item})".format(title=self.product.title,variation_item=self.title)
    


def product_post_save_receiver(sender, instance,created, *args, **kwargs):
    product = instance
    variations = product.product_variation.all()
    if variations.count() == 0:
        new_var = Vairation()
        new_var.product = product
        new_var.title   =  "Default"
        new_var.price   = product.price
        new_var.save()


post_save.connect(product_post_save_receiver, sender=Product)


def image_upload_to(instance,filename):
    title          = instance.product.title
    slug           = slugify(title)
    file_extension = filename.split(".")[1]
    new_filename = "{0}.{1}".format(instance.id,file_extension)
    return "product/{slug}/{filename}".format(slug=slug,filename=new_filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name='product_image')
    image   = models.ImageField(upload_to=image_upload_to)

    def __str__(self):
        return self.product.title


class Category(models.Model):
    title        = models.CharField(max_length=120, unique=True)
    slug         = models.SlugField(unique=True)
    description  = models.TextField(blank=True,null=True)
    active       = models.BooleanField(default=True)
    timestamp    = models.DateTimeField(auto_now_add=True)
    updated      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('product_categories:categories_detail',kwargs={'slug':self.slug})



def image_upload_to_featured(instance,filename):
    title          = instance.product.title
    slug           = slugify(title)
    file_extension = filename.split(".")[1]
    new_filename = "{instance_id}.{file_ext}".format(instance_id=instance.id,file_ext=file_extension)
    return "product/{slug}/featured/{filename}".format(slug=slug,filename=new_filename)

class ProductFeatured(models.Model):
    product             = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_featured')
    image               = models.ImageField(upload_to=image_upload_to_featured)
    title               = models.CharField(max_length=120,null=True,blank=True)
    text                = models.CharField(max_length=120,null=True,blank=True)
    text_right          = models.BooleanField(default=False)
    price               = models.BooleanField(default=False)
    active              = models.BooleanField(default=True)
    make_img_background = models.BooleanField(default=False)
    timestamp           = models.DateTimeField(auto_now_add=True)
    updated             = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title


