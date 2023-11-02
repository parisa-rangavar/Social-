from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Relations(models.Model):
    from_users = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    to_user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='following')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_users} following {self.to_user}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=0)
    bio = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='profile/%Y/%m/%d/', null=True, blank=True)




