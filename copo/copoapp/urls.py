from django.urls import path
from . import views
urlpatterns = [
     path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
     path("reset-credentials/", views.reset_credentials, name="reset-credentials"),
     path('user-profile/', views.UserProfileView.as_view(), name ='home'),
     path('logout/', views.LogoutView.as_view(), name ='logout'),
     path('register/', views.UserRegistrationView.as_view(), name='register'),
     
     path('get-department/', views.DepartmentView.as_view(), name ='get-department'),
     
     path("add-student/", views.add_student, name="add-student"),
     path("upload-students/", views.upload_student_data, name="upload_students"),
     path("students/edit/<int:student_id>/", views.edit_student, name="edit-student"),
     path('students/<int:student_id>/', views.get_student_details, name='get-student-details'),
     path('students/delete/<int:student_id>/', views.delete_student, name='delete-student'),
     path('students/by-programme/<int:programme_id>/', views.get_students_by_programme, name='get-students-by-programme'),
     path('get-students/', views.get_students_by_programme, name='get-students'),
          
     path("get-level/", views.get_levels, name="get-levels"),
     
     path('add-faculty/', views.FacultyView.as_view(), name ='add-faculty'),
     path("get-faculty/", views.get_faculty, name="get-faculty"),
     path('faculties/edit/<int:faculty_id>/', views.edit_faculty, name='edit-faculty'),
     path('faculties/delete/<int:faculty_id>/', views.delete_faculty, name='delete-faculty'),
     path('faculties/<int:faculty_id>/', views.get_faculty_details, name='get-faculty-details'),
     path("upload-faculty-csv/", views.FacultyCSVUploadView.as_view(), name="upload_faculty_csv"),
     
     path("add-course/", views.CourseView.as_view(), name="add-course"),
     path("courses/edit/<int:course_id>/", views.edit_course, name="edit-course"),
     path("courses/delete/<int:course_id>/", views.delete_course, name="delete-course"),
     path("get-courses/", views.get_courses, name="get-courses"),
     path("courses/<int:course_id>/", views.get_course_details, name="get-course-details"),
     # path("courses/by-programme/<int:programme_id>/", views.get_course_by_programme, name="get-course-by_programme"),
     path('upload-courses/', views.upload_courses_csv, name='upload-courses'),
     
     path('add-batch/', views.add_batch, name='add_batch'),
     path('batches/edit/<int:batch_id>/', views.edit_batch, name='edit_batch'),
     path('batches/delete/<int:batch_id>/', views.delete_batch, name='delete_batch'),
     path('get-batches/', views.get_batches, name='get_batches'),
     path('batches/<int:batch_id>/', views.get_batch_details, name='get_batch_details'),
     
     path("get-programme/", views.get_programmes, name="get-programmes"),
     path('add-programme/', views.ProgrammeView.as_view(), name='add_programme'),
     path('programme/edit/<int:programme_id>/', views.edit_programme, name='edit_programme'),
     path('programmes/delete/<int:programme_id>/', views.delete_programme, name='delete_programme'),
     path('get-programme/', views.get_programmes, name='get_programmes'),
     path('programme/<int:programme_id>/', views.get_programme_details, name='get_programme_details'),
     
     path('add-pos/', views.POView.as_view(), name='add-po'),
     path('pos/edit/<int:po_id>/', views.edit_po, name='edit-po'),
     path('pos/delete/<int:po_id>/', views.delete_po, name='delete-po'),
     path('get-pos/<int:level_id>/', views.get_pos_by_level, name='get-pos-by-level'),
     path('get-pos/', views.get_pos_by_level, name='get-all-pos'),
     path('pos/<int:po_id>/', views.get_po_details, name='get-po-details'),
     
     path('add-cos/',views.COView.as_view(),name="add-co"),
     path('cos/edit/<int:co_id>/',views.edit_co,name="edit-co"),
     path('cos/delete/<int:co_id>/',views.delete_co,name="delete-co"),
     path('get-cos/',views.get_cos,name="get-co"),
     path('cos/<int:co_id>/',views.get_co_details,name="get-co-details"),
     path('cos/by-course/<int:course_id>/',views.get_co_by_course,name="get-co-by-course"),
     
     path('add-pso/', views.PSOView.as_view(), name='add-pso'),
     path('pso/edit/<int:pso_id>/', views.edit_pso, name='edit-pso'),
     path('pso/delete/<int:pso_id>/', views.delete_pso, name='delete-pso'),
     path('get-psos/', views.get_psos, name='get-psos'),
     path('pso/<int:pso_id>/', views.get_pso_details, name='get-pso-details'),
     path('psos/by-programme/<int:programme_id>/', views.get_psos_by_programme, name='get-pso-by-programme'),
     
     path('add-question/', views.AddQuestionView.as_view(), name='add-question'),
     
     path('faculty-batches/', views.get_faculty_batches, name='faculty_batches'),
     
     path('add-internal-exam/', views.InternalExamView.as_view(), name='add_internal_exam'),
     path('get-internal-exams/', views.FacultyInternalExamsView.as_view(), name='get-internal-exam'),
     path("faculty-batches-exams/", views.FacultyBatchesAndExamsView.as_view(), name="faculty-batches-exams"),
     path('question/edit/<int:question_id>/', views.edit_question, name='edit-question'),
     path("question/<int:question_id>/", views.get_question_details, name="get-question-details"),
     path("get-questions/", views.get_questions, name="get-questions"),
     path("question/delete/<int:question_id>/", views.delete_question, name="delete-question"),
     
     path("exam-sections/<int:int_exam_id>/", views.get_exam_sections, name="get_exam_sections"),
     path("add-exam-sections/<int:int_exam_id>/", views.add_exam_section, name="add_exam_section"),
     path("exam-sections/delete/<int:section_id>/", views.delete_exam_section, name="delete_exam_section"),
     path('exam-details/<int:int_exam_id>/', views.get_exam_details, name='get_exam_details'),
     
     path("add-exam-questions/", views.AddExamQuestionsView.as_view(), name="add-exam-questions"),
     path('questions/by-marks/', views.GetQuestionsView.as_view(), name='get-questions-by-marks'),
     
     path('exam/<int:exam_id>/sections/<int:section_id>/questions/', views.get_questions_for_section, name='get_questions_for_section'),
     path('exam-preview/', views.generate_exam_preview, name='exam-preview'),
     path("delete-internal-exam/<int:exam_id>/", views.delete_internal_exam, name="delete-internal-exam"),
     path("exam-sections/update/<int:section_id>/", views.update_exam_section, name="update_exam_section"),
     
     path("upload_pdf/", views.upload_pdf, name="upload_pdf"),
     
     path("dashboard-stats/", views.get_dashboard_stats, name="get_dashboard_stats"),
]
