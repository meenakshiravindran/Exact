from django.urls import path
from . import views
urlpatterns = [
     path('home/', views.HomeView.as_view(), name ='home'),
     path('logout/', views.LogoutView.as_view(), name ='logout'),
     path('add-faculty/', views.FacultyView.as_view(), name ='add-faculty'),
     path('get-department/', views.DepartmentView.as_view(), name ='get-department'),
     path("add-student/", views.add_student, name="add-student"),
     path("get-programme/", views.get_programmes, name="get-programmes"),
     path("get-level/", views.get_levels, name="get-levels"),
     path("add-programme/", views.add_programme, name="add-programme"),
     path("add-course/", views.add_course, name="add-course"),
     path("get-faculty/", views.get_faculty, name="get-faculty"),
     path("get-courses/", views.get_courses, name="get-ourses"),
     path("add-batch/", views.add_batch, name="add-batch"),
     path('faculties/edit/<int:faculty_id>/', views.edit_faculty, name='edit-faculty'),
     path('faculties/delete/<int:faculty_id>/', views.delete_faculty, name='delete-faculty'),
     path('faculties/<int:faculty_id>/', views.get_faculty_details, name='get-faculty-details'),
]