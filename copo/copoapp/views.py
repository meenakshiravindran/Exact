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
    PO,
    CO,
)
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
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
        if not all([username, password, email, first_name, last_name]):
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
        required_fields = ["title", "dept", "course_code","syllabus_year","programme","no_of_cos","semester","credits"]
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
        
        try:
            programme = Programme.objects.get(programme_name=data["programme"])
        except ObjectDoesNotExist:
            return Response(
                {"programme": "The specified department does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Course instance
        course = Course(
            title=data["title"],
            dept=department,  # Assign the Department instance
            course_code=data["course_code"],
            syllabus_year=data["syllabus_year"],
            programme=programme,
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
            if "course_name" in data:
                course.title = data["course_name"]
            if "dept" in data:
                dept = Department.objects.get(dept_name=data["dept"])
                course.dept = dept
            if "course_code" in data:
                course.course_code = data["course_code"]
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
                "programme":course.programme.programme_name,
                "syllabus_year":course.syllabus_year,
                "no_of_cos":course.no_of_cos

            }
            return JsonResponse(course_data, status=200)
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)



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
        required_fields = ["programme_name", "department", "level", "no_of_pos", "duration"]
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
            "programme": student.programme.programme_name,  # Assuming Programme model has an ID field
            "year_of_admission": student.year_of_admission,
            "phone_number": student.phone_number,
            "email": student.email,
        }, status=200)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)

def get_students_by_programme(request, programme_id):
    if request.method == "GET":
        programme = get_object_or_404(Programme, programme_id=programme_id)
        students = Student.objects.filter(programme=programme).values(
            "student_id", "name", "register_no", "year_of_admission", "phone_number", "email"
        )
        return JsonResponse(list(students), safe=False, status=200)
    
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
            if "programme" in data:
                programme = Programme.objects.get(programme_name=data["programme"])
                po.programme = programme
            if "pos_description" in data:
                po.pos_description = data["pos_description"]
            if "level" in data:
                level = Level.objects.get(id=data["level"])
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

def get_pos(request):
    try:
        pos_list = PO.objects.all()
        pos_data = [
            {
                "id": po.id,
                "programme": po.programme.programme_name,
                "pos_description": po.pos_description,
                "level": po.level.id,
            }
            for po in pos_list
        ]
        return JsonResponse(pos_data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def get_po_details(request, po_id):
    if request.method == "GET":
        try:
            po = PO.objects.get(id=po_id)
            po_data = {
                "id": po.id,
                "programme": po.programme.programme_name,
                "pos_description": po.pos_description,
                "level": po.level.id,
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

        # Ensure the selected taxonomy field is valid
        selected_taxonomy = data["bloom_taxonomy"].lower()
        if selected_taxonomy not in taxonomy_values:
            return Response(
                {"bloom_taxonomy": "Invalid taxonomy selection."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set the selected taxonomy field to 1
        taxonomy_values[selected_taxonomy] = 1

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

# Edit a CO
@csrf_exempt
def edit_co(request, co_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            co = CO.objects.get(co_id=co_id)
            if "co_number" in data:
                co.co_number = data["co_number"]
            if "description" in data:
                co.description = data["description"]
            if "course_id" in data:
                course = Course.objects.get(course_id=data["course_id"])
                co.course = course
            co.save()
            return JsonResponse(
                {"message": "Course Outcome updated successfully."}, status=200
            )
        except CO.DoesNotExist:
            return JsonResponse({"error": "Course Outcome not found."}, status=404)
        except Course.DoesNotExist:
            return JsonResponse({"course_id": "Invalid course ID."}, status=400)
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
                "co_number": co.co_number,
                "description": co.description,
                "course": co.course.title,
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
                "co_number": co.co_number,
                "description": co.description,
                "course": co.course.title,
            }
            return JsonResponse(co_data, status=200)
        except CO.DoesNotExist:
            return JsonResponse({"error": "Course Outcome not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)
