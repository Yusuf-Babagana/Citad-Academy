# iexam/urls.py
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include([
        path('api/user_management/', include(('user_management.api_urls', 'user_management_api'), namespace='user_management_api')),
        path('api/school_management/', include(('school_management.api_urls', 'school_management_api'), namespace='school_management_api')),
        path('api/class_management/', include(('class_management.api_urls', 'class_management_api'), namespace='class_management_api')),
        path('api/subject_management/', include(('subject_management.api_urls', 'subject_management_api'), namespace='subject_management_api')),
        path('api/exam_management/', include(('exam_management.api_urls', 'exam_management_api'), namespace='exam_management_api')),
        path('api/student_management/', include(('student_management.api_urls', 'student_management_api'), namespace='student_management_api')),
        path('api/performance_tracking/', include(('performance_tracking.api_urls', 'performance_tracking_api'), namespace='performance_tracking_api')),
        path('api/leaderboard/', include(('leaderboard.api_urls', 'leaderboard_api'), namespace='leaderboard_api')),
        path('api/media_management/', include(('media_management.api_urls', 'media_management_api'), namespace='media_management_api')),
        path('api/payments/', include('payments.api_urls')),
        path('api/subscription/', include('subscription.api_urls')),
    ])),
    path('resource/', include('resource.urls', namespace='resource')),
    path('', include('user_management.urls', namespace='user_management_web')),
    path('class_management/', include('class_management.urls', namespace='class_management_web')),
    path('user_management/', include(('user_management.urls', 'user'), namespace='user_web')),
    path('school_management/', include(('school_management.urls', 'school'), namespace='school_web')),
    path('subject_management/', include(('subject_management.urls', 'subject'), namespace='subject_web')),
    path('exam_management/', include(('exam_management.urls', 'exam_management'), namespace='exam_management_web')),
    path('student_management/', include(('student_management.urls', 'student'), namespace='student_web')),
    path('performance_tracking/', include(('performance_tracking.urls', 'performance_tracking'), namespace='performance_tracking_web')),
    path('leaderboard/', include(('leaderboard.urls', 'leaderboard'), namespace='leaderboard_web')),
    path('media_management/', include(('media_management.urls', 'media_management'), namespace='media_management_web')),
    path('payments/', include('payments.urls')),
    path('subscription/', include('subscription.urls')),
    path('markdownx/', include('markdownx.urls')),
    path('tinymce/', include('tinymce.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
