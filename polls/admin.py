from django.contrib import admin

from .models import Category, Question, Choice

# Register your models here.
# admin.site.register(Question)
class ChoiceInLine(admin.StackedInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    """docstring for QuestionAdmin"""
    list_display = ('question_text', 'category', 'pub_date', 'was_published_recently',
                    'get_most_popular_choice')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    fieldsets = [
        (None, {'fields' : ['question_text']}),
        ('Category:', {'fields' : ['category'], 'classes' : ['list-group']}),
        ('Date Info:', {'fields' : ['pub_date'], 'classes' : ['collapse']}),
    ]
    inlines = [ChoiceInLine] 

class QuestionInLine(admin.StackedInline):
    model = Question
    extra = 3

class CategoryAdmin(admin.ModelAdmin):
    """docstring for CategoryAdmin"""
    model = Category
    inlines = [QuestionInLine]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Category, CategoryAdmin)
# admin.site.register(Choice)

