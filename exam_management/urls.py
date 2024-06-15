# exam_management/urls.py

from django.urls import path
from . import views
from django.views.generic.base import TemplateView
from .views import DeleteQuestionView, StudentExamStartView, StudentExamAttemptView, StudentExamScoreView, GlobalExamCompleteView, StudentExamAnalysisView, enter_manual_score, view_for_years, view_for_exams, ImageUploadView

app_name = 'exam_management'

urlpatterns = [
    path('exams/<category_type>/', views.ExamList.as_view(), name='exam_list_by_category'),
    path('exams/years/<category_type>/<entity_name>/', views.view_for_years, name='view_for_years'),
    path('exams/<category_type>/<entity_name>/<int:year>/', view_for_exams, name='view_for_exams'),
    path('category/<category_type>/', views.view_category_detail, name='view_category_detail'),
    path('exams/<int:pk>/', views.ExamDetail.as_view(), name='exam-detail'),
    path('exams/<int:exam_id>/questions/', views.QuestionList.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionDetail.as_view(), name='question-detail'),
    path('exams/<int:exam_id>/manage', views.ManageExamView.as_view(), name='manage_exam'),
    path('ckeditor/upload/', ImageUploadView.as_view(), name='ckeditor_upload'),
    path('exams/<int:exam_id>/upload-csv', views.UploadQuestionsView.as_view(), name='upload_csv_questions'),
    path('questions/<int:pk>/edit', views.EditQuestionView.as_view(), name='edit_question'),
    path('exams/<int:pk>/edit', views.EditExamView.as_view(), name='edit_exam'),
    path('questions/<int:pk>/delete/', DeleteQuestionView.as_view(), name='question-delete'),
    path('exams/<int:exam_id>/publish', views.PublishExamView.as_view(), name='publish_exam'),
    path('start_exam/<int:exam_id>/', StudentExamStartView.as_view(), name='start_exam'),
    path('exam/no_questions/', views.no_questions_view, name='no_questions'),
    path('exam/invalid_question_index/', views.invalid_question_index_view, name='invalid_question_index'),
    path('global_exam_complete/', GlobalExamCompleteView.as_view(), name='global_exam_complete'),
    path('attempt_exam/<int:exam_id>/<int:attempt_id>/', StudentExamAttemptView.as_view(), name='attempt_exam_without_index'),
    path('attempt_exam/<int:exam_id>/<int:attempt_id>/<int:question_index>/', StudentExamAttemptView.as_view(), name='attempt_exam'),
    path('view_score/<int:exam_id>/<int:attempt_id>/', StudentExamScoreView.as_view(), name='view_score'),
    path('exam_analysis/<int:exam_id>/<int:attempt_id>/', StudentExamAnalysisView.as_view(), name='exam_analysis'),
    path('enter_manual_score/', enter_manual_score, name='enter_manual_score'),
    path('manual_score_success/', TemplateView.as_view(template_name='exam_management/manual_score_success.html'), name='manual_score_success'),
]
