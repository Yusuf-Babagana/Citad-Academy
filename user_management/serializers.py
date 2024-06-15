# serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from school_management.models import School, SchoolAdmin
from .models import User
from school_management.models import School, SchoolAdmin
from class_management.models import Class, Teacher
from student_management.models import Student, SubjectCombination, EnrollmentRequest
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class SchoolAdminRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    school_name = serializers.CharField(write_only=True)
    school_address = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password_confirm', 
            'first_name', 'last_name', 'school_name', 'school_address', 
            'profile_image'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'profile_image': {'required': False},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        school_name = validated_data.pop('school_name')
        school_address = validated_data.pop('school_address')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='SA'
        )
        # Set the trial period for the user
        user.trial_start_date = timezone.now()
        user.trial_end_date = timezone.now() + timedelta(days=7)
        
        if 'profile_image' in validated_data:
            user.profile_image = validated_data['profile_image']
        user.save()

        # Additional logic to handle creating School and SchoolAdmin
        school = School.objects.create(
            name=school_name, 
            address=school_address
        )
        SchoolAdmin.objects.create(user=user, school=school)
        
        return user
    
class UserProfileImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']

    def save(self, **kwargs):
        user = super().save(**kwargs)
        # Perform any additional operations here if necessary
        return user

class TeacherRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    field_of_study = serializers.CharField(max_length=100)
    # Removed school from fields as it will be inferred from the logged-in user's school.
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'field_of_study', 'profile_image')
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'profile_image': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords don't match."})
        return data

    def create(self, validated_data, request):
        # Inferring school from the logged-in user (SchoolAdmin)
        school_admin = SchoolAdmin.objects.get(user=request.user)
        validated_data['school'] = school_admin.school
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='T',
            school=validated_data['school']  # Set the school here
        )
        if validated_data.get('profile_image'):
            user.profile_image = validated_data['profile_image']
        user.save()

        Teacher.objects.create(
            user=user, 
            field_of_study=validated_data['field_of_study']
        )
        
        # Assuming that the EnrollmentRequest model requires a school and teacher
        EnrollmentRequest.objects.create(teacher=user.teacher, school=validated_data['school'])

        return user

class StudentRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class_name = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), source='class_name.id', write_only=True
    )
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all())
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'school', 'class_name', 'profile_image')
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'profile_image': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_class_name(self, value):
        school_id = self.initial_data.get('school')
        if not Class.objects.filter(id=value.id, school_id=school_id).exists():
            raise serializers.ValidationError("Class does not exist in the given school.")
        return value

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords don't match."})
        return data

    def create(self, validated_data):
        class_name = validated_data.pop('class_name')['id']
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='S'
        )
        # Set the trial period for the user
        user.trial_start_date = timezone.now()
        user.trial_end_date = timezone.now() + timedelta(days=7)

        if validated_data.get('profile_image'):
            user.profile_image = validated_data['profile_image']
        user.save()

        selected_class = Class.objects.get(id=class_name)
        student = Student.objects.create(user=user, class_name=selected_class)
        
        # Note: The following line assumes that the SubjectCombination and
        # EnrollmentRequest models do not require additional mandatory fields.
        # If they do, you'll need to provide the required fields as arguments.
        SubjectCombination.objects.create(student=student)
        EnrollmentRequest.objects.create(student=student, school=user.school)
        
        return user

class IndependentLearnerRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'profile_image')
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'profile_image': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords don't match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='IL'  # Independent Learner
        )
        # Set the trial period for the user
        user.trial_start_date = timezone.now()
        user.trial_end_date = timezone.now() + timedelta(days=7)

        if validated_data.get('profile_image'):
            user.profile_image = validated_data['profile_image']
        user.save()

        return user

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

class CustomAuthSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username/Email", write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)

    def validate(self, data):
        username_or_email = data.get('username').lower()
        password = data.get('password')

        # If it looks like an email address, look up the username
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                username_or_email = user.username
            except User.DoesNotExist:
                raise AuthenticationFailed('Invalid username/email or password.')

        user = authenticate(request=self.context.get('request'), username=username_or_email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid username/email or password.')

        data['user'] = user
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    subscription_type = serializers.CharField(source='subscription.subscription_type', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'school_name', 'subscription_type', 'subscription_expiry_date', 'has_paid_subscription', 'profile_image']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_image']
        extra_kwargs = {'email': {'required': True}}
    
    def validate_email(self, value):
        instance = self.instance
        if User.objects.exclude(pk=instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']

    def validate_role(self, value):
        if value not in dict(User.ROLE_CHOICES).keys():
            raise serializers.ValidationError("Invalid role selected.")
        return value
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role

        return token