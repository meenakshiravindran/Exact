from django.db import models


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
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField()
    credits = models.IntegerField()
    no_of_cos = models.IntegerField()
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    syllabus_year = models.IntegerField()

    def __str__(self):
        return self.course_code


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
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True, blank=True)  
    faculty_id = models.ForeignKey(Faculty,on_delete=models.CASCADE)
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
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True, blank=True)
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
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
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
    duration = models.IntegerField()
    max_marks = models.IntegerField()

    def __str__(self):
        return f"Internal Exam {self.int_exam_id}"


class ExternalMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    external_exam = models.ForeignKey(ExternalExam, on_delete=models.CASCADE)
    marks = models.IntegerField()


class VivaMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    viva = models.ForeignKey(Viva, on_delete=models.CASCADE)
    marks = models.IntegerField()


class QuizMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    marks = models.IntegerField()


class AssignmentMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    marks = models.IntegerField()


class InternalMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    internal_exam = models.ForeignKey(InternalExam, on_delete=models.CASCADE)
    marks = models.IntegerField()


class ExamSection(models.Model):
    section_id = models.AutoField(primary_key=True)
    internal_exam = models.ForeignKey(InternalExam, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)
    no_of_questions = models.IntegerField()
    no_of_questions_to_be_answered = models.IntegerField()


class QuestionBank(models.Model):
    question_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    co = models.ForeignKey(CO, on_delete=models.CASCADE)
    question_text = models.TextField()

    def __str__(self):
        return f"Question {self.question_id}"


class ExamQuestions(models.Model):
    q_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE)
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)