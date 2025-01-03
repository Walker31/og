from django.db import models
from customer.models import Customer
from products.models import Product

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, db_column='customer_id', on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product,db_column = 'product_id', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)  
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart'
        managed = False 

    def __str__(self):
        return f"Cart {self.id} for Customer {self.customer_id.name}"

