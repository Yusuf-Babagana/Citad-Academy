from django.urls import path
from . import views

app_name = 'exam_management'

urlpatterns = [
    path('exams/', views.ExamList.as_view(), name='exams_list'),
    path('exams/<int:pk>/', views.ExamDetail.as_view(), name='exams_detail'),
    path('questions/', views.QuestionList.as_view(), name='questions_list'),
    path('questions/<int:pk>/', views.QuestionDetail.as_view(), name='questions_detail'),
  

]





from django.urls import path
from . import api_views

urlpatterns = [
    path('exam-categories/', api_views.ExamCategoryListView.as_view(), name='exam-category-list'),
    path('exam-categories/<int:pk>/', api_views.ExamCategoryDetailView.as_view(), name='exam-category-detail'),
    path('exams/', api_views.ExamListView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', api_views.ExamDetailView.as_view(), name='exam-detail'),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'questions', api_views.QuestionsViewSet)
router.register(r'options', api_views.OptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ExamAttemptViewSet

router = DefaultRouter()
router.register(r'exam-attempts', ExamAttemptViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path
from .api_views import ManualScoreListView, ManualScoreDetailView

urlpatterns += [
    path('manual-scores/', ManualScoreListView.as_view(), name='manual-score-list'),
    path('manual-scores/<int:pk>/', ManualScoreDetailView.as_view(), name='manual-score-detail'),
]
