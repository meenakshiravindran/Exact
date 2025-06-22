from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, LevelViewSet, ProgrammeViewSet, CourseViewSet, FacultyViewSet, BatchViewSet, StudentViewSet, COViewSet, POViewSet, PSOViewSet, ExternalExamViewSet, VivaViewSet, QuizViewSet, AssignmentViewSet, InternalExamViewSet, ExternalMarkViewSet, VivaMarkViewSet, QuizMarkViewSet, AssignmentMarkViewSet, InternalMarkViewSet, ExamSectionViewSet, QuestionBankViewSet, ExamQuestionViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'levels', LevelViewSet)
router.register(r'programmes', ProgrammeViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'facultys', FacultyViewSet)
router.register(r'batchs', BatchViewSet)
router.register(r'students', StudentViewSet)
router.register(r'cos', COViewSet)
router.register(r'pos', POViewSet)
router.register(r'psos', PSOViewSet)
router.register(r'externalexams', ExternalExamViewSet)
router.register(r'vivas', VivaViewSet)
router.register(r'quizs', QuizViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'internalexams', InternalExamViewSet)
router.register(r'externalmarks', ExternalMarkViewSet)
router.register(r'vivamarks', VivaMarkViewSet)
router.register(r'quizmarks', QuizMarkViewSet)
router.register(r'assignmentmarks', AssignmentMarkViewSet)
router.register(r'internalmarks', InternalMarkViewSet)
router.register(r'examsections', ExamSectionViewSet)
router.register(r'questionbanks', QuestionBankViewSet)
router.register(r'examquestions', ExamQuestionViewSet)

urlpatterns = router.urls
