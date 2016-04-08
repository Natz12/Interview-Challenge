import csv
import urllib2
import urllib
import datetime
import ast
import json
from django.db.models import Q
from django.views.generic import ListView, View
from django.http import JsonResponse
from django.core.exceptions import ValidationError
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
        finish = historicprice.last().date
        start = historicprice.first().date
      else:
        finish = datetime.date.today()
        start = finish - delta
    else:
      finish = form.cleaned_data['finish']
      start = form.cleaned_data['start']
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
      else:        
        url = 'http://real-chart.finance.yahoo.com/table.csv?%s' % urllib.urlencode({
          'a':(start.month - 1), 'b':start.day,'c':start.year,
          'd':(finish.month - 1), 'e':finish.day, 'f':finish.year, 
          's':symbol, 'g': 'd', 'ignore':'.csv' })
        print("Fetching from %s" % url)
        response = csv.DictReader(urllib2.urlopen(url))
        json_response = [row for row in response]
        models = []
        for price in json_response:
          model = HistoricPrice(date=price['Date'], price=price, investment=investment)
          try:
            model.full_clean()
            models.append(model)
          except ValidationError as e:
            pass
        HistoricPrice.objects.bulk_create(models)

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
      url = 'http://d.yimg.com/aq/autoc?%s' % urllib.urlencode({'query': query, 'region':'US', 'lang':'en-US'});
      print('Fetching list from %s' % url)
      response = json.load(urllib2.urlopen(url))
      models = []
      for i in response['ResultSet']['Result']:
        if asset_type(i['typeDisp']):
          model = Investment(symbol=i['symbol'], name=i['name'], market=i['exch'], asset_class=asset_type(i['typeDisp']))
          try:
            model.full_clean()
            models.append(model)
          except ValidationError as e:
            pass
      Investment.objects.bulk_create(models)

      json_response = [{'name': a['name'], 'symbol': a['symbol']} for a in response['ResultSet']['Result']]

    response = JsonResponse(json_response[:5], safe=False)
    response['Access-Control-Allow-Origin'] = '*'
    return response

def asset_type(a):
  if a == "Equity":
    return "stock"
  else:
    return None