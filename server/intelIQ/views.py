from django.shortcuts import render
from .models import Cryptocurrency

# Create your views here.

def welcome(request):
    cryptocurrencies = Cryptocurrency.objects.all()
    context = {'cryptocurrencies': cryptocurrencies}
    return render(request, 'welcome.html', context)
