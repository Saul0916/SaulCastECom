from django.db import models
from datetime import timedelta
from django.contrib.auth.models import User

class Podcast(models.Model):
    title = models.CharField(max_length=100)
    length = models.IntegerField()
    date_created = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    thumbnail_url = models.CharField(max_length=200)

    class Meta:
        app_label = 'SaulCastECom'

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def total_price(self):
        return self.podcast.price * self.quantity