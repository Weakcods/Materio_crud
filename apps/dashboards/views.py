from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.http import JsonResponse, Http404
from pos.models import Order, Table, Product, OrderItem, Category, Customer, Payment, ProductOptionChoice
from datetime import timedelta


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Add payment data when viewing transactions template
        if self.template_name == 'dashboard_transactions.html':
            from pos.models import Payment
            context['payments'] = Payment.objects.select_related('order').all().order_by('-payment_date')
        
        return context

@login_required
def analytics(request):
    from pos.models import Order, Customer, Product, Payment
    from django.utils import timezone
    from django.db.models import Sum, Count
    from datetime import timedelta
    
    # Get date ranges
    today = timezone.now()
    start_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = start_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    
    # Calculate current month metrics
    current_month_sales = Order.objects.filter(
        created_at__gte=start_month,
        payment_status='PAID'
    ).aggregate(
        total_amount=Sum('total_amount'),
        orders_count=Count('id')
    )
    
    # Calculate last month metrics for comparison
    last_month_sales = Order.objects.filter(
        created_at__range=[last_month_start, last_month_end],
        payment_status='PAID'
    ).aggregate(
        total_amount=Sum('total_amount'),
        orders_count=Count('id')
    )
    
    # Calculate growth percentages
    current_amount = current_month_sales['total_amount'] or 0
    last_amount = last_month_sales['total_amount'] or 1  # Avoid division by zero
    revenue_growth = ((current_amount - last_amount) / last_amount) * 100
    
    # Get current metrics
    context = {
        'total_sales': current_month_sales['orders_count'] or 0,
        'total_customers': Customer.objects.count(),
        'total_products': Product.objects.filter(is_available=True).count(),
        'total_revenue': current_amount,
        'revenue_growth': revenue_growth,
        
        # Weekly transactions for chart
        'weekly_transactions': Order.objects.filter(
            created_at__gte=today - timedelta(days=7)
        ).values('created_at__date').annotate(
            daily_sales=Sum('total_amount')
        ).order_by('created_at__date'),
        
        # Top selling products
        'top_products': OrderItem.objects.filter(
            order__created_at__gte=start_month
        ).values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_quantity')[:5],
        
        # Recent transactions
        'recent_transactions': Payment.objects.select_related(
            'order'
        ).order_by('-payment_date')[:10]
    }
    
    return render(request, 'dashboard_analytics.html', context)

@login_required
def crm(request):
    return render(request, 'dashboard_crm.html')

@login_required
def ecommerce(request):
    return render(request, 'dashboard_ecommerce.html')


class RestaurantDashboardView(LoginRequiredMixin, DashboardsView):
    template_name = 'restaurant_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Active orders (pending, preparing, ready)
        context['active_orders'] = Order.objects.filter(
            order_status__in=['PENDING', 'PREPARING', 'READY']
        ).select_related('table', 'customer').prefetch_related('items')

        # Table status
        context['tables'] = Table.objects.all()

        # Today's statistics
        today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        context['today_sales'] = Order.objects.filter(
            created_at__gte=today_start,
            payment_status='PAID'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        context['orders_today'] = Order.objects.filter(created_at__gte=today_start).count()

        # Average preparation time for completed orders today
        avg_prep_time = Order.objects.filter(
            created_at__gte=today_start,
            preparation_start_time__isnull=False,
            preparation_end_time__isnull=False
        ).aggregate(
            avg_time=Avg(
                (timezone.ExpressionWrapper(
                    timezone.F('preparation_end_time') - timezone.F('preparation_start_time'),
                    output_field=timezone.DurationField()
                ))
            )
        )['avg_time']
        
        context['avg_preparation_time'] = round(avg_prep_time.total_seconds() / 60 if avg_prep_time else 0)

        # Popular items
        popular_items = OrderItem.objects.filter(
            order__created_at__gte=today_start - timedelta(days=30)
        ).values(
            'product__name',
            'product__category__name'
        ).annotate(
            order_count=Count('id'),
            total_revenue=Sum('subtotal')
        ).order_by('-order_count')[:10]

        context['popular_items'] = popular_items
        context['popular_items_count'] = popular_items.count()

        # Recent activities
        recent_orders = Order.objects.select_related('customer', 'table').order_by('-created_at')[:10]
        recent_activities = []
        
        for order in recent_orders:
            status_colors = {
                'PENDING': 'warning',
                'PREPARING': 'info',
                'READY': 'primary',
                'SERVED': 'success',
                'COMPLETED': 'success',
                'CANCELLED': 'danger'
            }
            
            recent_activities.append({
                'title': f'Order #{order.id}',
                'description': f'{order.get_order_status_display()} - {order.customer.name if order.customer else "Walk-in"}',
                'timestamp': order.created_at,
                'status_color': status_colors.get(order.order_status, 'secondary')
            })

        context['recent_activities'] = recent_activities

        return context

class ProductsDashboardView(LoginRequiredMixin, DashboardsView):
    template_name = 'dashboard_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.select_related('category').all()
        return context

class CategoriesDashboardView(LoginRequiredMixin, DashboardsView):
    template_name = 'dashboard_categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.prefetch_related('products').all()
        return context

class OrdersDashboardView(LoginRequiredMixin, DashboardsView):
    template_name = 'dashboard_orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.select_related(
            'customer', 'table'
        ).prefetch_related('items__product').all()
        return context

