from django.db import models
from django.contrib.auth.models import User

class CarAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # optional user
    front_image = models.ImageField(upload_to='uploads/')
    left_image = models.ImageField(upload_to='uploads/')
    right_image = models.ImageField(upload_to='uploads/')
    back_image = models.ImageField(upload_to='uploads/')
    detected_parts = models.JSONField()  # stores detected parts and cost
    total_cost = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis #{self.id} - Total ${self.total_cost}"
