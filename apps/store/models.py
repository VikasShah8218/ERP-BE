from django.db import models
from apps.accounts.models import User,Department


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    class Meta:
        db_table = 'store_product'
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING,related_name="product_category")
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING,related_name="product_group",null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    serial_number = models.BigIntegerField(null=True,blank=True)
    model = models.CharField(max_length=255,null=True,blank=True)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,related_name="product_location")
    status = models.CharField(max_length=2, choices=[('1', '1'), ('2', '2')], default='0')
    product_image = models.ImageField(upload_to='products/', null=True, blank=True)
    bill_image = models.ImageField(upload_to='bills/', null=True, blank=True)
    other_document = models.FileField(upload_to='documents/', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class StoreRequest(models.Model):
    class Meta:
        db_table = 'store_request'
    employee = models.ForeignKey(User, on_delete=models.CASCADE,related_name="store_emp")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="store_product")
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=[('1', '1'), ('2', '2'), ('3', '3')], default='0')
    approval = models.ForeignKey('Approval', on_delete=models.SET_NULL, null=True, blank=True,related_name="store_approval")
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} requested {self.product}"

class Approval(models.Model):
    class Meta:
        db_table = 'store_approval'
    request = models.OneToOneField(StoreRequest, on_delete=models.CASCADE,related_name="approval_request")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approval_approver")
    status = models.CharField(max_length=50, choices=[('1', '1'), ('2', '2')], default='0')
    remarks = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Approval for {self.request}"

class StorePurchase(models.Model):
    class Meta:
        db_table = 'store_purchase'
    request = models.ForeignKey(StoreRequest, on_delete=models.CASCADE, related_name="store_purchase_request")
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name="store_purchase_supplier")
    status = models.CharField(max_length=50, choices=[('1', '1'), ('2', '2'), ('3', '3')], default='0')
    order_date = models.DateTimeField(auto_now_add=True)
    ordered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store_purchase_order_date")
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase {self.status} - {self.supplier.name}"

class Supplier(models.Model):
    class Meta:
        db_table = 'store_supplier'
    name = models.CharField(max_length=255, unique=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductIssue(models.Model):
    class Meta:
        db_table = 'store_product_issue'
    employee = models.ForeignKey(User, on_delete=models.CASCADE,related_name="issue_emp")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="issue_product")
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True, null=True)
    valid_upto = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} issued to {self.employee}"