class NewOrderView(LoginRequiredMixin, DashboardsView):
    template_name = 'dashboard_new_order.html'

    def get_context_data(self, **kwargs):
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        context = super().get_context_data(**kwargs)
        products = Product.objects.filter(is_available=True).select_related('category')
        
        # Prepare products data with serialized options
        products_data = []
        for product in products:
            options_data = []
            for option in product.options.all():
                choices = option.choices.filter(is_available=True).values('id', 'name', 'additional_price')
                if choices:
                    options_data.append({
                        'name': option.name,
                        'is_required': option.is_required,
                        'choices': list(choices)
                    })
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'stock': product.stock,
                'options': options_data
            })
        
        context.update({
            'tables': Table.objects.filter(status='AVAILABLE'),
            'customers': Customer.objects.all(),
            'products': products,
            'products_json': json.dumps(products_data, cls=DjangoJSONEncoder)
        })
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Get form data
            order_type = request.POST.get('order_type')
            customer_id = request.POST.get('customer')
            table_id = request.POST.get('table')
            special_instructions = request.POST.get('special_instructions')
            
            # Create order
            order = Order.objects.create(
                customer_id=customer_id if customer_id else None,
                table_id=table_id if table_id else None,
                cashier=request.user,
                order_type=order_type,
                special_instructions=special_instructions,
                order_status='PENDING',
                payment_status='PENDING'
            )
            
            # Process order items
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            
            total_amount = 0
            for index, (product_id, quantity) in enumerate(zip(products, quantities)):
                if product_id and quantity:
                    product = Product.objects.get(id=product_id)
                    quantity = int(quantity)
                    
                    # Create order item with base price
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        subtotal=product.price * quantity  # Initial subtotal with just base price
                    )
                    
                    # Handle options after order item is created
                    option_ids = request.POST.getlist(f'item_options[{index}][]')
                    if option_ids:
                        selected_options = ProductOptionChoice.objects.filter(id__in=option_ids)
                        # Add selected options
                        order_item.selected_options.set(selected_options)
                        # Update options text
                        options_text = ', '.join([f"{opt.option.name}: {opt.name}" for opt in selected_options])
                        order_item.options_text = options_text
                        # Update subtotal with options
                        order_item.update_subtotal()
                    
                    # Get the latest subtotal after options are added
                    order_item.refresh_from_db()
                    total_amount += order_item.subtotal
                    
                    # Update product stock
                    product.stock -= quantity
                    product.save()
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            # Update table status if dine-in
            if order_type == 'DINE_IN' and table_id:
                table = Table.objects.get(id=table_id)
                table.status = 'OCCUPIED'
                table.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Order created successfully'
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False, 
                'error': str(e),
                'details': traceback.format_exc()
            })

class TablesDashboardView(LoginRequiredMixin, DashboardsView):
    template_name = 'dashboard_tables.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Table.objects.all()
        return context

class SalesDashboardView(LoginRequiredMixin, DashboardsView):
    template_name = "dashboard_sales.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Get sales data
        sales_data = Order.objects.filter(
            created_at__range=[start_date, end_date],
            order_status='COMPLETED'
        ).aggregate(
            total_sales=Sum('total_amount'),
            total_orders=Count('id'),
            avg_order_value=Avg('total_amount')
        )
        
        # Top selling products
        top_products = OrderItem.objects.filter(
            order__created_at__range=[start_date, end_date],
            order__order_status='COMPLETED'
        ).values(
            'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('subtotal')
        ).order_by('-total_quantity')[:5]
        
        category_sales = OrderItem.objects.filter(
            order__created_at__range=[start_date, end_date],
            order__order_status='COMPLETED'
        ).values(
            'product__category__name'
        ).annotate(
            total_sales=Sum('subtotal')
        ).order_by('-total_sales')

        # Calculate percentages if there are sales
        total_sales = sales_data.get('total_sales') or 0
        if total_sales > 0:
            for category in category_sales:
                category['percentage'] = (category['total_sales'] / total_sales) * 100
        
        context.update({
            'sales_data': sales_data,
            'top_products': top_products,
            'category_sales': category_sales,
            'start_date': start_date,
            'end_date': end_date
        })
        
        return context

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

