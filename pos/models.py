from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    image = models.ImageField(upload_to='menu_categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

class ProductOption(models.Model):
    """For options like 'Size', 'Temperature', 'Sugar Level', etc."""
    name = models.CharField(max_length=100)  # e.g., "Size", "Temperature"
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductOptionChoice(models.Model):
    """For specific choices like 'Small', 'Medium', 'Large' or 'Hot', 'Cold'"""
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='choices')
    name = models.CharField(max_length=100)  # e.g., "Small", "Hot"
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.option.name} - {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    preparation_time = models.IntegerField(help_text='Preparation time in minutes', default=15)
    allergens = models.TextField(blank=True, null=True, help_text='Comma-separated list of allergens')
    calories = models.IntegerField(null=True, blank=True)
    spicy_level = models.IntegerField(default=0, choices=[(0, 'Not Spicy'), (1, 'Mild'), (2, 'Medium'), (3, 'Hot'), (4, 'Extra Hot')])
    stock = models.IntegerField(default=0)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    options = models.ManyToManyField(ProductOption, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category', 'name']

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    number = models.CharField(max_length=10)
    capacity = models.IntegerField(default=4)
    is_occupied = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'),
        ('MAINTENANCE', 'Maintenance')
    ], default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.number} ({self.get_status_display()})"

    class Meta:
        ordering = ['number']

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    ORDER_TYPE_CHOICES = [
        ('DINE_IN', 'Dine In'),
        ('TAKEAWAY', 'Takeaway'),
        ('DELIVERY', 'Delivery'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='DINE_IN')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(default=timezone.now)
    preparation_start_time = models.DateTimeField(null=True, blank=True)
    preparation_end_time = models.DateTimeField(null=True, blank=True)
    served_time = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    special_instructions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

    class Meta:
        ordering = ['-created_at']

    @property
    def preparation_time(self):
        if self.preparation_start_time and self.preparation_end_time:
            return (self.preparation_end_time - self.preparation_start_time).total_seconds() / 60
        return None

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    selected_options = models.ManyToManyField(ProductOptionChoice, blank=True, related_name='order_items')
    options_text = models.TextField(blank=True, null=True, help_text='Text representation of selected options')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        base_price = self.price
        options_price = sum(option.additional_price for option in self.selected_options.all())
        total_price = base_price + options_price
        self.subtotal = self.quantity * total_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('TRANSFER', 'Bank Transfer'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(default=timezone.now)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id}"
