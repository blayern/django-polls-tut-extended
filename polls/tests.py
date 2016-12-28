from django.test import TestCase
from django.test import Client

import datetime
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice

def create_question(question_text, days):
    time = timezone.now() - datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

# Create your tests
class IndexViewTests(TestCase):
    def test_with_no_questions(self):
        """view MUST show msg when there are no questions"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_with_old_question(self):
        create_question(question_text="old_question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                    ['<Question: old_question>'])

    def test_with_five_old_questions(self):
        """view MUST show all five questions and sort them by -pub_date"""
        create_question(question_text='old_question_1', days=1)
        create_question(question_text='old_question_2', days=2)
        create_question(question_text='old_question_3', days=5)
        create_question(question_text='old_question_4', days=4)
        create_question(question_text='old_question_5', days=3)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
            ['<Question: old_question_1>', 
            '<Question: old_question_2>',
            '<Question: old_question_5>',
            '<Question: old_question_4>',
            '<Question: old_question_3>'])

    def test_with_six_old_questions(self):
        """view MUST show five questions and sort them by -pub_date"""
        create_question(question_text='old_question_1', days=1)
        create_question(question_text='old_question_2', days=6)
        create_question(question_text='old_question_3', days=5)
        create_question(question_text='old_question_4', days=4)
        create_question(question_text='old_question_5', days=3)
        create_question(question_text='old_question_6', days=2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
            ['<Question: old_question_1>', 
            '<Question: old_question_6>',
            '<Question: old_question_5>',
            '<Question: old_question_4>',
            '<Question: old_question_3>'])

    def test_with_future_question(self):
        create_question(question_text="future_question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_with_future_and_old_question(self):
        create_question(question_text="future_question", days=-30)
        create_question(question_text="old_question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                    ['<Question: old_question>'])

class DetailViewTests(TestCase):
    def test_with_no_added_questions(self):
        """view MUST return 404 on invalid question.id"""
        response = self.client.get(reverse('polls:detail', args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_with_no_added_choices(self):
        question = create_question(question_text="question_1", days=0)
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, 'No Answers')

    def test_with_one_added_choice(self):
        question = create_question(question_text="question_1", days=0)
        choice = question.choice_set.create(choice_text="choice 1", votes=0) 
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, 'choice 1')

    def test_with_multiple_added_choice(self):
        question = create_question(question_text="question_1", days=0)
        question.choice_set.create(choice_text="choice 1", votes=0) 
        question.choice_set.create(choice_text="choice 2", votes=0) 
        question.choice_set.create(choice_text="choice 3", votes=0) 
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)
        self.assertContains(response, 'choice 1')
        self.assertContains(response, 'choice 2')
        self.assertContains(response, 'choice 3')

class QuestionMethodTest(TestCase):
    def test_was_published_recently_for_question_with_old_date(self):
        """was_published_recently()
        MUST retrun False for question with date > 1 day from now"""
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently()
        MUST return True for question within a day"""
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_future_date(self):
        """was_published_recently()
        MUST return False for question with future date"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)    

    def test_get_most_popular_choice_with_no_choices(self):
        question = create_question(question_text="qestion_1", days=0)
        choice = question.get_most_popular_choice()
        self.assertQuerysetEqual(choice, [])

    def test_get_most_popular_choice_with_multiple_choices(self):
        question = create_question(question_text="qestion_1", days=0)
        question.choice_set.create(choice_text="choice_1", votes=1)
        question.choice_set.create(choice_text="choice_2", votes=2)
        question.choice_set.create(choice_text="choice_3", votes=4)
        question.choice_set.create(choice_text="choice_4", votes=3)
        choice = question.get_most_popular_choice()
        self.assertQuerysetEqual(choice, ['<Choice: choice_3>'])
