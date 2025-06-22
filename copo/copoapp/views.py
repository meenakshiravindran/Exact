from rest_framework import viewsets
from .models import Department, Level, Programme, Course, Faculty, Batch, Student, CO, PO, PSO, ExternalExam, Viva, Quiz, Assignment, InternalExam, ExternalMark, VivaMark, QuizMark, AssignmentMark, InternalMark, ExamSection, QuestionBank, ExamQuestion
from .serializers import DepartmentSerializer, LevelSerializer, ProgrammeSerializer, CourseSerializer, FacultySerializer, BatchSerializer, StudentSerializer, COSerializer, POSerializer, PSOSerializer, ExternalExamSerializer, VivaSerializer, QuizSerializer, AssignmentSerializer, InternalExamSerializer, ExternalMarkSerializer, VivaMarkSerializer, QuizMarkSerializer, AssignmentMarkSerializer, InternalMarkSerializer, ExamSectionSerializer, QuestionBankSerializer, ExamQuestionSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class ProgrammeViewSet(viewsets.ModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class COViewSet(viewsets.ModelViewSet):
    queryset = CO.objects.all()
    serializer_class = COSerializer

class POViewSet(viewsets.ModelViewSet):
    queryset = PO.objects.all()
    serializer_class = POSerializer

class PSOViewSet(viewsets.ModelViewSet):
    queryset = PSO.objects.all()
    serializer_class = PSOSerializer

class ExternalExamViewSet(viewsets.ModelViewSet):
    queryset = ExternalExam.objects.all()
    serializer_class = ExternalExamSerializer

class VivaViewSet(viewsets.ModelViewSet):
    queryset = Viva.objects.all()
    serializer_class = VivaSerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

class InternalExamViewSet(viewsets.ModelViewSet):
    queryset = InternalExam.objects.all()
    serializer_class = InternalExamSerializer

class ExternalMarkViewSet(viewsets.ModelViewSet):
    queryset = ExternalMark.objects.all()
    serializer_class = ExternalMarkSerializer

class VivaMarkViewSet(viewsets.ModelViewSet):
    queryset = VivaMark.objects.all()
    serializer_class = VivaMarkSerializer

class QuizMarkViewSet(viewsets.ModelViewSet):
    queryset = QuizMark.objects.all()
    serializer_class = QuizMarkSerializer

class AssignmentMarkViewSet(viewsets.ModelViewSet):
    queryset = AssignmentMark.objects.all()
    serializer_class = AssignmentMarkSerializer

class InternalMarkViewSet(viewsets.ModelViewSet):
    queryset = InternalMark.objects.all()
    serializer_class = InternalMarkSerializer

class ExamSectionViewSet(viewsets.ModelViewSet):
    queryset = ExamSection.objects.all()
    serializer_class = ExamSectionSerializer

class QuestionBankViewSet(viewsets.ModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer

class ExamQuestionViewSet(viewsets.ModelViewSet):
    queryset = ExamQuestion.objects.all()
    serializer_class = ExamQuestionSerializer

