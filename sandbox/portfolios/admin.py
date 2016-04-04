from django.contrib import admin
from .models import Investment, Allocation, HistoricPrice

class AllocationInline(admin.TabularInline):
	model = Allocation
	extra = 1
	fk_name = 'asset'

class InvestmentAdmin(admin.ModelAdmin):
	list_display = ('name', 'symbol', 'market', 'asset_class')
	inlines = (AllocationInline, )

class HistoricPriceAdmin(admin.ModelAdmin):
	list_display = ('date', 'price', 'investment_name')

	def investment_name(self, obj):
		return obj.investment.name

admin.site.register(Investment, InvestmentAdmin)
admin.site.register(HistoricPrice, HistoricPriceAdmin)