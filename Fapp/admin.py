from django.contrib import admin
from .models import  Product, Contact, Cart, CartItem, Order


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price','quantity','image','description']
    
admin.site.register(Product, ProductAdmin)


class ContactAdmin(admin.ModelAdmin):
    readonly_fields = ['name','email','message']

admin.site.register(Contact, ContactAdmin)    




class CartItemInline(admin.TabularInline):
    
	model = CartItem
	extra = 0
	readonly_fields = ['product', 'quantity', 'price', 'get_total_price']
	fields = ['product', 'quantity', 'price', 'get_total_price']

	def get_total_price(self, obj):
		return obj.get_total_price()
	get_total_price.short_description = 'Total Price'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at', 'updated_at', 'get_total_price']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_price', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__email', 'user__username']
    readonly_fields = ['order_number', 'user', 'cart', 'total_price', 'created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'cart', 'total_price', 'status')
        }),
        ('Address Information', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Payment Information', {
            'fields': ('payment_method',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['payment_method', 'shipping_address', 'billing_address']
        return self.readonly_fields