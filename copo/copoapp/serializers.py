from rest_framework import serializers
from .models import Department, Level, Programme, Course, Faculty, Batch, Student, CO, PO, PSO, ExternalExam, Viva, Quiz, Assignment, InternalExam, ExternalMark, VivaMark, QuizMark, AssignmentMark, InternalMark, ExamSection, QuestionBank, ExamQuestion

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class COSerializer(serializers.ModelSerializer):
    class Meta:
        model = CO
        fields = '__all__'

class POSerializer(serializers.ModelSerializer):
    class Meta:
        model = PO
        fields = '__all__'

class PSOSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSO
        fields = '__all__'

class ExternalExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalExam
        fields = '__all__'

class VivaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Viva
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

class InternalExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalExam
        fields = '__all__'

class ExternalMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalMark
        fields = '__all__'

class VivaMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VivaMark
        fields = '__all__'

class QuizMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizMark
        fields = '__all__'

class AssignmentMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentMark
        fields = '__all__'

class InternalMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalMark
        fields = '__all__'

class ExamSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSection
        fields = '__all__'

class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'

class ExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamQuestion
        fields = '__all__'

