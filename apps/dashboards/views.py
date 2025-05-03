from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from pos.models import Order, Table, Product, OrderItem, Category
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

        return context

@login_required
def analytics(request):
    return render(request, 'dashboard_analytics.html')

@login_required
def crm(request):
    return render(request, 'dashboard_crm.html')

@login_required
def ecommerce(request):
    return render(request, 'dashboard_ecommerce.html')


class RestaurantDashboardView(LoginRequiredMixin, TemplateView):
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

class ProductsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.select_related('category').all()
        return context

class CategoriesDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.prefetch_related('products').all()
        return context

class OrdersDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.select_related('customer', 'table').prefetch_related('items').all()
        return context

class TablesDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_tables.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Table.objects.all()
        return context
