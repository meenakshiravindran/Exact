from django.contrib import admin

# Register your models here.
from .models import Student, Programme, Course,PO
admin.site.register(Student)
admin.site.register(Programme)
admin.site.register(Course)
admin.site.register(POs)
admin.site.register(COs)
admin.site.register(PSOs)
admin.site.register()
admin.site.register(COAttainment)