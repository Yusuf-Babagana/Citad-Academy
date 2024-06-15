# user_management/forms.py
from django import forms
from .models import User
from school_management.models import School, SchoolAdmin
from class_management.models import Class, Teacher
from student_management.models import Student, SubjectCombination, EnrollmentRequest
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()

# form for School Admin
class SchoolAdminRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text="Password must contain at least 8 characters, numbers, and both lowercase and uppercase letters."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    school_name = forms.CharField(
        max_length=255,
        validators=[RegexValidator(r'^[a-zA-Z\s\'\-]+$', 'Enter a valid school name. Only letters, spaces, dashes, and apostrophes are allowed.')],
        help_text='Enter the school name. Only letters, spaces, dashes, and apostrophes are allowed.'
    )
    school_address = forms.CharField(
        max_length=255,
        validators=[RegexValidator(r'^[a-zA-Z0-9\s,.-]+$', 'Enter a valid address. Only letters, numbers, spaces, commas, periods, and hyphens are allowed.')],
        help_text='Enter the school address. Only letters, numbers, spaces, commas, periods, and hyphens are allowed.'
    )
    email = forms.EmailField(validators=[EmailValidator()])  # Email validation
    profile_image = forms.ImageField(
        required=False,  # Make it optional
        help_text='Optional: Upload a profile picture.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'school_name', 'school_address', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
            # ... other widgets ...
        }

    def clean_school_name(self):
        school_name = self.cleaned_data.get('school_name')
        if School.objects.filter(name__iexact=school_name).exists():
            raise ValidationError("A school with this name already exists.")
        return school_name

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Check if the email already exists.
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'SA'
        user.set_password(self.cleaned_data['password'])
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        
        if commit:
            user.save()
            school = School.objects.create(name=self.cleaned_data['school_name'], address=self.cleaned_data['school_address'])
            SchoolAdmin.objects.create(user=user, school=school)
        return user

class TeacherRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text="Password must contain at least 8 characters, numbers, and both lowercase and uppercase letters."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    school = forms.ModelChoiceField(queryset=School.objects.all())
    field_of_study = forms.CharField(
        max_length=100,
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Enter a valid field of study. Only letters and spaces are allowed.')],
        label='Field of Study',
        help_text='Enter the field of study. Only letters and spaces are allowed.',
        required=True
    )
    email = forms.EmailField(validators=[EmailValidator()])  # Email validation
    profile_image = forms.ImageField(
        required=False,
        help_text='Optional: Upload a profile picture.'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'school', 'field_of_study', 'profile_image']

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        self.fields['school'].widget.attrs['readonly'] = True
        if school:
            self.fields['school'].initial = school
            self.fields['school'].queryset = School.objects.filter(id=school.id)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Check if the email already exists.
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'T'
        user.set_password(self.cleaned_data['password'])
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        
        if commit:
            user.save()
            # Extract the field of study and create a Teacher instance
            field_of_study = self.cleaned_data['field_of_study']
            teacher = Teacher.objects.create(user=user, field_of_study=field_of_study)
            # If you need to create an EnrollmentRequest, you can do so here
            EnrollmentRequest.objects.create(teacher=teacher, school=user.school)
        return user

class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text="Password must contain at least 8 characters, numbers, and both lowercase and uppercase letters."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=True)
    class_name = forms.ChoiceField(choices=[])  # Empty initial choices
    email = forms.EmailField(validators=[EmailValidator()])
    profile_image = forms.ImageField(
        required=False,
        help_text='Optional: Upload a profile picture.'
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'school', 'class_name', 'profile_image'
        ]
    def __init__(self, *args, **kwargs):
        super(StudentRegisterForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'school' in kwargs['initial']:
            school = kwargs['initial']['school']
            self.fields['class_name'].choices = [(c.id, c.name) for c in Class.objects.filter(school=school)]
        

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        school = cleaned_data.get('school')
        class_name = cleaned_data.get('class_name')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        # Update choices for 'class_name' dynamically based on the selected school
        if school:
            self.fields['class_name'].choices = [(c.id, c.name) for c in Class.objects.filter(school=school)]
        else:
            raise forms.ValidationError("School must be provided for students.")

        # Validate if the class_name is a valid choice
        if class_name and not any(class_name in str(choice[0]) for choice in self.fields['class_name'].choices):
            raise forms.ValidationError(f"Select a valid choice. {class_name} is not one of the available choices.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'S'
        user.set_password(self.cleaned_data['password'])
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']

        
        try:
            selected_class = Class.objects.get(id=self.cleaned_data['class_name'])
        except Class.DoesNotExist:
            selected_class = None

        if commit:
            user.save()
            student = Student.objects.create(user=user, class_name=selected_class)  # Save the Class object
            SubjectCombination.objects.create(student=student)
            EnrollmentRequest.objects.create(student=student, school=user.school)
        return user

class IndependentLearnerRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text="Password must contain at least 8 characters, numbers, and both lowercase and uppercase letters."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    email = forms.EmailField(validators=[EmailValidator()])  # Email validation
    profile_image = forms.ImageField(
        required=False,
        help_text='Optional: Upload a profile picture.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'profile_image']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Check if the email already exists.
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'IL'  # Assuming 'IL' represents Independent Learner
        user.set_password(self.cleaned_data['password'])
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        
        if commit:
            user.save()
        return user

# form for Admin
class AdminRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text="Password must contain at least 8 characters, numbers, and both lowercase and uppercase letters."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'A'
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username/Email", max_length=254)

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email:
            username_or_email = username_or_email.lower()

            # If it looks like an email address, look up the username
            if '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    username_or_email = user.username
                except User.DoesNotExist:
                    pass  # We'll show an invalid login error later
            
            self.cleaned_data['username'] = username_or_email

        return super().clean()
    
class ProfileImageUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']