class OrderDetailView(LoginRequiredMixin, DashboardsView):
    def get(self, request, order_id):
        order = get_object_or_404(Order.objects.select_related('customer').prefetch_related('items__product'), id=order_id)
        data = {
            'id': order.id,
            'customer': {'name': order.customer.name} if order.customer else None,
            'order_type': order.order_type,
            'order_type_display': order.get_order_type_display(),
            'order_status': order.order_status,
            'order_status_display': order.get_order_status_display(),
            'payment_status': order.payment_status,
            'payment_status_display': order.get_payment_status_display(),
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.isoformat(),
            'items': [{
                'product': {'name': item.product.name},
                'quantity': item.quantity,
                'price': float(item.price),
                'subtotal': float(item.subtotal)
            } for item in order.items.all()]
        }
        return JsonResponse(data)

    def delete(self, request, order_id):
        try:
            order = get_object_or_404(Order.objects.select_related('table').prefetch_related('items__product'), id=order_id)
            
            if order.order_status != 'PENDING':
                return JsonResponse({'error': 'Can only delete pending orders'}, status=400)
            
            if order.payment_status == 'PAID':
                return JsonResponse({'error': 'Cannot delete paid orders'}, status=400)
                
            # Begin cleanup
            # 1. Restore product stock
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save()
                
            # 2. Free up table if it was a dine-in order
            if order.table and order.order_type == 'DINE_IN':
                table = order.table
                table.status = 'AVAILABLE'
                table.save()
            
            # 3. Delete the order (this will cascade delete items due to FK relationship)
            order.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Order deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class OrderPaymentView(LoginRequiredMixin, DashboardsView):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.payment_status != 'PENDING':
            return JsonResponse({'error': 'Order is already paid or payment failed'}, status=400)
        
        payment_method = request.POST.get('payment_method')
        amount = request.POST.get('amount')
        
        if not payment_method or not amount:
            return JsonResponse({'error': 'Payment method and amount are required'}, status=400)
            
        try:
            amount = float(amount)
            if amount != float(order.total_amount):
                return JsonResponse({'error': 'Invalid payment amount'}, status=400)
                
            # Create payment record
            Payment.objects.create(
                order=order,
                amount=amount,
                payment_method=payment_method
            )
            
            # Update order status
            order.payment_status = 'PAID'
            order.save()
            
            return JsonResponse({'success': True})
        except ValueError:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class OrderReceiptView(LoginRequiredMixin, DashboardsView):
    def get(self, request, order_id):
        order = get_object_or_404(Order.objects.select_related('customer').prefetch_related('items__product'), id=order_id)
        if order.payment_status != 'PAID':
            return JsonResponse({'error': 'Cannot print receipt for unpaid order'}, status=400)
        
        # TODO: Generate PDF receipt
        return JsonResponse({'error': 'Receipt printing not implemented'}, status=501)

class EditOrderView(LoginRequiredMixin, DashboardsView):
    template_name = 'dashboard_edit_order.html'
    
    def get_context_data(self, **kwargs):
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order.objects.select_related('customer')
                                 .prefetch_related('items__product', 'items__selected_options'), 
                                 id=self.kwargs['order_id'])
        
        if order.order_status != 'PENDING':
            raise Http404("Only pending orders can be edited")
            
        products = Product.objects.filter(is_available=True).select_related('category')
        
        # Prepare products data with serialized options
        products_data = []
        for product in products:
            options_data = []
            for option in product.options.all():
                choices = option.choices.filter(is_available=True).values('id', 'name', 'additional_price')
                if choices:
                    options_data.append({
                        'name': option.name,
                        'is_required': option.is_required,
                        'choices': list(choices)
                    })
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'options': options_data
            })

        context.update({
            'order': order,
            'products': products,
            'products_json': json.dumps(products_data, cls=DjangoJSONEncoder),
            'customers': Customer.objects.all()  # Removed is_active filter
        })
        
        return context
            
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        if order.order_status != 'PENDING':
            return JsonResponse({'error': 'Only pending orders can be edited'}, status=400)
            
        try:
            # Get form data
            order_type = request.POST.get('order_type')
            customer_id = request.POST.get('customer')
            special_instructions = request.POST.get('special_instructions')
            
            # Update order basic info
            order.order_type = order_type
            order.customer_id = customer_id if customer_id else None
            order.special_instructions = special_instructions
            
            # Clear any existing table assignment
            if order.table:
                # Free up old table
                old_table = order.table
                old_table.status = 'AVAILABLE'
                old_table.save()
                order.table = None
            
            # Process order items
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            
            # First, restore stock for removed items
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save()
            
            # Clear existing items
            order.items.all().delete()
            
            # Add new items
            total_amount = 0
            for i, (product_id, quantity) in enumerate(zip(products, quantities)):
                if not product_id or not quantity:
                    continue
                    
                product = Product.objects.get(id=product_id)
                quantity = int(quantity)
                
                # Check stock availability
                if product.stock < quantity:
                    return JsonResponse({
                        'error': f'Not enough stock for {product.name}. Available: {product.stock}'
                    }, status=400)
                
                # Create order item
                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                
                # Process options if any
                item_options = request.POST.getlist(f'item_options[{i}][]')
                if item_options:
                    item.selected_options.set(item_options)
                    
                # Calculate item total including options
                option_total = sum(
                    choice.additional_price 
                    for choice in item.selected_options.all()
                )
                item.subtotal = (product.price + option_total) * quantity
                item.save()
                
                # Update stock
                product.stock -= quantity
                product.save()
                
                total_amount += item.subtotal
            
            order.total_amount = total_amount
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Order updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
