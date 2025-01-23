from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import JsonResponse
import json
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from .models import Faculty, Department

class HomeView(APIView):  
   permission_classes = (IsAuthenticated, )
   def get(self, request):
       content = {'message': 'Welcome to the JWT Authentication page using React Js and Django!'}
       return Response(content)
  
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
          
          

class FacultyView(APIView):
    def post(self, request):
        data = request.data

        # Manual validation
        required_fields = ['name', 'department', 'email', 'phone_number']
        for field in required_fields:
            if field not in data:
                return Response({field: 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(data['email'])
        except ValidationError:
            return Response({'email': 'Enter a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for unique email
        if Faculty.objects.filter(email=data['email']).exists():
            return Response({'email': 'A faculty member with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the Department instance
        try:
            department = Department.objects.get(dept_name=data['department'])
        except ObjectDoesNotExist:
            return Response({'department': 'The specified department does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Faculty instance
        faculty = Faculty(
            name=data['name'],
            dept=department,  # Assign the Department instance
            email=data['email'],
            phone_no=data['phone_number']
        )
        faculty.save()

        return Response({'message': 'Faculty member created successfully.'}, status=status.HTTP_201_CREATED)