from django.shortcuts import render
from django.http import HttpResponse
import json
import io
import csv
import urllib2
from urllib import urlencode
from datetime import date
from .models import *
from django.core.serializers.json import DjangoJSONEncoder

def financialSourceURL(symbol, start_date, end_date):
	params = {
		's': symbol,
		'a': '%02d' % start_date.day,
		'b': '%02d' % start_date.month,
		'c': start_date.year,
		'd': '%02d' % end_date.day,
		'e': '%02d' % end_date.month,
		'f': end_date.year,
		'g': 'd',
		'ignore': '.csv',
	}
	return 'http://real-chart.finance.yahoo.com/table.csv?' + urlencode(params)

def get_historic_data(symbol, start_date, end_date):
	historic_data = (HistoricPrice.objects
	.values_list('date', 'close')
	.filter(date__range=(start_date, end_date), 
		investment__symbol__iexact=symbol))
	if(historic_data.exists()):
		return zip(*historic_data)
	else:
		response = urllib2.urlopen(financialSourceURL(symbol, start_date, end_date))
		csvstring = response.read()
		reader = csv.DictReader(io.StringIO(csvstring.decode('utf-8')), delimiter=',')
		investment = Investment.objects.get(symbol=symbol)
		dates = []
		closing = []
		#prices = []
		for row in reader:
			dates.append(row['Date'])
			closing.append(row['Close'])
			price = HistoricPrice(
				date = row['Date'],
				open = row['Open'],
				high = row['High'],
				low = row['Low'],
				close = row['Close'],
				adjusted_close = row['Adj Close'],
				volume = row['Volume'],
				investment = investment)
			price.save()
		#HistoricPrice.bulk_create(prices)
		return (dates, closing)

def generate_graph(symbol="YHOO", 
	start_date=date(2016,1,1), 
	end_date=date(2016,2,3)):
	(dates, closing) = get_historic_data(symbol, start_date, end_date)
	return [{
		'x': dates,
		'y': closing,
		'type': 'scatter'
	}]

def index(request):
	context = {
	'data': json.dumps(generate_graph(), cls=DjangoJSONEncoder)
	}
	return render(request, 'portfolios/index.html', context);