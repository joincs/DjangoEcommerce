from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.views.generic import DetailView, ListView
from .models import Product,Vairation,ProductImage,Category,ProductFeatured
from django.http import Http404
from .forms import VairationInventoryFormSet
from django.contrib import messages
from .mixins import StaffRequiredMixin, LoginRequiredMixin


# Create your views here.

def home(request):
    products = Product.objects.all().order_by("?")[:6]
    products2 = Product.objects.all().order_by("?")[:6]
    context = {
        'products':products,
        'products2':products2
    }
    return render(request,'theme/index.html',context)


class CategoryListView(ListView):
    model = Category
    template_name = 'products/product_list.html'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'

    def get_context_data(self,*args,**kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_category.all()
        default_products = obj.default_category.all()
        products = ( product_set | default_products ).distinct()
        context["products"] = products
        return context



class VariationListView(StaffRequiredMixin,ListView):
    model = Vairation
    template_name = 'products/variation_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(*args, **kwargs)
        context['formset'] = VairationInventoryFormSet(queryset=self.get_queryset())
        return context
    
    def get_queryset(self, *args, **kwargs):
        product_pk = self.kwargs.get("pk")
        if product_pk:
            product = get_object_or_404(Product, pk=product_pk)
            queryset = Vairation.objects.filter(product=product)
        return queryset
    
    def post(self,request, *args, **kwargs):
        formset = VairationInventoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(commit=False)
            for form in formset:
                new_item = form.save(commit=False)
                if new_item.title:
                    product_pk = self.kwargs.get("pk")
                    product = get_object_or_404(Product,pk=product_pk)
                    new_item.product = product
                    new_item.save()
            messages.success(request, "Your inventory and pricing has been updated.")
            return redirect("product:product_list")
        return Http404
    

import random
class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_details.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        instance = self.get_object

        context['related'] = sorted(Product.objects.get_related(instance)[:4], key=lambda x: random.random())
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        context['query'] = self.request.GET.get("q")
        return context
    
    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = self.model.objects.filter(
                Q(title__icontains=query)|
                Q(description__icontains=query)
            )
            try:
                qs2 = self.model.objects.filter(
                    Q(price=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs
    


