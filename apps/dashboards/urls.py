from django.urls import path
from . import views
from .views import (
    DashboardsView, 
    ProductsDashboardView,
    CategoriesDashboardView,
    OrdersDashboardView,
    NewOrderView,
    TablesDashboardView,
    SalesDashboardView,
    OrderDetailView,
    OrderPaymentView,
    OrderReceiptView,
    EditOrderView
)

urlpatterns = [
    path("", DashboardsView.as_view(template_name="dashboard_analytics.html"), name="index"),
    path("transactions/", DashboardsView.as_view(template_name="dashboard_transactions.html"), name="dashboard-transactions"),
    path("total-earning/", DashboardsView.as_view(template_name="dashboard_total_earning.html"), name="dashboard-total-earning"),
    path("logistics/", DashboardsView.as_view(template_name="dashboard_logistics.html"), name="dashboard-logistics"),
    path("deposit/", DashboardsView.as_view(template_name="dashboard_deposit.html"), name="dashboard-deposit"),
    
    # POS Dashboard URLs
    path("pos/products/", ProductsDashboardView.as_view(), name="dashboard-products"),
    path("pos/categories/", CategoriesDashboardView.as_view(), name="dashboard-categories"),
    path("pos/orders/", OrdersDashboardView.as_view(), name="dashboard-orders"),
    path("pos/orders/new/", NewOrderView.as_view(), name="dashboard-new-order"),
    path("pos/orders/<int:order_id>/edit/", EditOrderView.as_view(), name="dashboard-order-edit"),
    path("pos/orders/<int:order_id>/", OrderDetailView.as_view(), name="dashboard-order-detail"),
    path("pos/orders/<int:order_id>/payment/", OrderPaymentView.as_view(), name="dashboard-order-payment"),
    path("pos/orders/<int:order_id>/receipt/", OrderReceiptView.as_view(), name="dashboard-order-receipt"),
    path("pos/tables/", TablesDashboardView.as_view(), name="dashboard-tables"),
    path("sales/", SalesDashboardView.as_view(), name="dashboard-sales"),
]
