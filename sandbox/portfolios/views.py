import csv
from django.views.generic import ListView, View
from portfolios.models import Investment, Allocation, HistoricPrice
import urllib2
import urllib
from django.http import JsonResponse
from portfolios.forms import DateFilterForm
from django.core import serializers
import datetime
from django.db.models import Q
import ast
import json

class InvestmentList(View):
  def get(self, request):
    form = DateFilterForm(request.GET)
    if not form.is_valid():
      json_response = form.errors.as_json()
    else:
      start = form.cleaned_data['start']
      finish = form.cleaned_data['finish']
      symbol = form.cleaned_data['symbol']

      delta = datetime.timedelta(days=3)
      start_plus = start + delta
      start_minus = start - delta
      finish_plus = finish + delta
      finish_minus = finish - delta

      investment = Investment.objects.get(symbol__iexact=symbol)
      if investment:
        prices = HistoricPrice.objects.filter(investment=investment)
        if prices.filter(Q(date__range=[start_minus, start_plus])|Q(date__range=[finish_minus, finish_plus])).exists():
          objects = prices.filter(date__range=[start, finish])
          json_response = map(ast.literal_eval, objects.values_list('price', flat=True))
        else:        
          url = 'http://real-chart.finance.yahoo.com/table.csv?%s' % urllib.urlencode({
            'a':(start.month - 1), 'b':start.day,'c':start.year,
            'd':(finish.month - 1), 'e':finish.day, 'f':finish.year, 
            's':symbol, 'g': 'd', 'ignore':'.csv' })
          print("Fetching from %s" % url)
          remote_response = urllib2.urlopen(url)
          cr = csv.DictReader(remote_response)
          json_response = [row for row in cr]
          HistoricPrice.objects.bulk_create([HistoricPrice(date=price['Date'], price=price, investment=investment) for price in json_response])

        return JsonResponse(json_response, safe=False)

class AllocationList(ListView):
  model = Allocation

class HistoricPriceList(ListView):
  model = HistoricPrice

class InvestmentSearchList(View):
  def get(self, request, query):
    investments = Investment.objects.filter(symbol__icontains=query)

    if investments.exists():
      json_response = [i for i in investments.values('symbol', 'name')]
    else:
      url = 'http://d.yimg.com/aq/autoc?query=%s&region=US&lang=en-US' % query
      print('Fetching list from %s' % url)
      remote_response = urllib2.urlopen(url)
      cr = json.load(remote_response)
      json_response = [{'name': a['name'], 'symbol': a['symbol']} for a in cr['ResultSet']['Result']]

    return JsonResponse(json_response, safe=False)