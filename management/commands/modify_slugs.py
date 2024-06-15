# from django.core.management.base import BaseCommand
# from django.utils.text import slugify
# from resource.models import Blog

# class Command(BaseCommand):
#     help = 'Modify existing slugs to make them unique'

#     def handle(self, *args, **kwargs):
#         blogs = Blog.objects.all()
#         seen_slugs = set()

#         for blog in blogs:
#             slug = blog.slug
#             new_slug = slug
#             count = 1

#             while new_slug in seen_slugs:
#                 new_slug = f"{slug}-{count}"
#                 count += 1

#             blog.slug = new_slug
#             blog.save()
#             seen_slugs.add(new_slug)
#             self.stdout.write(self.style.SUCCESS(f'Successfully updated slug for "{blog.name}"'))

