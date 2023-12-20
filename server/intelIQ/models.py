from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import json
import random

# from django.contrib.postgres.fields import JSONField


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=100) 

class Cryptocurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=False)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    market_cap_usd = models.DecimalField(max_digits=15, decimal_places=2)
    volume_usd_24h = models.DecimalField(max_digits=15, decimal_places=2)
    
    last_7_days_data = models.JSONField(null=True, blank=True)

    percent_change_1h = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percent_change_24h = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percent_change_7d = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def cal_percentage_change(self, old_value, new_value):
        if old_value == 0:
            return None
        return ((new_value - old_value) / old_value) * 100
    
    def update_price(self, new_price):
        # update price and cal percentage changes
        self.percent_change_1h = self.cal_percentage_change(self.price_usd, new_price)
        self.percent_change_24h = self.cal_percentage_change(self.price_usd_24h, new_price)
        self.percent_change_7d = self.cal_percentage_change(self.price_usd_7d, new_price)

        self.price_usd = new_price
        self.save()
        
    def generate_last_7_days_data(self):
        # data to draw the graph 
        # today = timezone.now().date()
        # last_7_days = [today - timezone.timedelta(days=i) for i in range(6, -1, -1)]
        # data = {'dates': [date.strftime('%Y-%m-%d') for date in last_7_days],
        #         'values': [45000.0 + i * 1000.0 for i in range(7)]}
        # return data
        today = timezone.now().date()
        last_7_days = [today - timezone.timedelta(days=i) for i in range(6, -1, -1)]

        random_values = [random.uniform(45000.0, 55000.0) for _ in range(10)]

        data = {'dates': [date.strftime('%Y-%m-%d') for date in last_7_days],
                'values': random_values}

        # data = {'dates': [date.strftime('%Y-%m-%d') for date in last_7_days],
        #         'values': [45000.0 + i * 1000.0 for i in range(10)]}

        return data
   

    def save(self, *args, **kwargs):
        # Ensure that price, volume, and market cap are saved with two decimal places
        self.price_usd = round(self.price_usd, 2)
        self.volume_usd_24h = round(self.volume_usd_24h, 2)
        self.market_cap_usd = round(self.market_cap_usd, 2)
        # self.generate_last_7_days_data()
        self.last_7_days_data = self.generate_last_7_days_data()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    # python3 manage.py makemigrations
    # python3 manage.py migrate
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)  
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return super().__str__()
    
    
class HistoricalPrice(models.Model):
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='historical_prices')
    timestamp = models.DateTimeField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        ordering = ['timestamp']
        
        
        
# from intelIQ.models import Cryptocurrency, HistoricalPrice
# from django.utils import timezone
# from decimal import Decimal

# btc = Cryptocurrency.objects.create(name='Bitcoin', price_usd=50000, percent_change_1h=0.3, percent_change_24h=1.41, percent_change_7d=3.4, market_cap_usd=900000, volume_usd_24h=56623.54)
# eth = Cryptocurrency.objects.create(name='Ethereum', price_usd=3000, percent_change_1h=0.3, percent_change_24h=1.41, percent_change_7d=3.4, market_cap_usd=56623.54, volume_usd_24h=56623.54)

# btc_historical_prices = [
#     HistoricalPrice(cryptocurrency=btc, timestamp=timezone.now() - timezone.timedelta(days=i), price_usd=Decimal(50000 - i * 100)) for i in range(7)
# ]

# eth_historical_prices = [
#     HistoricalPrice(cryptocurrency=eth, timestamp=timezone.now() - timezone.timedelta(days=i), price_usd=Decimal(3000 - i * 50)) for i in range(7)
# ]
# HistoricalPrice.objects.bulk_create(btc_historical_prices)
# HistoricalPrice.objects.bulk_create(eth_historical_prices)

