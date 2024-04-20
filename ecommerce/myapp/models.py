from django.db import models

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_images/')
    sold_out = models.BooleanField(default=False)  # Keep sold_out field
    featured = models.BooleanField(default=False)  # Add featured field
    main_product = models.BooleanField(default=False)  # Add main_product field
    
    def __str__(self):
        return self.title

