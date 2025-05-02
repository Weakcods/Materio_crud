from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Customer, Order, OrderItem, Payment, Table

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_available', 'display_order', 'product_count', 'created_at')
    list_filter = ('is_available',)
    search_fields = ('name',)
    ordering = ('display_order', 'name')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'preparation_time', 'spicy_level_display', 'stock')
    list_filter = ('category', 'is_available', 'is_featured', 'spicy_level')
    search_fields = ('name', 'description', 'barcode')
    ordering = ('category', 'name')
    
    def spicy_level_display(self, obj):
        spicy_icons = '🌶️' * obj.spicy_level if obj.spicy_level > 0 else 'Not Spicy'
        return spicy_icons
    spicy_level_display.short_description = 'Spicy Level'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'status', 'is_occupied')
    list_filter = ('status', 'is_occupied')
    search_fields = ('number',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'orders_count')
    search_fields = ('name', 'email', 'phone')

    def orders_count(self, obj):
        return obj.orders.count()
    orders_count.short_description = 'Total Orders'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'table', 'order_type', 'order_status', 'total_amount', 'payment_status', 'order_date')
    list_filter = ('order_status', 'payment_status', 'order_type', 'order_date')
    search_fields = ('customer__name', 'table__number')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'table', 'cashier', 'order_type')
        }),
        ('Status Information', {
            'fields': ('order_status', 'payment_status')
        }),
        ('Timing Information', {
            'fields': ('order_date', 'preparation_start_time', 'preparation_end_time', 'served_time')
        }),
        ('Financial Information', {
            'fields': ('total_amount',)
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'notes')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_method', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('order__id', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
