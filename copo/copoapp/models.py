from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("teacher", "Teacher"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="teacher")

    def __str__(self):
        return self.username


class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=255)

    def __str__(self):
        return self.dept_name


class Level(models.Model):
    level_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Programme(models.Model):
    programme_id = models.AutoField(primary_key=True)
    programme_name = models.CharField(max_length=255)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    no_of_pos = models.IntegerField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    duration = models.IntegerField()

    def __str__(self):
        return self.programme_name


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField()
    credits = models.IntegerField()
    no_of_cos = models.IntegerField()
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    syllabus_year = models.IntegerField()

    def __str__(self):
        return self.title


class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Batch(models.Model):
    batch_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    year = models.IntegerField()
    part = models.CharField(max_length=50)
    active = models.BooleanField()

    def __str__(self):
        return f"Batch {self.year}"


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    register_no = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    year_of_admission = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name


class CO(models.Model):
    co_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    co_label = models.CharField(max_length=255)

    co_description = models.TextField()
    remember = models.IntegerField()
    understand = models.IntegerField()
    apply = models.IntegerField()
    analyze = models.IntegerField()
    evaluate = models.IntegerField()
    create = models.IntegerField()

    def __str__(self):
        return self.co_label


class PO(models.Model):
    id = models.AutoField(primary_key=True)
    po_label = models.CharField(max_length=255, null=True, blank=True)
    pos_description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return f"PO-{self.id}"


class PSO(models.Model):
    pso_id = models.AutoField(primary_key=True)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    pso_label = models.CharField(max_length=255)
    pso_desc = models.TextField()

    def __str__(self):
        return self.pso_label


class ExternalExam(models.Model):
    external_exam_id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    max_marks = models.IntegerField()

    def __str__(self):
        return f"External Exam {self.external_exam_id}"


class Viva(models.Model):
    viva_id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    max_marks = models.IntegerField()

    def __str__(self):
        return f"Viva {self.viva_id}"


class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    max_marks = models.IntegerField()

    def __str__(self):
        return f"Quiz {self.quiz_id}"


class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    max_marks = models.IntegerField()

    def __str__(self):
        return f"Assignment {self.assignment_id}"


class InternalExam(models.Model):
    int_exam_id = models.AutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    exam_name = models.CharField(
        max_length=20, null=True, blank=True
    )  # Example: IA1, IA2
    duration = models.IntegerField(null=True,blank=True)
    max_marks = models.IntegerField(null=True,blank=True)
    date=models.DateField(default=timezone.now,null=True,blank=True)

    def __str__(self):
        return f"{self.exam_name} - {self.module} (Batch {self.batch.id})"


class ExternalMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    external_exam = models.ForeignKey(
        ExternalExam, on_delete=models.CASCADE, null=True, blank=True
    )
    marks = models.IntegerField()


class VivaMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    viva = models.ForeignKey(Viva, on_delete=models.CASCADE, null=True, blank=True)
    marks = models.IntegerField()


class QuizMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, null=True, blank=True
    )  # Once all existing rows have valid quiz values, make the field non-nullable again by removing null=True, blank=True and running migrations.
    marks = models.IntegerField()


class AssignmentMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, null=True, blank=True
    )
    marks = models.IntegerField()


class InternalMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    internal_exam = models.ForeignKey(
        InternalExam, on_delete=models.CASCADE, null=True, blank=True
    )
    marks = models.IntegerField()


class ExamSection(models.Model):
    section_id = models.AutoField(primary_key=True)
    internal_exam = models.ForeignKey(InternalExam, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)
    no_of_questions = models.IntegerField()
    no_of_questions_to_be_answered = models.IntegerField()
    ceiling_mark=models.IntegerField(default=0,null=True,blank=True)
    description=models.CharField(default="Default description",max_length=500,null=True,blank=True)


class QuestionBank(models.Model):
    question_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    co = models.ForeignKey(CO, on_delete=models.CASCADE)
    question_text = models.TextField()
    marks = models.IntegerField(default=0)

    def __str__(self):
        return f"Question {self.question_id}"


class ExamQuestion(models.Model):
    q_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE)
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
