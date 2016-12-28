import datetime

from django.db import models
from django.utils import timezone
from django.core import serializers

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, default="")
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def get_choice_set_all_json(self):
        return serializers.serialize("json", self.choice_set.all())

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.short_description = 'Published recently?'
    was_published_recently.boolean = True
    was_published_recently.admin_order_field = 'pub_date'

    def get_most_popular_choice(self):
        return self.choice_set.all().order_by('-votes')[:1]

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
