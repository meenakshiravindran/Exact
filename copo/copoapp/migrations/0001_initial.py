# Generated by Django 5.1.5 on 2025-01-20 11:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('batch_id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.IntegerField()),
                ('part', models.CharField(max_length=50)),
                ('active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.AutoField(primary_key=True, serialize=False)),
                ('course_code', models.CharField(max_length=50, unique=True)),
                ('semester', models.IntegerField()),
                ('credits', models.IntegerField()),
                ('no_of_cos', models.IntegerField()),
                ('syllabus_year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('dept_id', models.AutoField(primary_key=True, serialize=False)),
                ('dept_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('level_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('assignment_id', models.AutoField(primary_key=True, serialize=False)),
                ('max_marks', models.IntegerField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.batch')),
            ],
        ),
        migrations.CreateModel(
            name='CO',
            fields=[
                ('co_id', models.AutoField(primary_key=True, serialize=False)),
                ('co_label', models.CharField(max_length=255)),
                ('co_description', models.TextField()),
                ('remember', models.IntegerField()),
                ('understand', models.IntegerField()),
                ('apply', models.IntegerField()),
                ('analyze', models.IntegerField()),
                ('evaluate', models.IntegerField()),
                ('create', models.IntegerField()),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='copoapp.course')),
            ],
        ),
        migrations.AddField(
            model_name='batch',
            name='course_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='copoapp.course'),
        ),
        migrations.AddField(
            model_name='course',
            name='dept',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.department'),
        ),
        migrations.CreateModel(
            name='ExternalExam',
            fields=[
                ('external_exam_id', models.AutoField(primary_key=True, serialize=False)),
                ('max_marks', models.IntegerField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.batch')),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('faculty_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_no', models.CharField(max_length=15)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.department')),
            ],
        ),
        migrations.AddField(
            model_name='batch',
            name='faculty_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.faculty'),
        ),
        migrations.CreateModel(
            name='InternalExam',
            fields=[
                ('int_exam_id', models.AutoField(primary_key=True, serialize=False)),
                ('duration', models.IntegerField()),
                ('max_marks', models.IntegerField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.batch')),
            ],
        ),
        migrations.CreateModel(
            name='ExamSection',
            fields=[
                ('section_id', models.AutoField(primary_key=True, serialize=False)),
                ('section_name', models.CharField(max_length=255)),
                ('no_of_questions', models.IntegerField()),
                ('no_of_questions_to_be_answered', models.IntegerField()),
                ('internal_exam_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.internalexam')),
            ],
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('programme_id', models.AutoField(primary_key=True, serialize=False)),
                ('programme_name', models.CharField(max_length=255)),
                ('no_of_pos', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.department')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.level')),
            ],
        ),
        migrations.CreateModel(
            name='PO',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('pos_description', models.TextField()),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.level')),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.programme')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='programme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.programme'),
        ),
        migrations.CreateModel(
            name='PSO',
            fields=[
                ('pso_id', models.AutoField(primary_key=True, serialize=False)),
                ('pso_label', models.CharField(max_length=255)),
                ('pso_desc', models.TextField()),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.programme')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionBank',
            fields=[
                ('question_id', models.AutoField(primary_key=True, serialize=False)),
                ('question_text', models.TextField()),
                ('co', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.co')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.course')),
            ],
        ),
        migrations.CreateModel(
            name='ExamQuestions',
            fields=[
                ('q_id', models.AutoField(primary_key=True, serialize=False)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.examsection')),
                ('question_bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.questionbank')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('quiz_id', models.AutoField(primary_key=True, serialize=False)),
                ('max_marks', models.IntegerField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.batch')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.AutoField(primary_key=True, serialize=False)),
                ('register_no', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('year_of_admission', models.IntegerField()),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.programme')),
            ],
        ),
        migrations.CreateModel(
            name='QuizMarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.IntegerField()),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.student')),
            ],
        ),
        migrations.CreateModel(
            name='InternalMarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.IntegerField()),
                ('internal_exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.internalexam')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.student')),
            ],
        ),
        migrations.CreateModel(
            name='ExternalMarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.IntegerField()),
                ('external_exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.externalexam')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.student')),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentMarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.IntegerField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.student')),
            ],
        ),
        migrations.CreateModel(
            name='Viva',
            fields=[
                ('viva_id', models.AutoField(primary_key=True, serialize=False)),
                ('max_marks', models.IntegerField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.batch')),
            ],
        ),
        migrations.CreateModel(
            name='VivaMarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.IntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.student')),
                ('viva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='copoapp.viva')),
            ],
        ),
    ]
