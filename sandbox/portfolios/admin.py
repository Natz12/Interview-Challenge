from django.contrib import admin
from .models import Investment, Allocation, HistoricPrice

class AllocationInline(admin.TabularInline):
	model = Allocation
	extra = 1
	fk_name = 'asset'

class InvestmentAdmin(admin.ModelAdmin):
	list_display = ('name', 'symbol', 'market', 'asset_class')
	list_filter = ('market', 'asset_class')
	search_fields = ('name', 'symbol', 'market')
	inlines = (AllocationInline, )

class HistoricPriceAdmin(admin.ModelAdmin):
	list_display = ('date', 'price', 'investment_name')
	list_editable = ('date', 'price')
	list_filter = ('date', )
	ordering = ('date', )
	search_fields = ('investment__name', 'investment__symbol', 'investment__market', 'investment__asset_class')

	def investment_name(self, obj):
		return obj.investment.symbol

admin.site.register(Investment, InvestmentAdmin)
admin.site.register(HistoricPrice, HistoricPriceAdmin)