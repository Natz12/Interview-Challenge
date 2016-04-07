import csv
import urllib2
import urllib
import datetime
import ast
import json
from django.db.models import Q
from django.views.generic import ListView, View
from django.http import JsonResponse
from portfolios.models import Investment, Allocation, HistoricPrice
from portfolios.forms import DateFilterForm

class InvestmentList(View):
  def get(self, request):
    symbol = "YHOO"
    delta = datetime.timedelta(days=3)
    form = DateFilterForm(request.GET)
    if not form.is_valid():
      historicprice = HistoricPrice.objects.filter(investment__symbol__iexact=symbol)
      if historicprice.exists():
        start = historicprice.first().date
        finish = historicprice.last().date
      else:
        finish = datetime.date.today()
        start = finish - delta
    else:
      start = form.cleaned_data['start']
      finish = form.cleaned_data['finish']
      symbol = form.cleaned_data['symbol']

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
        print(json_response)
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
      investments = []
      for i in cr['ResultSet']['Result']:
        if asset_type(i['typeDisp']):
          investment = Investment(symbol=i['symbol'], name=i['name'], market=i['exch'], asset_class=asset_type(i['typeDisp']))
          investments.append(investment)
      Investment.objects.bulk_create(investments)

      json_response = [{'name': a['name'], 'symbol': a['symbol']} for a in cr['ResultSet']['Result']]

    return JsonResponse(json_response, safe=False)

def asset_type(a):
  if a == "Equity":
    return "stock"
  else:
    return None