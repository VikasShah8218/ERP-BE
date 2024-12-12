from .serializers import (TaskAssignSerializer,GetTaskAssignSerializer, 
AssosiatedUsersLandmarkCreateUpdateSerializer, AssosiatedUsersLandmarkRetrieveSerializer,
UserWithLandmarksSerializer)
from .models import TaskAssign,AssosiatedUsersLandmark
from rest_framework.viewsets import ModelViewSet
from utilities.send_message import send_message
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.structure.models import Landmark
from rest_framework.views import APIView
from apps.accounts.models import User
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from django.db.models import Q
import asyncio
import time


class Test(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0].strip()  if x_forwarded_for else request.META.get('REMOTE_ADDR')
    def post(self, request, *args, **kwargs):
        client_ip = self.get_client_ip(request)
        return Response({"client_ip": client_ip})

class TaskAssignViewSet(ModelViewSet):

    queryset = TaskAssign.objects.all()
    serializer_class = TaskAssignSerializer
    def get_queryset(self):
        return TaskAssign.objects.all().order_by("-updated_on")
    
    def get_serializer_class(self):
        """
        Dynamically select serializer based on the HTTP method.
        """
        if self.action in ["list", "retrieve"]:  # For GET requests (list and detail)
            return GetTaskAssignSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """
        Create a new task and set the creator.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        assigned_users_ids = data.get("assigned_users", [])
        eligible_users = User.objects.filter(id__in=assigned_users_ids, client_id__isnull=False)
        # asyncio.run(send_message(['1399188883'],f"Mr Shah is testing: {int(time.time())}"))
        for user in eligible_users:
            asyncio.run(send_message([user.client_id], str(data.get("name"))+" \n "+str(data.get("note")) + str(int(time.time()))))

        task = serializer.save(created_by=request.user)  
        return Response({"detail": "Task created successfully.", "data": TaskAssignSerializer(task).data},status=status.HTTP_201_CREATED)
        # return Response({"detail": "Task created successfully."},status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='accept-task')
    def task_accepted(self, request, pk=None):
        """
        Mark a task as accepted and update related fields.
        """
        task = self.get_object()
        data = request.data
        task.updated_by = request.user
        task.is_started = True
        task.conversation = (task.conversation or "") + f"\n {request.user.username}  : {data.get('conversation', '')}"
        task.started_on = timezone.now()
        task.save()
        return Response({"detail": "Task accepted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='add-conversation')
    def conversation(self, request, pk=None):
        """
        Append to the task conversation with the current user's name.
        """
        task = self.get_object()
        new_conversation = request.data.get("conversation", "")
        if not new_conversation:
            return Response({"detail": "Conversation content is required."}, status=status.HTTP_400_BAD_REQUEST)
        task.conversation = (task.conversation or "") + f"\n {request.user.username} : {new_conversation}"
        task.updated_by = request.user
        task.save()
        return Response({"detail": "Conversation added successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='complete-task')
    def task_completed(self, request, pk=None):
        """
        Mark a task as completed and update the conversation field.
        """
        task = self.get_object()
        data = request.data
        task.is_complete = True
        task.conversation = (task.conversation or "") + f"\n {request.user.username} : {data.get('conversation', '')}"
        task.completed_on = timezone.now()  # Ensure you import `timezone` from Django
        task.updated_by = request.user
        task.save()
        return Response({"detail": "Task marked as completed."}, status=status.HTTP_200_OK)
    

class AssosiatedUsersLandmarkViewSet(ModelViewSet):
    queryset = AssosiatedUsersLandmark.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:  # For GET actions
            return AssosiatedUsersLandmarkRetrieveSerializer
        return AssosiatedUsersLandmarkCreateUpdateSerializer  # For POST, PUT, PATCH, DELETE

    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get("user_id")
        landmark_ids = data.get("landmarks", [])

        if not user_id or not landmark_ids:return Response({"detail": "Both 'user_id' and 'landmarks' are required."},status=status.HTTP_400_BAD_REQUEST,)

        try: user = User.objects.get(id=user_id)
        except User.DoesNotExist:return Response({"detail": f"User with id {user_id} does not exist."},status=status.HTTP_404_NOT_FOUND,)

        landmarks = Landmark.objects.filter(id__in=landmark_ids)
        if landmarks.count() != len(landmark_ids):return Response({"detail": "One or more landmark IDs are invalid."},status=status.HTTP_400_BAD_REQUEST,)

        associated_records = []
        for landmark in landmarks:
            associated_record, created = AssosiatedUsersLandmark.objects.get_or_create(
                user=user,
                landmark=landmark,
                defaults={"created_by": request.user},
            )
            associated_records.append(associated_record)

        return Response({"detail": "Associations created successfully."},status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """
        Automatically set the `updated_by` field during update operations.
        """
        serializer.save(updated_by=self.request.user)


class UsersWithLandmarksViewSet(ModelViewSet):
    def list(self, request):
        users = User.objects.all()
        serializer = UserWithLandmarksSerializer(users, many=True)
        return Response(serializer.data)