# exam_management/views.py
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
from django.http import HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView
from rest_framework import generics, permissions
from django.views.decorators.csrf import csrf_exempt
from .models import Exam, Questions, ExamAttempt, Option, ExamCategory
from .serializers import ExamSerializer, QuestionSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from user_management.models import User
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from student_management.models import StudentExam, StudentExamAnswer, Student
from .forms import QuestionsForm, ExamForm, OptionsFormSet, UploadQuestionsForm, StudentExamAttemptForm
from subject_management.models import Topic, SubTopic
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from leaderboard.models import Leaderboard
from django.db.models import Max
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from random import shuffle
from django.core.exceptions import ObjectDoesNotExist
from student_management.forms import StudentExamAnswerForm
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.edit import DeleteView
from datetime import timedelta
from django.db.models import Count, Sum, Q
from io import BytesIO
from django.core.files.base import ContentFile
import pdfplumber
from docx import Document
from .forms import ManualScoreForm
from django.contrib.auth.decorators import permission_required  # or other permission decorators
from .models import ManualScore
from django.core.exceptions import PermissionDenied
from .utils.parsers import parse_word_document
import mammoth
from django.core.files.storage import default_storage
import os
import tempfile

class ExamList(ListView):
    model = Exam
    template_name = 'exam_management/exam_list.html'

    def get_queryset(self):
        category_type = self.kwargs.get('category_type', None)
        if category_type:
            return Exam.objects.filter(category__category_type=category_type, teacher=self.request.user.teacher)
        else:
            return Exam.objects.filter(teacher=self.request.user.teacher)
        
def view_for_years(request, category_type, entity_name):
    # Fetch all categories of the given type and entity
    categories = ExamCategory.objects.filter(category_type=category_type, name=entity_name)

    # Extract distinct years from these categories
    years = categories.order_by('year').values_list('year', flat=True).distinct()

    return render(request, 'exam_management/years_template.html', {
        'category_type': category_type,
        'entity_name': entity_name,
        'years': years
    })

def view_for_exams(request, category_type, entity_name, year):
    # Filter exams based on category type, entity, and year
    exams = Exam.objects.filter(
        category__category_type=category_type, 
        category__name=entity_name, 
        category__year=year, 
        is_published=True
    )

    return render(request, 'exam_management/exams_template.html', {
        'category_type': category_type,
        'entity_name': entity_name,
        'year': year,
        'exams': exams
    })

def view_category_detail(request, category_type):
    # Fetch all unique names under the selected category_type
    details = ExamCategory.objects.filter(category_type=category_type).distinct('name')

    return render(request, 'exam_management/category_detail.html', {
        'category_type': category_type,
        'details': details
    })

class ExamDetail(DetailView):
    model = Exam
    template_name = 'exam_management/exam_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.get_object()
        
        # Fetching related questions and options
        questions_with_options = []
        for question in exam.questions.all():
            options = question.options.all()
            questions_with_options.append({
                'question': question,
                'options': options
            })
        
        context['questions_with_options'] = questions_with_options
        return context


