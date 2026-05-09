from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:attempt_id>/<int:question_index>/', views.play_quiz, name='play_quiz'),
    path('quiz/<int:attempt_id>/<int:question_index>/submit/', views.submit_answer, name='submit_answer'),
    path('quiz/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:attempt_id>/<int:question_index>/quit/', views.quit_quiz, name='quit_quiz'),
]
