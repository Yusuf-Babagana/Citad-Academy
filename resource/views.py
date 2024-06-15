from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.views import View, generic
from django.utils.text import slugify
from .models import Resource, ResourceComment
from .forms import ContactForm
from .forms import ResourceCommentForm
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView






class ResourceListView(generic.ListView):
    model = Resource
    template_name = 'resources/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 10
    queryset = Resource.objects.all().order_by('-timestamp')



class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'resources/resource_detail.html'
    context_object_name = 'resource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.get_object()
        context['comments'] = ResourceComment.objects.filter(resource=resource).order_by('-created_at')
        # Corrected: Use self.request to access the request object
        context['comment_form'] = ResourceCommentForm(initial={'user': self.request.user if self.request.user.is_authenticated else None})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Ensure the detail object is available for re-rendering the page
        form = ResourceCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.resource = self.object
            if request.user.is_authenticated:
                comment.user = request.user
            # No need to handle anonymous differently here unless you're capturing more fields
            comment.save()
            messages.success(request, 'Your comment has been posted.')
        else:
            messages.error(request, 'There was an error with your comment.')

        context = self.get_context_data()
        context['comment_form'] = form  # Include the form with errors
        return self.render_to_response(context)
    
    
def download_resource(request, slug):
    resource = get_object_or_404(Resource, slug=slug)
    file_path = resource.file.path
    response = FileResponse(open(file_path, 'rb'))
    return response

class ContactView(generic.FormView):
    template_name = "resources/contact.html"
    form_class = ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Thank you. We will be in touch soon.')
        return super().form_valid(form)