class QuestionList(ListView):
    model = Questions
    template_name = 'exam_management/question_list.html'

    def get_queryset(self):
        # Get the exam id from the URL
        exam_id = self.kwargs['exam_id']
        # Filter the questions by the specific exam
        return Questions.objects.filter(exam__id=exam_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the exam object to display exam details
        exam_id = self.kwargs['exam_id']
        context['exam'] = Exam.objects.get(id=exam_id)
        return context


class QuestionDetail(DetailView):
    model = Questions
    template_name = 'exam_management/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Including the options related to the question in the context
        context['options'] = self.object.options.all()
        return context

class QuestionsList(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Questions.objects.filter(exam__subject__students=self.request.user.student)

class ManageExamView(TemplateView):
    template_name = "exam_management/manage_exam.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = Exam.objects.get(pk=self.kwargs['exam_id'])
        questions_form = QuestionsForm(request=self.request, prefix="questions")
        options_formset = OptionsFormSet(prefix="options", queryset=Option.objects.none())
        context['exam'] = exam
        context['questions_form'] = questions_form
        context['options_formset'] = options_formset
        return context

    def post(self, request, *args, **kwargs):
        exam = Exam.objects.get(pk=self.kwargs['exam_id'])
        
        questions_form = QuestionsForm(request.POST, request.FILES, request=self.request, prefix="questions")
        options_formset = OptionsFormSet(request.POST, prefix="options", queryset=Option.objects.none())
        
        if questions_form.is_valid() and options_formset.is_valid():
            # Your existing logic for saving
            question = questions_form.save(commit=False)
            question.exam = exam
            question.school = exam.school  # set the school to be the same as the school on the exam
            question.save()
            
            options_formset.instance = question
            options_formset.save()
            
            return redirect('exam_management:manage_exam', exam_id=exam.id)
        else:
            # Optionally, you can add the form and formset errors to context and render the same template to display the errors
            context = {
                'questions_form': questions_form,
                'options_formset': options_formset,
                'exam': exam,
            }
            return render(request, self.template_name, context)
            

@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadView(View):

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('exam_management/upload')
        if image_file:
            file_path = default_storage.save('exam_management/uploads/' + image_file.name, image_file)
            image_url = request.build_absolute_uri(default_storage.url(file_path))
            return JsonResponse({'uploaded': 1, 'fileName': image_file.name, 'url': image_url})
        else:
            return JsonResponse({'uploaded': 0, 'error': {'message': 'No image uploaded'}})
    
class UploadQuestionsView(FormView):
    template_name = 'exam_management/upload_csv_questions.html'
    form_class = UploadQuestionsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the logged-in user
        return kwargs

    def form_valid(self, form):
        file = form.cleaned_data['file']
        file_extension = file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            # Handle CSV files
            self.handle_csv(file)
        elif file_extension in ['pdf']:
            # Handle PDF files
            self.handle_pdf(file)
        elif file_extension in ['doc', 'docx']:
            # Handle Word files
            self.handle_docx(file)
        else:
            messages.error(self.request, 'Invalid file format.')
            return redirect('exam_management:upload_questions')

        return redirect('exam_management:manage_exam', exam_id=self.kwargs['exam_id'])
        
    def handle_csv(self, file):
        try:
            exam = Exam.objects.get(pk=self.kwargs['exam_id'])
            subject = exam.subject
            school = exam.school
            csv_text = file.read().decode('utf-8')
            reader = csv.DictReader(csv_text.splitlines())

            expected_headers = [x.strip().lower() for x in [
                'instructions', 'question_text', 'topic_name', 'subtopic_name',
                'option_1', 'is_correct_1', 'option_2', 'is_correct_2',
                'option_3', 'is_correct_3', 'option_4', 'is_correct_4',
                'explanation'
            ]]

            if set(expected_headers) != set([x.strip().lower() for x in reader.fieldnames]):
                messages.error(self.request, 'CSV file has incorrect headers.')
                return

            option_list = []
            with transaction.atomic():
                for row in reader:
                    for header in expected_headers:
                        if not row.get(header, "").strip():
                            messages.error(self.request, f"Row is missing {header}")
                            return

                    topic_name = row['topic_name'].strip()
                    topic, _ = Topic.objects.get_or_create(name=topic_name, subject=subject)

                    subtopic_name = row.get('subtopic_name', "").strip()
                    subtopic, _ = SubTopic.objects.get_or_create(name=subtopic_name, topic=topic) if subtopic_name else (None, False)

                    question = Questions.objects.create(
                        exam=exam,
                        school=school,
                        topic=topic,
                        subtopic=subtopic,
                        question_text=row['question_text'].strip(),
                        instructions=row['instructions'].strip(),
                        explanation=row.get('explanation', "").strip()
                    )

                    for i in range(1, 5):
                        option_text = row[f'option_{i}'].strip()
                        is_correct = row[f'is_correct_{i}'].strip().lower() == 'true'
                        option_list.append(Option(
                            question=question,
                            option_text=option_text,
                            is_correct=is_correct
                        ))

                Option.objects.bulk_create(option_list)

        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return
            
        pass
    
    def handle_pdf(self, file):
        try:
            exam = Exam.objects.get(pk=self.kwargs['exam_id'])
            subject = exam.subject
            school = exam.school
            questions_to_create = []
            options_to_create = []

            with pdfplumber.open(file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.split('\n')
                    instructions = None
                    question_text = None
                    topic_name = None
                    options = []
                    explanation = None

                    with transaction.atomic():
                        for line in lines:
                            if question_text and options:
                                if line.startswith("instruction"):
                                    instructions = line.replace("instruction", "").strip()

                            elif line.startswith(tuple(str(x) + '.' for x in range(1, 1000))):
                                if question_text and options:
                                    topic, _ = Topic.objects.get_or_create(name=topic_name.strip(), subject=subject)
                                    question = Questions(
                                        exam=exam,
                                        school=school,
                                        topic=topic,
                                        question_text=question_text.strip(),
                                        instructions=instructions,
                                        explanation=explanation
                                    )
                                    questions_to_create.append(question)

                                    for opt in options:
                                        opt.question = question
                                        options_to_create.append(opt)

                                    question_text = None
                                    options = []

                                parts = line.split(',')
                                question_number, question_text, topic_name = int(parts[0].split('.')[0]), parts[1], parts[2]
                                options = []

                            elif line.startswith(tuple(str(x) + '.' for x in ['A', 'B', 'C', 'D', 'E'])):
                                parts = line.split(',')
                                option_text = parts[0].split('.')[1].strip()
                                is_correct = parts[1].strip().lower() == 'true'
                                
                                option = Option(
                                    question=None,
                                    option_text=option_text,
                                    is_correct=is_correct
                                )
                                options.append(option)

                            elif line.startswith("explanation"):
                                explanation = line.replace("explanation", "").strip()

                        if questions_to_create:
                            Questions.objects.bulk_create(questions_to_create)
                        
                        if options_to_create:
                            Option.objects.bulk_create(options_to_create)

        except IntegrityError as e:
            messages.error(self.request, f"An integrity error occurred: {str(e)}")
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
        
            pass

    def handle_docx(self, uploaded_file):
        try:
            exam = Exam.objects.get(pk=self.kwargs['exam_id'])
            school = exam.school

            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # Parse the .docx file from the temporary file path
            questions_data = parse_word_document(temp_file_path)
            print("Parsed Questions Data:", questions_data)  # Print parsed questions data

            if not questions_data:
                print("No questions were parsed from the document.")
                messages.warning(self.request, "No questions were parsed from the document.")
                return

            # Save the parsed questions and options to the database
            with transaction.atomic():
                for question_data in questions_data:
                    print("Processing question data:", question_data)  # Print each question data being processed

                    topic_name = question_data.get('topic')
                    subtopic_name = question_data.get('subtopic')

                    # Create or get topic and subtopic instances, only if they are not None
                    topic = None
                    if topic_name:
                        topic, _ = Topic.objects.get_or_create(name=topic_name.strip(), subject=exam.subject)

                    subtopic = None
                    if subtopic_name and topic:
                        subtopic, _ = SubTopic.objects.get_or_create(name=subtopic_name.strip(), topic=topic)

                    # Save question with associated media and options
                    saved_question = Questions.create_from_parsed_data(
                        exam, school, question_data
                    )
                    print("Question saved:", saved_question)  # Print after saving each question

            messages.success(self.request, "Questions successfully uploaded.")

        except Exception as e:
            print("Error occurred:", e)
            messages.error(self.request, f"An error occurred: {str(e)}")
        finally:
            # Delete the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def save_question(self, exam, school, subject, question_data):
        topic_name = question_data.get('topic', '').strip()
        subtopic_name = question_data.get('subtopic', '').strip()

        # Create or get topic and subtopic instances
        topic = None
        if topic_name:
            topic, _ = Topic.objects.get_or_create(name=topic_name, subject=subject)

        subtopic = None
        if subtopic_name and topic:
            subtopic, _ = SubTopic.objects.get_or_create(name=subtopic_name.strip(), topic=topic)

        # Create the question instance
        question = Questions.objects.create(
            exam=exam,
            school=school,
            topic=topic,
            subtopic=subtopic,
            question_text=question_data['text'],
            instructions=question_data.get('instructions', None),
            explanation=question_data.get('explanation', None)
        )

        # Handle options
        for option_data in question_data['options']:
            Option.objects.create(
                question=question,
                option_text=option_data['text'],
                is_correct=option_data['is_correct']
            )
        return question
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = Exam.objects.get(pk=self.kwargs['exam_id'])
        return context
    
class EditExamView(UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exam_management/edit_exam.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse('exam_management:exam-detail', kwargs={'pk': self.object.pk})
   
class EditQuestionView(UpdateView):
    model = Questions
    form_class = QuestionsForm
    template_name = 'exam_management/edit_question.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse('exam_management:question-detail', kwargs={'pk': self.object.pk})
    

class DeleteQuestionView(DeleteView):
    model = Questions
    template_name = 'exam_management/delete_question.html'

    def get_success_url(self):
        exam_id = self.object.exam.id
        return reverse_lazy('exam_management:question-list', kwargs={'exam_id': exam_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.object.exam
        return context

class PublishExamView(View):
    def get(self, request, *args, **kwargs):
        exam_id = kwargs.get('exam_id')
        exam = get_object_or_404(Exam, pk=exam_id)

        # Change the publication status
        exam.is_published = not exam.is_published
        exam.save()

        return redirect('exam_management:exam-detail', pk=exam_id)  # Redirect to the exam detail page

class StudentExamStartView(View):
    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(pk=exam_id)
        except Exam.DoesNotExist:
            return HttpResponse("Exam not found", status=404)

        # Check if the user is a student or if the exam is global
        user = User.objects.get(username=request.user.username)
        if user.role == 'IL':
            # Handle Independent Learner
            student, _ = Student.objects.get_or_create(user=request.user, is_independent_learner=True)
        else:
            try:
                student = Student.objects.get(user=request.user)
            except Student.DoesNotExist:
                student = None

        # Check if the student is allowed to take the exam or if it's a global exam
        if student or exam.is_global:
            student_exam, _ = StudentExam.objects.get_or_create(student=student if student else None, exam=exam)
            exam_attempt = ExamAttempt.objects.create(student_exam=student_exam, start_time=timezone.now())
            return redirect('exam_management:attempt_exam_without_index', exam_id=exam_id, attempt_id=exam_attempt.id)
        else:
            return HttpResponse("Access Denied", status=403)
    
class StudentExamAttemptView(View):
    def get(self, request, exam_id, attempt_id, question_index=0):
        # Clear any existing session answers if this is the first question of a new exam attempt.
        if question_index == 0:
            for key in list(request.session.keys()):
                if key.startswith(f'answer_{exam_id}_'):
                    del request.session[key]
        try:
            query_conditions = Q(student_exam__exam__is_global=True) | Q(student_exam__exam_id=exam_id)
            
            if request.user.is_authenticated:
                if request.user.role == 'IL':
                    query_conditions &= Q(student_exam__student__user=request.user, student_exam__student__is_independent_learner=True)
                else:
                    query_conditions &= Q(student_exam__student__user=request.user)

                exam_attempt = ExamAttempt.objects.prefetch_related('questions__options').get(
                    query_conditions,
                    pk=attempt_id
                )
                # Determine if this is a new attempt
                is_new_attempt = question_index == 0 and not any(
                    key.startswith(f'answer_{exam_id}_') for key in request.session.keys()
                )

            questions = exam_attempt.questions.all()
            # Check if there are questions in the exam
            if not questions:
                messages.add_message(request, messages.INFO, "This exam has no questions.")
                return redirect('exam_management:no_questions')  # Use the name of the no_questions URL

            try:
                current_question = questions[int(question_index)]
            except IndexError:
                messages.add_message(request, messages.ERROR, "Invalid question index.")
                return redirect('exam_management:invalid_question_index') 
            is_first_question = int(question_index) == 0
            is_last_question = int(question_index) == len(questions) - 1

            existing_answer_id = request.session.get(f'answer_{exam_id}_{current_question.id}', None)
            request.session.save()
            
            if existing_answer_id:
                existing_answer = Option.objects.get(id=existing_answer_id)
                form = StudentExamAttemptForm(initial={'selected_option': existing_answer}, question=current_question)
            else:
                try:
                    existing_answer = StudentExamAnswer.objects.get(student_exam=exam_attempt.student_exam, question=current_question)
                    form = StudentExamAttemptForm(instance=existing_answer, question=current_question)
                except StudentExamAnswer.DoesNotExist:
                    form = StudentExamAttemptForm(question=current_question)

            # Fetching the duration (as a timedelta) and start time
            duration = exam_attempt.student_exam.exam.duration if exam_attempt.student_exam else None
            start_time = exam_attempt.start_time

            # Calculating the time remaining
            time_elapsed = timezone.now() - start_time
            time_remaining = duration - time_elapsed if duration else None

            # Converting to seconds for easier handling in the frontend
            time_remaining_seconds = time_remaining.total_seconds() if time_remaining else None

            # Convert remaining time to minutes for front-end
            remaining_minutes = int(time_remaining_seconds // 60) if time_remaining_seconds else None

            # Count unanswered questions
            total_questions = questions.count()
            answered_questions = 0
            for question in questions:
                if request.session.get(f'answer_{exam_id}_{question.id}', None):
                    answered_questions += 1
            unanswered_questions_count = total_questions - answered_questions

            # Update context to include new variables
            context = {
                'form': form,
                'time_remaining': time_remaining_seconds,
                'remaining_minutes': remaining_minutes,
                'unanswered_questions_count': unanswered_questions_count,
                'questions': questions,
                'current_question': current_question,
                'attempt_id': attempt_id,
                'is_new_attempt': is_new_attempt,
                'exam_id': exam_id,
                'question_index': question_index,
                'is_first_question': is_first_question,
                'is_last_question': is_last_question,
            }
            
            return render(request, 'exam_management/exam_attempt.html', context)
        except ExamAttempt.DoesNotExist:
            return HttpResponse("Exam attempt does not exist", status=404)

    def post(self, request, exam_id, attempt_id, question_index=0):
        exam_attempt = ExamAttempt.objects.get(pk=attempt_id, student_exam__exam_id=exam_id)
        
        # Check for the auto_submit flag
        auto_submit = request.POST.get('auto_submit', 'false') == 'true'

        if auto_submit:
            # Logic for handling automatic submission
            # Process any stored answers in the session, mark the exam as complete, etc.
            # ...
            return redirect('exam_management:view_score', exam_id=exam_id, attempt_id=attempt_id)

        # Existing logic for handling manual question submission
        current_question = exam_attempt.questions.all()[int(question_index)]
        form = StudentExamAttemptForm(request.POST, question=current_question)

        if form.is_valid():
            selected_option = form.cleaned_data['selected_option']
            if selected_option:
                request.session[f'answer_{exam_id}_{current_question.id}'] = selected_option.id
                request.session.save()

        next_question_index = int(question_index) + 1
        if next_question_index > exam_attempt.questions.count() - 1:
            exam_attempt.current_question_index = next_question_index
            if exam_attempt.student_exam:
                exam_attempt.complete_attempt(request)  # Pass request object here

                # Clear the session data here
                for key in list(request.session.keys()):
                    if key.startswith('answer_'):
                        del request.session[key]

                return redirect('exam_management:view_score', exam_id=exam_id, attempt_id=attempt_id)
            else:
                return redirect('exam_management:global_exam_complete')

        return redirect('exam_management:attempt_exam', exam_id=exam_id, attempt_id=attempt_id, question_index=next_question_index)

def no_questions_view(request):
    # Render a template or return a simple HttpResponse for the no questions scenario
    return render(request, 'exam_management/no_questions.html')

def invalid_question_index_view(request):
    # Render a template or return a simple HttpResponse for the invalid question index scenario
    return render(request, 'exam_management/invalid_question_index.html')

class StudentExamScoreView(View):
    def get(self, request, exam_id, attempt_id):  # Include attempt_id here
        exam_attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student_exam__student__user=request.user, student_exam__exam_id=exam_id)
        raw_score, percentage_score = exam_attempt.calculate_score()

        # Update leaderboard
        self.update_leaderboard(exam_attempt.student_exam, raw_score)

        # Add exam_id and attempt_id to the context
        context = {
            'score': raw_score,
            'percentage_score': percentage_score,
            'exam_id': exam_id,  # Add this line
            'attempt_id': attempt_id,  # Add this line
        }

        return render(request, 'exam_management/exam_score.html', context)
    def update_leaderboard(self, student_exam, score):
        subject = student_exam.exam.subject

        # Classroom might be None for Independent Learners
        classroom = student_exam.student.enrolled_class if hasattr(student_exam.student, 'enrolled_class') else None

        leaderboard_entry, created = Leaderboard.objects.get_or_create(
            student=student_exam.student,
            subject=subject,
            classroom=classroom,  # This might be None
            defaults={'score': score}
        )

        if not created and score > leaderboard_entry.score:
            leaderboard_entry.score = score
            leaderboard_entry.save()

        # After updating the score, update the ranks for all Leaderboard entries for this subject and class
        self.update_ranks(subject, classroom)

    def update_ranks(self, subject, classroom):
        # Get all Leaderboard entries for this subject and class, ordered by score
        leaderboard_entries = Leaderboard.objects.filter(
            subject=subject,
            classroom=classroom
        ).order_by('-score')

        # Loop through the entries and update their rank
        for i, entry in enumerate(leaderboard_entries):
            entry.rank = i + 1  # rank should start at 1, not 0
            entry.save()

class GlobalExamCompleteView(View):
    def get(self, request):
        # You can include any context data if needed
        return render(request, 'exam_management/global_exam_complete.html')
    
class StudentExamAnalysisView(View):
    def get(self, request, exam_id, attempt_id):
        try:
            exam_attempt = ExamAttempt.objects.select_related('student_exam').get(pk=attempt_id, student_exam__exam_id=exam_id)
        except ExamAttempt.DoesNotExist:
            raise Http404("Exam Attempt not found.")
        
        try:
            context = generate_exam_analysis(exam_attempt)
        except Exception as e:
            context = {'error': 'An unexpected error occurred while generating the analysis.'}

        return render(request, 'exam_management/exam_analysis.html', context)

def generate_exam_analysis(exam_attempt):
    questions = exam_attempt.questions.select_related('topic', 'subtopic').prefetch_related('options').all()
    student_exam_answers = StudentExamAnswer.objects.filter(student_exam=exam_attempt.student_exam)

    topic_weaknesses = {}
    topic_scores = {}
    detailed_answers = []
    errors = []  # Collect errors here

    for question in questions:
        # Check if question.topic exists
        topic_name = question.topic.name if question.topic else "Others"
        
        try:
            answer = student_exam_answers.get(question=question)
        except StudentExamAnswer.DoesNotExist:
            answer = None
        except StudentExamAnswer.MultipleObjectsReturned:
            errors.append(f"Multiple answers found for question ID {question.id}")
            continue

        is_correct = answer.student_answer.is_correct if answer else False
        # Use topic_name variable instead of direct access
        topic_weaknesses[topic_name] = topic_weaknesses.get(topic_name, 0) + int(not is_correct)

        try:
            correct_option = question.options.get(is_correct=True)
        except Option.DoesNotExist:
            correct_option = None
            errors.append(f"No correct option found for question ID {question.id}")

        detailed_answers.append({
            'question': question,
            'student_answer': answer.student_answer.option_text if answer and answer.student_answer else "Not answered",
            'correct_answer': correct_option.option_text if correct_option else "Not available",
            'explanation': question.explanation
        })

        # Again, using topic_name for consistency
        topic_scores[topic_name] = topic_scores.get(topic_name, 0) + int(is_correct)

    topic_percentage_scores = {}
    for topic, score in topic_scores.items():
        # Use filter on topic_name to safely handle "Unknown Topic"
        total_questions = questions.filter(topic__name=topic).count() if topic != "Others" else 0
        topic_percentage_scores[topic] = (score / total_questions) * 100 if total_questions else 0

    raw_score, percentage_score = exam_attempt.calculate_score()

    return {
        'topic_weaknesses': topic_weaknesses,
        'topic_scores': topic_scores,
        'topic_percentage_scores': topic_percentage_scores,
        'raw_score': raw_score,
        'percentage_score': percentage_score,
        'detailed_answers': detailed_answers,
        'errors': errors
    }


#Manual score entry view
@login_required
def enter_manual_score(request):
    if not hasattr(request.user, 'teacher'):
        raise PermissionDenied("You do not have permission to enter manual scores.")

    if request.method == 'POST':
        form = ManualScoreForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            subject = form.cleaned_data['subject']
            date_assigned = form.cleaned_data['date_assigned']

            # Try to get an existing record
            existing_score = ManualScore.objects.filter(
                student=student, 
                subject=subject, 
                date_assigned=date_assigned
            ).first()

            if existing_score:
                # Update existing record
                existing_score.ca1_score = form.cleaned_data.get('ca1_score')
                existing_score.ca2_score = form.cleaned_data.get('ca2_score')
                existing_score.exam_score = form.cleaned_data.get('exam_score')
                # If total score is provided, use it, otherwise recalculate
                existing_score.total_score = form.cleaned_data.get('total_score') or sum(
                    filter(None, [existing_score.ca1_score, existing_score.ca2_score, existing_score.exam_score])
                )
                existing_score.save()
            else:
                # Create a new record
                new_score = form.save(commit=False)
                new_score.save()

            return redirect('exam_management:manual_score_success')
        else:
            print("Form errors:", form.errors)  # For debugging
    else:
        form = ManualScoreForm()

    return render(request, 'exam_management/manual_score_entry.html', {'form': form})