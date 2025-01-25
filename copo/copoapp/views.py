from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
import json
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from .models import (
    Faculty,
    Department,
    Student,
    Programme,
    Level,
    Course,
    Batch,
    CustomUser,
)
from django.views.decorators.csrf import csrf_exempt


class UserRegistrationView(APIView):
    def post(self, request):
        data = request.data
        # Assuming you have data to create user and set role
        role = data.get("role", "teacher")  # default to teacher if not provided
        user = CustomUser.objects.create_user(
            username=data["username"], password=data["password"], role=role
        )
        if role == "admin":
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return Response({"message": "User created successfully!"})




class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user  # Get the currently authenticated user
        return Response({
            "username": user.username,  # Return the username
            "role": getattr(user, 'role', 'teacher')  # Return the role if it exists
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
                dept = Department.objects.get(dept_id=data["dept"])
                faculty.dept = dept
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
            faculty.delete()
            return JsonResponse(
                {"message": "Faculty deleted successfully."}, status=200
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
            {"faculty_id": faculty.faculty_id, "name": faculty.name}
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


# Views related to Programme
@csrf_exempt
def add_programme(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            dept = Department.objects.get(dept_id=data["dept"])
            level = Level.objects.get(name=data["level"])
            programme = Programme.objects.create(
                programme_name=data["programme_name"],
                dept=dept,
                no_of_pos=data["no_of_pos"],
                level=level,
                duration=data["duration"],
            )
            return JsonResponse(
                {"message": "Programme created successfully."}, status=201
            )
        except Department.DoesNotExist:
            return JsonResponse({"dept": "Invalid department."}, status=400)
        except Level.DoesNotExist:
            return JsonResponse({"level": "Invalid level."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


def get_programmes(request):
    try:
        programmes = Programme.objects.all()
        programmes_data = [
            {
                "programme_id": programme.programme_id,
                "programme_name": programme.programme_name,
            }
            for programme in programmes
        ]
        return JsonResponse(programmes_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_levels(request):
    try:
        levels = Level.objects.all()
        levels_data = [
            {"level_id": level.level_id, "level_name": level.name} for level in levels
        ]
        return JsonResponse(levels_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Views related to courses
@csrf_exempt
def add_course(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            dept = Department.objects.get(dept_id=data["dept"])
            programme = Programme.objects.get(programme_id=data["programme"])
            course = Course.objects.create(
                course_code=data["course_code"],
                title=data["title"],
                dept=dept,
                semester=data["semester"],
                credits=data["credits"],
                no_of_cos=data["no_of_cos"],
                programme=programme,
                syllabus_year=data["syllabus_year"],
            )
            return JsonResponse({"message": "Course created successfully."}, status=201)
        except Department.DoesNotExist:
            return JsonResponse({"dept": "Invalid department."}, status=400)
        except Programme.DoesNotExist:
            return JsonResponse({"programme": "Invalid programme."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Get all courses
def get_courses(request):
    try:
        course_list = Course.objects.all()
        course_data = [
            {"course_id": course.course_id, "course_code": course.course_code}
            for course in course_list
        ]
        return JsonResponse(course_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def add_batch(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            faculty = Faculty.objects.get(faculty_id=data["faculty_id"])
            course = (
                Course.objects.get(course_id=data["course"]) if data["course"] else None
            )
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
