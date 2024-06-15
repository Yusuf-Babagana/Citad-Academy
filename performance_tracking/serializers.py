# serializers.py
from rest_framework import serializers
from .models import Performance

class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ['id', 'student', 'subject', 'score']


from rest_framework import serializers
from .models import Performance, AttendanceRecord, ExtraCurricularActivity, ReportCard

class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class ExtraCurricularActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraCurricularActivity
        fields = '__all__'

class ReportCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = '__all__'
