from __future__ import unicode_literals

from django.db import models

ASSET_CLASSES = (
	('stock', 'Stock'), ('index', 'Index'), (None, '')
)
class  Investment(models.Model):
	symbol = models.CharField(max_length=5)
	name = models.CharField(max_length=50)
	market = models.CharField(max_length=50, blank=True)
	asset_class = models.CharField(max_length=10, blank=True, choices=ASSET_CLASSES)
	investments = models.ManyToManyField('self', null=True, blank=True, symmetrical=False, through="Allocation")
	
class Allocation(models.Model):
	portfolio = models.ForeignKey(Investment, related_name="portfolio")
	asset = models.ForeignKey(Investment, related_name="asset", null=True, blank=True)
	weight = models.DecimalField(max_digits=5, decimal_places=2)

class HistoricPrice(models.Model):
	date = models.DateField()
	price = models.CharField(max_length=50)
	investment = models.ForeignKey(Investment)