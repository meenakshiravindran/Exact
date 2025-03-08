from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
import json
import re
import io
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.core.files.storage import default_storage
import pandas as pd
from .models import (
    Faculty,
    Department,
    Student,
    Programme,
    Level,
    Course,
    Batch,
    CustomUser,
    PO,
    CO,
    PSO,
    QuestionBank,
    InternalExam,
    ExamSection,
    ExamQuestion
)
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import os
import subprocess
import base64
import fitz  # PyMuPDF
from g4f.client import Client
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


User = get_user_model()


class CustomTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)

            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
                "full_name": f"{user.first_name} {user.last_name}",
                "is_first_login": user.is_first_login,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_credentials(request):
    """Allow user to update username and password on first login"""
    new_username = request.data.get("new_username")
    new_password = request.data.get("new_password")
    
    user = request.user
    print("User",user.is_first_login)
    if user.is_first_login and user.role=="teacher":
        user.username = new_username
        user.password = make_password(new_password) 
        user.is_first_login = False
        user.save()
        return Response({"message": "Credentials updated successfully"}, status=status.HTTP_200_OK)
    
    return Response({"error": "User has already updated credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(APIView):
    def post(self, request):
        data = request.data
        
        # Extracting user details from request data
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        email = data.get("email", "")
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "teacher")  # Default role is "teacher"

        # Validate required fields
        if not all([username, password, email, first_name]):
            return Response({"error": "All fields are required."}, status=400)

        # Create user
        user = CustomUser.objects.create_user(
            username=username, 
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )

        # Assign admin privileges if role is "admin"
        if role == "admin":
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return Response({"message": "User created successfully!"}, status=201)


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user  # Get the currently authenticated user
        return Response({
            "username": user.username,  # Return the username
            "role": getattr(user, 'role', 'teacher') , # Return the role if it exists
            "full_name": user.get_full_name() ,
        })

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        try:
            refresh_token = request.data["refresh_token"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Views related to faculty


class FacultyView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = ["name", "department", "email", "phone_number"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validate email format
        try:
            validate_email(data["email"])
        except ValidationError:
            return Response(
                {"email": "Enter a valid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for unique email
        if Faculty.objects.filter(email=data["email"]).exists():
            return Response(
                {"email": "A faculty member with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the Department instance
        try:
            department = Department.objects.get(dept_name=data["department"])
        except ObjectDoesNotExist:
            return Response(
                {"department": "The specified department does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Faculty instance
        faculty = Faculty(
            name=data["name"],
            dept=department,  # Assign the Department instance
            email=data["email"],
            phone_no=data["phone_number"],
        )
        faculty.save()

        return Response(
            {"message": "Faculty member created successfully."},
            status=status.HTTP_201_CREATED,
        )


@csrf_exempt
def edit_faculty(request, faculty_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            if "name" in data:
                faculty.name = data["name"]
            if "dept" in data:
                dept = Department.objects.get(dept_name=data["dept"])
                faculty.dept = dept
            if "email" in data:
                faculty.email = data["email"]
            if "phone" in data:
                faculty.phone_no = data["phone"]
            faculty.save()
            return JsonResponse(
                {"message": "Faculty updated successfully."}, status=200
            )
        except Faculty.DoesNotExist:
            return JsonResponse({"error": "Faculty not found."}, status=404)
        except Department.DoesNotExist:
            return JsonResponse({"dept": "Invalid department."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)



@csrf_exempt
def delete_faculty(request, faculty_id):
    if request.method == "DELETE":
        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            email = faculty.email  

            # Delete Faculty Record
            faculty.delete()

            # Delete Associated User Record
            deleted, _ = CustomUser.objects.filter(email=email).delete()

            return JsonResponse(
                {
                    "message": "Faculty and associated user deleted successfully."
                    if deleted
                    else "Faculty deleted, but no associated user found.",
                },
                status=200,
            )
        except Faculty.DoesNotExist:
            return JsonResponse({"error": "Faculty not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

# Get All Faculties name
def get_faculty(request):
    try:
        faculty_list = Faculty.objects.all()
        faculty_data = [
            {"faculty_id": faculty.faculty_id, "name": faculty.name, "dept":faculty.dept.dept_name}
            for faculty in faculty_list
        ]
        return JsonResponse(faculty_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Get specific details of faculties
@csrf_exempt
def get_faculty_details(request, faculty_id):
    if request.method == "GET":
        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            faculty_data = {
                "faculty_id": faculty.faculty_id,
                "name": faculty.name,
                "dept": faculty.dept.dept_name,  # Including department name for context (optional)
                "email": faculty.email,
                "phone": faculty.phone_no,
            }
            return JsonResponse(faculty_data, status=200)
        except Faculty.DoesNotExist:
            return JsonResponse({"error": "Faculty not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


class DepartmentView(APIView):
    def get(self, request):
        departments = Department.objects.all()
        department_data = [
            {"dept_id": dept.dept_id, "dept_name": dept.dept_name}
            for dept in departments
        ]
        return JsonResponse(department_data, safe=False)


@csrf_exempt
def add_student(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            programme = Programme.objects.get(programme_name=data["programme"])
            student = Student.objects.create(
                register_no=data["register_no"],
                name=data["name"],
                programme=programme,
                year_of_admission=data["year_of_admission"],
                phone_number=data["phone_number"],
                email=data["email"],
            )
            return JsonResponse({"message": "Student added successfully."}, status=201)
        except Programme.DoesNotExist:
            return JsonResponse({"programme": "Invalid programme."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


def get_levels(request):
    try:
        levels = Level.objects.all()
        levels_data = [
            {"level_id": level.level_id, "level_name": level.name} for level in levels
        ]
        return JsonResponse(levels_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



# Add a Course
class CourseView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = ["title", "dept", "course_code","syllabus_year","no_of_cos","semester","credits"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check for unique course code
        if Course.objects.filter(course_code=data["course_code"]).exists():
            return Response(
                {"course_code": "A course with this code already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the Department instance
        try:
            department = Department.objects.get(dept_name=data["dept"])
        except ObjectDoesNotExist:
            return Response(
                {"department": "The specified department does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

        # Create Course instance
        course = Course(
            title=data["title"],
            dept=department,  # Assign the Department instance
            course_code=data["course_code"],
            syllabus_year=data["syllabus_year"],
            no_of_cos=data["no_of_cos"],
            semester=data["semester"],
            credits=data["credits"]

        )
        course.save()

        return Response(
            {"message": "Course created successfully."},
            status=status.HTTP_201_CREATED,
        )


# Edit a Course
@csrf_exempt
def edit_course(request, course_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            course = Course.objects.get(course_id=course_id)
            if "title" in data:
                course.title = data["title"]
            if "dept" in data:
                dept = Department.objects.get(dept_name=data["dept"])
                course.dept = dept
            if "course_code" in data:
                course.course_code = data["course_code"]
            if "credits" in data:
                course.credits = data["credits"]
            if "syllabus_year" in data:
                course.syllabus_year = data["syllabus_year"]
            if "no_of_cos" in data:
                course.no_of_cos = data["no_of_cos"]
            course.save()
            return JsonResponse(
                {"message": "Course updated successfully."}, status=200
            )
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found."}, status=404)
        except Department.DoesNotExist:
            return JsonResponse({"dept": "Invalid department."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Delete a Course
@csrf_exempt
def delete_course(request, course_id):
    if request.method == "DELETE":
        try:
            course = Course.objects.get(course_id=course_id)
            course.delete()
            return JsonResponse(
                {"message": "Course deleted successfully."}, status=200
            )
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Get All Courses
def get_courses(request):
    try:
        course_list = Course.objects.all()
        course_data = [
            {"course_id": course.course_id, "title": course.title,"dept":course.dept.dept_name}
            for course in course_list
        ]
        return JsonResponse(course_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Get Specific Course Details
@csrf_exempt
def get_course_details(request, course_id):
    if request.method == "GET":
        try:
            course = Course.objects.get(course_id=course_id)
            course_data = {
                "course_id": course.course_id,
                "title": course.title,
                "dept": course.dept.dept_name,  # Including department name for context
                "course_code": course.course_code,
                "semester":course.semester,
                "credits":course.credits,
                "syllabus_year":course.syllabus_year,
                "no_of_cos":course.no_of_cos

            }
            return JsonResponse(course_data, status=200)
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

# def get_course_by_programme(request, programme_id):
#     if request.method == "GET":
#         programme = get_object_or_404(Programme, programme_id=programme_id)
#         course = Course.objects.filter(programme=programme).values(
#            "course_id","title"
#         )
#         return JsonResponse(list(course), safe=False, status=200)
    
#     return JsonResponse({"error": "Invalid request method."}, status=405)


# Add a Batch
@csrf_exempt
def add_batch(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            faculty = Faculty.objects.get(faculty_id=data["faculty_id"])
            course = Course.objects.get(title=data["course"]) if data.get("course") else None
            batch = Batch.objects.create(
                faculty_id=faculty,
                course=course,
                year=data["year"],
                part=data["part"],
                active=data["active"],
            )
            return JsonResponse({"message": "Batch created successfully."}, status=201)
        except Faculty.DoesNotExist:
            return JsonResponse({"faculty_id": "Invalid faculty."}, status=400)
        except Course.DoesNotExist:
            return JsonResponse({"course": "Invalid course."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Edit a Batch
@csrf_exempt
def edit_batch(request, batch_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            batch = Batch.objects.get(batch_id=batch_id)
            if "faculty" in data:
                faculty = Faculty.objects.get(name=data["faculty"])
                batch.faculty_id = faculty
            if "course" in data:
                course = Course.objects.get(title=data["course"])
                batch.course = course
            if "year" in data:
                batch.year = data["year"]
            if "part" in data:
                batch.part = data["part"]
            if "active" in data:
                batch.active = data["active"]
            batch.save()
            return JsonResponse({"message": "Batch updated successfully."}, status=200)
        except Batch.DoesNotExist:
            return JsonResponse({"error": "Batch not found."}, status=404)
        except Faculty.DoesNotExist:
            return JsonResponse({"faculty_id": "Invalid faculty."}, status=400)
        except Course.DoesNotExist:
            return JsonResponse({"course": "Invalid course."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Delete a Batch
@csrf_exempt
def delete_batch(request, batch_id):
    if request.method == "DELETE":
        try:
            batch = Batch.objects.get(batch_id=batch_id)
            batch.delete()
            return JsonResponse({"message": "Batch deleted successfully."}, status=200)
        except Batch.DoesNotExist:
            return JsonResponse({"error": "Batch not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Get All Batches
def get_batches(request):
    try:
        batch_list = Batch.objects.all()
        batch_data = [
            {
                "batch_id": batch.batch_id,
                "faculty": batch.faculty_id.name,
                "course": batch.course.title if batch.course else None,
                "year": batch.year,
                "part": batch.part,
                "active": batch.active,
            }
            for batch in batch_list
        ]
        return JsonResponse(batch_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Get Specific Batch Details
@csrf_exempt
def get_batch_details(request, batch_id):
    if request.method == "GET":
        try:
            batch = Batch.objects.get(batch_id=batch_id)
            batch_data = {
                "batch_id": batch.batch_id,
                "faculty": batch.faculty_id.name,
                "course": batch.course.title if batch.course else None,
                "year": batch.year,
                "part": batch.part,
                "active": batch.active,
            }
            return JsonResponse(batch_data, status=200)
        except Batch.DoesNotExist:
            return JsonResponse({"error": "Batch not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Add a Programme
class ProgrammeView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = ["programme_name", "department", "level", "duration"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check for unique programme name
        if Programme.objects.filter(programme_name=data["programme_name"]).exists():
            return Response(
                {"programme_name": "A programme with this name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the Department instance
        try:
            department = Department.objects.get(dept_name=data["department"])
        except ObjectDoesNotExist:
            return Response(
                {"department": "The specified department does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the Level instance
        try:
            level = Level.objects.get(name=data["level"])
        except ObjectDoesNotExist:
            return Response(
                {"level": "The specified level does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Programme instance
        programme = Programme(
            programme_name=data["programme_name"],
            dept=department,  # Assign the Department instance
            no_of_pos=data["no_of_pos"],
            level=level,  # Assign the Level instance
            duration=data["duration"],
        )
        programme.save()

        return Response(
            {"message": "Programme created successfully."},
            status=status.HTTP_201_CREATED,
        )


# Edit a Programme
@csrf_exempt
def edit_programme(request, programme_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            programme = Programme.objects.get(programme_id=programme_id)
            if "programme_name" in data:
                programme.programme_name = data["programme_name"]
            if "dept" in data:
                dept = Department.objects.get(dept_name=data["dept"])
                programme.dept = dept
            if "level" in data:
                level = Level.objects.get(name=data["level"])
                programme.level = level
            if "no_of_pos" in data:
                programme.no_of_pos = data["no_of_pos"]
            if "duration" in data:
                programme.duration = data["duration"]
            programme.save()
            return JsonResponse(
                {"message": "Programme updated successfully."}, status=200
            )
        except Programme.DoesNotExist:
            return JsonResponse({"error": "Programme not found."}, status=404)
        except Department.DoesNotExist:
            return JsonResponse({"dept": "Invalid department."}, status=400)
        except Level.DoesNotExist:
            return JsonResponse({"level": "Invalid level."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Delete a Programme
@csrf_exempt
def delete_programme(request, programme_id):
    if request.method == "DELETE":
        try:
            programme = Programme.objects.get(programme_id=programme_id)
            programme.delete()
            return JsonResponse(
                {"message": "Programme deleted successfully."}, status=200
            )
        except Programme.DoesNotExist:
            return JsonResponse({"error": "Programme not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Get All Programmes
def get_programmes(request):
    try:
        programme_list = Programme.objects.all()
        programme_data = [
            {
                "programme_id": programme.programme_id,
                "programme_name": programme.programme_name,
                "department": programme.dept.dept_name,
                "level": programme.level.name,
            }
            for programme in programme_list
        ]
        return JsonResponse(programme_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Get Specific Programme Details
@csrf_exempt
def get_programme_details(request, programme_id):
    if request.method == "GET":
        try:
            programme = Programme.objects.get(programme_id=programme_id)
            programme_data = {
                "programme_id": programme.programme_id,
                "programme_name": programme.programme_name,
                "department": programme.dept.dept_name,
                "level": programme.level.name,
                "no_of_pos": programme.no_of_pos,
                "duration": programme.duration,
            }
            return JsonResponse(programme_data, status=200)
        except Programme.DoesNotExist:
            return JsonResponse({"error": "Programme not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def edit_student(request, student_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            student = Student.objects.get(student_id=student_id)
            
            if "name" in data:
                student.name = data["name"]
            if "register_no" in data:
                student.register_no = data["register_no"]
            if "programme" in data:
                programme = Programme.objects.get(programme_name=data["programme"])  # Assuming Programme model has an ID field
                student.programme = programme
            if "year_of_admission" in data:
                student.year_of_admission = data["year_of_admission"]
            if "phone_number" in data:
                student.phone_number = data["phone_number"]
            if "email" in data:
                student.email = data["email"]
            
            student.save()
            return JsonResponse({"message": "Student updated successfully."}, status=200)

        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=404)
        except Programme.DoesNotExist:
            return JsonResponse({"error": "Invalid programme."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def get_student_details(request, student_id):
    if request.method == "GET":
        student = get_object_or_404(Student, student_id=student_id)
        return JsonResponse({
            "name": student.name,
            "register_no": student.register_no,
            "admn_no":student.admn_no,
            "programme": student.programme.programme_name,  # Assuming Programme model has an ID field
            "year_of_admission": student.year_of_admission,
            "phone_number": student.phone_number,
            "email": student.email,
        }, status=200)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_students_by_programme(request, programme_id=None):
    if request.method == "GET":
        if programme_id:
            programme = get_object_or_404(Programme, programme_id=programme_id)
            students = Student.objects.filter(programme=programme)
        else:
            students = Student.objects.all()

        student_data = students.values(
            "student_id", "name", "register_no", "year_of_admission", "phone_number", "email","admn_no","programme__programme_name"
        )

        return JsonResponse(list(student_data), safe=False, status=200)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)
@csrf_exempt
def delete_student(request,student_id):
    if request.method=="DELETE":
        try:
            student = Student.objects.get(student_id=student_id)
            student.delete()
            return JsonResponse(
                {"message": "Student deleted successfully."}, status=200
            )
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

class POView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = [ "description", "level","po_number"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get Level instance
        try:
            level = Level.objects.get(name=data["level"])
        except ObjectDoesNotExist:
            return Response(
                {"level": "The specified level does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create PO instance
        po = PO(
            pos_description=data["description"],
            level=level,
            po_label=data['po_number']
        )
        po.save()

        return Response(
            {"message": "Programme Outcome created successfully."},
            status=status.HTTP_201_CREATED,
        )

@csrf_exempt
def edit_po(request, po_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            po = PO.objects.get(id=po_id)
            if "po_label" in data:
                po.po_label=data["po_label"]
            if "pos_description" in data:
                po.pos_description = data["pos_description"]
            if "level" in data:
                level = Level.objects.get(level_id=data["level"])
                po.level = level
            po.save()
            return JsonResponse(
                {"message": "Programme Outcome updated successfully."}, status=200
            )
        except PO.DoesNotExist:
            return JsonResponse({"error": "Programme Outcome not found."}, status=404)
        except Programme.DoesNotExist:
            return JsonResponse({"programme": "Invalid programme."}, status=400)
        except Level.DoesNotExist:
            return JsonResponse({"level": "Invalid level."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def delete_po(request, po_id):
    if request.method == "DELETE":
        try:
            po = PO.objects.get(id=po_id)
            po.delete()
            return JsonResponse(
                {"message": "Programme Outcome deleted successfully."}, status=200
            )
        except PO.DoesNotExist:
            return JsonResponse({"error": "Programme Outcome not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


def get_pos_by_level(request, level_id=None):
    try:
        if level_id:
            po_list = PO.objects.filter(level_id=level_id)
        else:
            po_list = PO.objects.all()

        po_data = [
            {
                "id": po.id,
                "po_label": po.po_label,
                "pos_description": po.pos_description,
                "level_id": po.level.level_id,
                "level_name": po.level.name,
            }
            for po in po_list
        ]
        return JsonResponse(po_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def get_po_details(request, po_id):
    if request.method == "GET":
        try:
            po = PO.objects.get(id=po_id)
            po_data = {
                "id": po.id,
                "po_label":po.po_label,
                "pos_description": po.pos_description,
                "level": po.level.level_id,
            }
            return JsonResponse(po_data, status=200)
        except PO.DoesNotExist:
            return JsonResponse({"error": "Programme Outcome not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

# Add a CO
class COView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = ["bloom_taxonomy", "co_label", "co_description", "course"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check if course exists
        try:
            course = Course.objects.get(title=data["course"])
        except ObjectDoesNotExist:
            return Response(
                {"course": "The specified course does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Initialize all Bloom's Taxonomy fields to 0
        bloom_taxonomy_fields = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        taxonomy_values = {field: 0 for field in bloom_taxonomy_fields}

        # Check if bloom_taxonomy is provided and valid
        if "bloom_taxonomy" in data and isinstance(data["bloom_taxonomy"], list):
            for taxonomy in data["bloom_taxonomy"]:
                taxonomy = taxonomy.lower()
                if taxonomy in taxonomy_values:
                    taxonomy_values[taxonomy] = 1
                else:
                    return Response(
                        {"bloom_taxonomy": f"Invalid taxonomy selection: {taxonomy}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # Create Course Outcome instance
        co = CO(
            co_label=data["co_label"],
            co_description=data["co_description"],
            course=course,
            **taxonomy_values,  # Unpacking the dictionary to assign values dynamically
        )
        co.save()

        return Response(
            {"message": "Course Outcome created successfully."},
            status=status.HTTP_201_CREATED,
        )

@csrf_exempt
def edit_co(request, co_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            co = CO.objects.get(co_id=co_id)  # Fetching CO by co_id
            
            # Update CO label
            if "co_label" in data:
                co.co_label = data["co_label"]
            
            # Update CO description
            if "co_description" in data:
                co.co_description = data["co_description"]
            
            # Update course
            if "course" in data:
                course = Course.objects.get(title=data["course"])
                co.course = course
            
            # Update Bloom's Taxonomy using the dictionary format
            if "bloom_taxonomy" in data and isinstance(data["bloom_taxonomy"], dict):
                bloom_taxonomy_fields = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
                
                for field in bloom_taxonomy_fields:
                    if field in data["bloom_taxonomy"]:
                        setattr(co, field, int(data["bloom_taxonomy"][field]))  # Ensure it's stored as an integer
            
            co.save()
            return JsonResponse(
                {"message": "Course Outcome updated successfully."}, status=200
            )
        except CO.DoesNotExist:
            return JsonResponse({"error": "Course Outcome not found."}, status=404)
        except Course.DoesNotExist:
            return JsonResponse({"error": "Invalid course title."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Delete a CO
@csrf_exempt
def delete_co(request, co_id):
    if request.method == "DELETE":
        try:
            co = CO.objects.get(co_id=co_id)
            co.delete()
            return JsonResponse(
                {"message": "Course Outcome deleted successfully."}, status=200
            )
        except CO.DoesNotExist:
            return JsonResponse({"error": "Course Outcome not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Get All COs
def get_cos(request):
    try:
        co_list = CO.objects.all()
        co_data = [
            {
                "co_id": co.co_id,
                "co_label": co.co_label,
                "co_description": co.co_description,
                "course": co.course.title,
                "programme":co.course.programme.programme_name
            }
            for co in co_list
        ]
        return JsonResponse(co_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Get Specific CO Details
@csrf_exempt
def get_co_details(request, co_id):
    if request.method == "GET":
        try:
            co = CO.objects.get(co_id=co_id)
            co_data = {
                "co_id": co.co_id,
                "co_label": co.co_label,
                "co_description": co.co_description,
                "course": co.course.title,
                "bloom_taxonomy": {
                    "remember": co.remember,
                    "understand": co.understand,
                    "apply": co.apply,
                    "analyze": co.analyze,
                    "evaluate": co.evaluate,
                    "create": co.create,
                }
            }
            return JsonResponse(co_data, status=200)
        except CO.DoesNotExist:
            return JsonResponse({"error": "Course Outcome not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_co_by_course(request, course_id):
    if request.method == "GET":
        course = get_object_or_404(Course, course_id=course_id)
        co = CO.objects.filter(course=course).values(
            "co_id","co_label","co_description"
        )
        return JsonResponse(list(co), safe=False, status=200)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)


class PSOView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = ["pso_label", "programme", "pso_desc"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check for unique PSO name
        if PSO.objects.filter(pso_label=data["pso_label"]).exists():
            return Response(
                {"pso_label": "A PSO with this name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the Programme instance
        try:
            programme = Programme.objects.get(programme_name=data["programme"])
        except ObjectDoesNotExist:
            return Response(
                {"programme": "The specified programme does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create PSO instance
        pso = PSO(
            pso_label=data["pso_label"],
            programme=programme,  # Assign the Programme instance
            pso_desc=data["pso_desc"],
        )
        pso.save()

        return Response(
            {"message": "PSO created successfully."},
            status=status.HTTP_201_CREATED,
        )

@csrf_exempt
def edit_pso(request, pso_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            pso = PSO.objects.get(pso_id=pso_id)
            if "pso_label" in data:
                pso.pso_label = data["pso_label"]
            if "programme" in data:
                programme = Programme.objects.get(programme_name=data["programme"])
                pso.programme = programme
            if "description" in data:
                pso.pso_desc = data["description"]
            pso.save()
            return JsonResponse(
                {"message": "PSO updated successfully."}, status=200
            )
        except PSO.DoesNotExist:
            return JsonResponse({"error": "PSO not found."}, status=404)
        except Programme.DoesNotExist:
            return JsonResponse({"programme": "Invalid programme."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def delete_pso(request, pso_id):
    if request.method == "DELETE":
        try:
            pso = PSO.objects.get(pso_id=pso_id)
            pso.delete()
            return JsonResponse(
                {"message": "PSO deleted successfully."}, status=200
            )
        except PSO.DoesNotExist:
            return JsonResponse({"error": "PSO not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_psos(request):
    try:
        pso_list = PSO.objects.all()
        pso_data = [
            {
                "pso_id": pso.pso_id,
                "pso_label": pso.pso_label,
                "programme": pso.programme.programme_name,
                "pso_desc": pso.pso_desc,
            }
            for pso in pso_list
        ]
        return JsonResponse(pso_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def get_pso_details(request, pso_id):
    if request.method == "GET":
        try:
            pso = PSO.objects.get(pso_id=pso_id)
            pso_data = {
                "pso_id": pso.pso_id,
                "pso_name": pso.pso_label,
                "programme": pso.programme.programme_name,
                "description": pso.pso_desc,
            }
            return JsonResponse(pso_data, status=200)
        except PSO.DoesNotExist:
            return JsonResponse({"error": "PSO not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_psos_by_programme(request, programme_id):
    if request.method == "GET":
        programme = get_object_or_404(Programme, programme_id=programme_id)
        psos = PSO.objects.filter(programme=programme).values(
            "pso_id", "pso_label", "pso_desc"
        )
        return JsonResponse(list(psos), safe=False, status=200)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)



class AddQuestionView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation of required fields
        required_fields = ["question_text", "course", "co","marks"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get Course instance
        try:
            course = Course.objects.get(course_id=data["course"])
        except ObjectDoesNotExist:
            return Response(
                {"course": "The specified course does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get CO instance
        try:
            co = CO.objects.get(co_id=data["co"])
        except ObjectDoesNotExist:
            return Response(
                {"co": "The specified CO does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        #Validate marks
        try:
            marks = int(data["marks"])
            if marks <= 0:
                return Response(
                    {"marks": "Marks must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"marks": "Marks must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create QuestionBank instance
        question = QuestionBank(
            question_text=data["question_text"],
            course=course,
            co=co,
            marks=marks,
        )
        question.save()

        return Response(
            {"message": "Question added successfully."},
            status=status.HTTP_201_CREATED,
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only allow authenticated users
def get_faculty_batches(request):
    try:
        faculty = get_object_or_404(Faculty, email=request.user.email)
        batches = Batch.objects.filter(faculty_id=faculty).values(
            "batch_id", "course__title", "year", "part", "active"
        )
        return Response(list(batches), status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

class InternalExamView(APIView):
    def post(self, request):
        data = request.data

        # Required fields validation
        required_fields = ["batch", "exam_name", "duration", "max_marks", "exam_date"]
        for field in required_fields:
            if field not in data or not data[field]:
                return Response(
                    {field: "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validate batch existence
        try:
            batch = Batch.objects.get(batch_id=data["batch"])
        except ObjectDoesNotExist:
            return Response(
                {"batch": "The specified batch does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate and parse exam_date
        try:
            exam_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"exam_date": "Invalid date format. Expected format: YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create InternalExam instance with the date field
        internal_exam = InternalExam(
            batch=batch,
            exam_name=data["exam_name"],
            duration=data["duration"],
            max_marks=data["max_marks"],
            date=exam_date,  # Assigning the parsed date
        )
        internal_exam.save()

        return Response(
            {"message": "Internal exam created successfully.","data":internal_exam.int_exam_id},
            status=status.HTTP_201_CREATED,
        )

class FacultyInternalExamsView(APIView):
    def get(self, request):
        faculty_email = request.user.email

        batches = Batch.objects.filter(faculty_id__email=faculty_email)

        exams = InternalExam.objects.filter(batch__in=batches).values(
            "int_exam_id", "exam_name", "duration", "max_marks"
        )

        return Response(exams, status=status.HTTP_200_OK)

@csrf_exempt
def edit_question(request, question_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            question = get_object_or_404(QuestionBank, question_id=question_id)

            if "course" in data:
                course = get_object_or_404(Course, course_id=data["course"])
                question.course = course

            if "co" in data:
                co = get_object_or_404(CO, co_id=data["co"])
                question.co = co

            if "question_text" in data:
                question.question_text = data["question_text"]

            if "marks" in data:
                question.marks = int(data["marks"])

            question.save()
            return JsonResponse({"message": "Question updated successfully."}, status=200)
        
        except Course.DoesNotExist:
            return JsonResponse({"error": "Invalid course."}, status=400)
        
        except CO.DoesNotExist:
            return JsonResponse({"error": "Invalid CO."}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def get_question_details(request, question_id):
    """Fetch details of a specific question"""
    if request.method == "GET":
        try:
            question = get_object_or_404(QuestionBank, question_id=question_id)
            question_data = {
                "question_id": question.question_id,
                "question_text": question.question_text,
                "course": question.course.course_id,
                "co": question.co.co_id,
                "marks": question.marks,
            }
            return JsonResponse(question_data, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def delete_question(request, question_id):
    if request.method == "DELETE":
        try:
            question = QuestionBank.objects.get(pk=question_id)
            question.delete()
            return JsonResponse({"message": "Question deleted successfully"})
        except QuestionBank.DoesNotExist:
            return JsonResponse({"error": "Question not found"}, status=404)

# Get All Questions
def get_questions(request):
    try:
        question_list = QuestionBank.objects.all()
        question_data = [
            {
                "question_id": question.question_id,
                "question_text": question.question_text,
                "marks": question.marks,
                "course": question.course.title,
                "programme": question.course.programme.programme_name,
                "co_label": question.co.co_label,
            }
            for question in question_list
        ]
        return JsonResponse(question_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def add_exam_section(request, int_exam_id):
    if request.method == "POST":
        data = json.loads(request.body)
        internal_exam = get_object_or_404(InternalExam, pk=int_exam_id)
        
        new_section = ExamSection.objects.create(
            internal_exam=internal_exam,
            section_name=data.get("section_name"),
            no_of_questions=data.get("no_of_questions"),
            no_of_questions_to_be_answered=data.get("no_of_questions_to_be_answered"),
            ceiling_mark=data.get("ceiling_mark", 0),
            description=data.get("description", "Default description"),
        )
        
        return JsonResponse({
            "id": new_section.section_id,
            "name": new_section.section_name,
            "numQuestions": new_section.no_of_questions,
            "numToAnswer": new_section.no_of_questions_to_be_answered,
            "ceilingMark": new_section.ceiling_mark,
            "description": new_section.description
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

        
def get_exam_sections(request, int_exam_id):
    sections = ExamSection.objects.filter(internal_exam_id=int_exam_id)
    sections_data = [
        {
            "id": section.section_id,
            "name": section.section_name,
            "numQuestions": section.no_of_questions,
            "numToAnswer": section.no_of_questions_to_be_answered,
            "ceilingMark": section.ceiling_mark,
            "description": section.description
        }
        for section in sections
    ]
    return JsonResponse({"sections": sections_data})

@csrf_exempt
def delete_exam_section(request, section_id):
    if request.method == "DELETE":
        section = get_object_or_404(ExamSection, pk=section_id)
        section.delete()
        return JsonResponse({"message": "Section deleted successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)


def get_exam_details(request, int_exam_id):
    # Get the internal exam object by id
    exam = get_object_or_404(InternalExam, int_exam_id=int_exam_id)

    # Fetch batch and course info
    batch = exam.batch
    course_name = batch.course.title if batch.course else "Unknown Course"
    faculty_name = batch.faculty_id.name if batch.faculty_id else "Unknown Faculty"
    
    # Create a response data structure
    exam_details = {
        "exam_name": exam.exam_name,
        "course_name": course_name,
        "faculty_name": faculty_name,
        "duration": exam.duration,
        "max_marks": exam.max_marks,
        "date": exam.date,
    }

    return JsonResponse(exam_details)


class GetQuestionsView(APIView):
    def get(self, request):
        marks = request.GET.get("marks")
        if not marks:
            return JsonResponse({"error": "Marks parameter is required"}, status=400)

        questions = QuestionBank.objects.filter(marks=int(marks)).values("question_id", "question_text", "marks")
        return JsonResponse(list(questions), safe=False)
    
    
    
class AddExamQuestionsView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            section = ExamSection.objects.get(section_id=data["section_id"])
            question_ids = data["question_ids"]

            # Remove all existing questions that are not in the selected list
            ExamQuestion.objects.filter(section=section).exclude(question_bank__question_id__in=question_ids).delete()

            # Add the new questions
            for q_id in question_ids:
                # Check if the question already exists to avoid duplicates
                question = QuestionBank.objects.get(question_id=q_id)
                if not ExamQuestion.objects.filter(section=section, question_bank=question).exists():
                    ExamQuestion.objects.create(section=section, question_bank=question)

            return JsonResponse({"message": "Questions updated successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def get_exam_sections(request, int_exam_id):
    sections = ExamSection.objects.filter(internal_exam_id=int_exam_id)
    sections_data = [
        {
            "id": section.section_id,
            "name": section.section_name,
            "numQuestions": section.no_of_questions,
            "numToAnswer": section.no_of_questions_to_be_answered,
            "ceilingMark": section.ceiling_mark,
            "description": section.description
        }
        for section in sections
    ]
    return JsonResponse({"sections": sections_data})

def get_questions_for_section(request, exam_id, section_id):
    try:
        # Fetch all ExamQuestions for the specific section
        exam_questions = ExamQuestion.objects.filter(section_id=section_id)
        
        # Prepare the response data manually
        questions_data = []
        for exam_question in exam_questions:
            question_bank = exam_question.question_bank  # Access related QuestionBank model
            question_data = {
                'question_id': exam_question.q_id,
                'question_text': question_bank.question_text,  # From QuestionBank
                'marks': question_bank.marks , # Marks from QuestionBank
                'co':exam_question.question_bank.co.co_label
            }
            questions_data.append(question_data)
        
        # Return the questions as a response
        return JsonResponse(questions_data,safe=False)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400,safe=False)
    
EXAM_TEMPLATE = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage[margin=1in]{geometry}
\begin{document}
\begin{center}
    \Large\textbf{%s - %s}\\
\end{center}

\begin{flushleft}
\textbf{Date:} %s \quad \textbf{Faculty:} %s \hfill \textbf{Max Marks:} %s \quad \textbf{Duration:} %s mins
\end{flushleft}

%s
\end{document}
"""
def generate_sections_content(sections):
    content = ""
    question_counter = 1  

    for section in sections:
        content += f"\n\\section{{{section['name']}}}\n{section['description']}\n\n"
        content += "\\vspace{1em}\n"

        for question in section["questions"]:
            question_text = question['text'].replace('\n', ' \\\\\n\\hspace*{1.5em}')  # Handle new lines separately
            content += (
                f"\\noindent \\textbf{{Q{question_counter}:}} "
                f"\\hangindent=1.5em {question_text} "
                f"\\hspace*{{\\fill}}[{question['co']}]\n\n"
            )
            question_counter += 1 

    return content

@csrf_exempt
def generate_exam_preview(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            sections_content = generate_sections_content(data['sections'])
            tex_content = EXAM_TEMPLATE % (
                data['exam_name'],
                data['course_name'],
                data['date'],
                data['faculty_name'],
                data['max_marks'],
                data['duration'],
                sections_content
            )

            # Write and compile LaTeX
            with open("exam_temp.tex", "w") as f:
                f.write(tex_content)

            subprocess.run(["pdflatex", "-interaction=nonstopmode", "exam_temp.tex"], 
                         stdout=subprocess.PIPE)

            # Convert to PNG
            subprocess.run(["pdftoppm", "-png", "exam_temp.pdf", "exam_temp"],
                         stdout=subprocess.PIPE)
            os.rename("exam_temp-1.png", "exam_temp.png")

            # Convert to base64
            with open("exam_temp.png", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()

            # Cleanup
            for file in ["exam_temp.aux", "exam_temp.log", "exam_temp.pdf", 
                        "exam_temp.tex", "exam_temp.png"]:
                if os.path.exists(file):
                    os.remove(file)

            return JsonResponse({"image": img_base64})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
@csrf_exempt
def delete_internal_exam(request, exam_id):
    exam = get_object_or_404(InternalExam, int_exam_id=exam_id)
    exam.delete()
    return JsonResponse({"message": "Internal exam deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
def update_exam_section(request, section_id):
    if request.method == "PUT":
        try:
            section = get_object_or_404(ExamSection, section_id=section_id)
            data = json.loads(request.body)

            section.section_name = data.get("section_name", section.section_name)
            section.no_of_questions = data.get("no_of_questions", section.no_of_questions)
            section.no_of_questions_to_be_answered = data.get("no_of_questions_to_be_answered", section.no_of_questions_to_be_answered)
            section.ceiling_mark = data.get("ceiling_mark", section.ceiling_mark)
            section.description = data.get("description", section.description)

            section.save()

            return JsonResponse({
                "message": "Section updated successfully",
                "section": {
                    "section_id": section.section_id,
                    "section_name": section.section_name,
                    "no_of_questions": section.no_of_questions,
                    "no_of_questions_to_be_answered": section.no_of_questions_to_be_answered,
                    "ceiling_mark": section.ceiling_mark,
                    "description": section.description,
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# Initialize GPT-4 client (g4f)
client = Client()

def extract_text_from_pdf(pdf_path):
    """Extracts text from the uploaded PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text


def generate_questions_from_text(text, marks=5):
    """Generate questions based on extracted text using GPT-4."""
    prompt = f"""Generate {marks}-mark questions from the following content:\n{text} 
                Return the questions as a JSON array of strings, where each item is a question."""

    # Using g4f's client to call GPT-4 and generate questions
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        web_search=False
    )

    # Extracting and cleaning up the JSON response
    raw_response = response.choices[0].message.content.strip()
    
    # Use regex to extract JSON array from the response
    json_match = re.search(r"\[.*\]", raw_response, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)  # Extract the JSON array as a string
        
        try:
            # Convert JSON string to Python list
            questions_list = json.loads(json_str)
            
            # Format as numbered list for React display
            formatted_questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions_list)])
            return formatted_questions
        
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
            print("Raw Response:", raw_response)
            return "Error: Could not parse questions. Please try again."
    else:
        return "Error: No valid questions found in the response."

@csrf_exempt
def upload_pdf(request):
    """Handles PDF upload, extracts text, and generates questions."""
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf = request.FILES["pdf"]
        marks = int(request.POST.get("marks", 5))  # Default to 5 marks

        # Ensure the "uploads" directory exists
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the PDF file
        saved_path = os.path.join(upload_dir, pdf.name)
        with open(saved_path, "wb") as f:
            for chunk in pdf.chunks():
                f.write(chunk)

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(saved_path)

        # Generate questions based on the extracted text
        questions = generate_questions_from_text(extracted_text, marks)

        # Return the generated questions as a response
        return JsonResponse({"questions": questions})

    return JsonResponse({"error": "Invalid request"}, status=400)
def get_dashboard_stats(request):
    stats = {
        "faculty": Faculty.objects.count(),
        "courses": Course.objects.count(),
        "batches": Batch.objects.count(),
        "students": Student.objects.count(),
        "levels": Level.objects.count(),
        "programmes": Programme.objects.count(),
    }
    return JsonResponse(stats)

@csrf_exempt
def upload_student_data(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_path = default_storage.save("uploads/" + uploaded_file.name, uploaded_file)

        try:
            # Read CSV file
            df = pd.read_csv(file_path, encoding="utf-8")

            # Normalize column names (convert to lowercase & strip spaces)
            df.columns = df.columns.str.strip().str.lower()

            for _, row in df.iterrows():
                programme_name = row.get("programme")
                register_no = row.get("examination register number")
                admission_no = row.get("admission no.")
                name = row.get("name")

                if not all([programme_name, register_no, admission_no, name]):
                    continue  # Skip rows with missing required data

                programme, _ = Programme.objects.get_or_create(programme_name=programme_name)
                print('p-',programme)
                print("reg_no=",register_no)
                # Extract year of admission from register number (e.g., "NA24ECORO50" -> 2024)
                year_of_admission = 2000 + int(register_no[2:4])
                
                print("yoa",year_of_admission)

                Student.objects.update_or_create(
                    admn_no=admission_no,
                    defaults={
                        "register_no": register_no,
                        "name": name,
                        "year_of_admission": year_of_admission,
                        "programme": programme,
                    },
                )

            os.remove(file_path)  # Clean up the uploaded file
            return JsonResponse({"message": "Students added successfully"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def upload_courses_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({'error': 'Invalid file format. Please upload a CSV file.'}, status=400)

            # Read CSV file into pandas DataFrame
            df = pd.read_csv(io.StringIO(csv_file.read().decode('utf-8')))

            required_columns = {'course_code', 'course_title', 'dept_name', 'sem', 'credits', 'syllabus_year'}
            if not required_columns.issubset(df.columns):
                return JsonResponse({'error': 'Invalid CSV format. Required columns: course_code, course_title, dept_name, sem, credits, syllabus_year'}, status=400)

            courses_to_create = []
            for _, row in df.iterrows():
                try:
                    department = Department.objects.get(dept_name=row['dept_name'])  # Get Department instance
                    course = Course(
                        course_code=row['course_code'],
                        title=row['course_title'],
                        dept=department,  # Assign the Department instance
                        semester=row['sem'],
                        credits=row['credits'],
                        syllabus_year=row['syllabus_year'],
                        no_of_cos=1  # Default value
                    )
                    courses_to_create.append(course)
                except ObjectDoesNotExist:
                    return JsonResponse({'error': f'Department with name "{row["dept_name"]}" does not exist.'}, status=400)

            Course.objects.bulk_create(courses_to_create)  # Bulk insert all courses at once
            return JsonResponse({'message': 'Courses uploaded successfully!'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

class FacultyCSVUploadView(APIView):
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        try:
            df = pd.read_csv(file, dtype=str)

            created_faculty = []
            skipped_faculty = []

            for _, row in df.iterrows():
                name = str(row.get("name", "")).strip()
                designation = str(row.get("designation_name", "")).strip()
                dept_name = str(row.get("dept_name", "")).strip()
                email = str(row.get("email", "")).strip()
                phone_no = str(row.get("mob", "")).strip() or "123"  # Default password if empty

                # Ignore records without a valid email
                if not email or email.lower() == "nan":
                    continue

                # Check if email already exists
                if Faculty.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
                    skipped_faculty.append(name)
                    continue  # Skip record if email already exists

                # Split name into first and last name
                name_parts = name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Set username as email prefix (before @)
                username = email.split("@")[0]

                # Fetch or create department
                try:
                    department = Department.objects.get(dept_name=dept_name)
                except ObjectDoesNotExist:
                    return Response({"error": f"Department '{dept_name}' does not exist"}, status=400)

                # Create Faculty record
                faculty = Faculty.objects.create(
                    name=name,
                    dept=department,
                    email=email,
                    phone_no=phone_no
                )
                created_faculty.append(faculty.name)

                # Register user via UserRegistrationView
                user_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "username": username,
                    "password": phone_no,  # Phone number as password
                    "role": "teacher"
                }

                user_view = UserRegistrationView()
                request._request.data = user_data  # Set request data properly
                response = user_view.post(request._request)
 
                if response.status_code != 201:
                    return Response({"error": f"Failed to create user for {name}", "details": response.data}, status=400)

            return Response({
                "message": "Faculty records processed successfully",
                "created": created_faculty,
                "skipped": skipped_faculty
            }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)