from django.contrib import admin
from .models import Student, StudentExam, StudentExamAnswer, EnrollmentRequest, SubjectCombination, StudentPerformance, StudentActivity, BehavioralAssessment  # Add your model names here

admin.site.register(Student)
admin.site.register(StudentExam)
admin.site.register(StudentExamAnswer)
admin.site.register(EnrollmentRequest)
admin.site.register(SubjectCombination)
admin.site.register(StudentPerformance)
admin.site.register(StudentActivity)
admin.site.register(BehavioralAssessment)