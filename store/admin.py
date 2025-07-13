from django.contrib import admin
from .models import Product,Order,OrderItem
# Register your models here.
admin.site.register(Product)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone', 'status', 'created_at')  # 👈 added status
    list_display_links = ('id', 'user')
    inlines = [OrderItemInline]
    search_fields = ['user__username', 'phone', 'name']
    list_filter = ['status', 'created_at']  # 👈 can now filter by status


admin.site.register(Order, OrderAdmin)


