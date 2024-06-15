# user_management/context_processors.py
from school_management.models import School

def add_school_to_context(request):
    school_id = request.session.get('school_id')
    school = School.objects.get(id=school_id) if school_id else None
    return {'school': school}
