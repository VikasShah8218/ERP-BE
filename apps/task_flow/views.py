from .serializers import (TaskAssignSerializer,GetTaskAssignSerializer, UserWithLandmarksSerializer,TaskMediaSerializer,
AssosiatedUsersLandmarkCreateUpdateSerializer, AssosiatedUsersLandmarkRetrieveSerializer,
TaskReAllocationCreateUpdateSerializer,TaskReAllocationRetrieveSerializer,
TaskLandmarkCompleteCreateUpdateSerializer,TaskLandmarkCompleteRetrieveSerializer)
from .models import TaskAssign,AssosiatedUsersLandmark,TaskReAllocation,TaskLandmarkComplete,TaskMedia
from utilities.image_size_scale import resize_and_save_image
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
import mimetypes
import tempfile
import asyncio
import time
import cv2


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
        if self.action in ["list", "retrieve"]:  
            return GetTaskAssignSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        assigned_users_ids = data.get("assigned_users", [])
        eligible_users = User.objects.filter(id__in=assigned_users_ids, client_id__isnull=False)
        for user in eligible_users:
            asyncio.run(send_message([user.client_id], str(data.get("name"))+" \n "+str(data.get("note")) + str(int(time.time()))))

        task = serializer.save(created_by=request.user)  
        return Response({"detail": "Task created successfully.", "data": TaskAssignSerializer(task).data},status=status.HTTP_201_CREATED)

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

class TaskReAllocationViewSet(ModelViewSet):
    queryset = TaskReAllocation.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TaskReAllocationRetrieveSerializer 
        return TaskReAllocationCreateUpdateSerializer  

    def create(self, request, *args, **kwargs):
        data = request.data
        if not all(key in data for key in ["task","re_allocate_to"]):
            return Response({"detail": "All fields (task, user, re_allocate_to, message) are required."},status=status.HTTP_400_BAD_REQUEST,)
        
        existing_reallocation = TaskReAllocation.objects.filter(task_id=data["task"], user_id=request.user.id).exists()
        if existing_reallocation:return Response({"detail": "You can't reallocate again."},status=status.HTTP_400_BAD_REQUEST,)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='filter-by-task')
    def filter_by_task(self, request):
        print("*"*50,"Working ","*"*50)
        """
        Filter TaskReAllocation data by task ID and return a user-to-reallocated-user mapping.
        """
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response(
                {"detail": "task_id is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch all reallocations linked to the task ID
        reallocations = TaskReAllocation.objects.filter(task_id=task_id)

        if not reallocations.exists():
            return Response(
                {"detail": "No reallocations found for the given task ID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Build the user-to-reallocate mapping
        user_reallocate_map = {}
        for reallocation in reallocations:
            user_reallocate_map[f"{reallocation.user.username}"] = (f"{reallocation.re_allocate_to.username}")

        # Prepare the response with task details
        task_detail = {
            "task_id": task_id,
            "task_name": reallocations.first().task.name,  # Assuming all entries have the same task
            "user_reallocate_map": user_reallocate_map,
        }

        return Response(task_detail, status=status.HTTP_200_OK)
    
class TaskLandmarkCompleteViewSet(ModelViewSet):
    queryset = TaskLandmarkComplete.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]: 
            return TaskLandmarkCompleteRetrieveSerializer
        return TaskLandmarkCompleteCreateUpdateSerializer 

    def create(self, request, *args, **kwargs):
        data = request.data
        if not all(key in data for key in ["task", "landmark", "is_complete"]):
            return Response(
                {"detail": "All fields (task, landmark, is_complete) are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_record = TaskLandmarkComplete.objects.filter(
            task_id=data["task"], landmark_id=data["landmark"]
        ).exists()

        if existing_record:
            return Response(
                {"detail": "This task-landmark combination already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='filter-by-task')
    def filter_by_task(self, request):
        """
        Filter TaskLandmarkComplete records by task ID.
        """
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response(
                {"detail": "task_id is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        completions = TaskLandmarkComplete.objects.filter(task_id=task_id)

        if not completions.exists():
            return Response({"detail": "No completions found for the given task ID."},status=status.HTTP_404_NOT_FOUND,)

        serializer = self.get_serializer(completions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TaskMediaViewSet(ModelViewSet):
    queryset = TaskMedia.objects.all()
    serializer_class = TaskMediaSerializer

    def get_queryset(self):
        task_id = self.request.query_params.get("task_id")
        if task_id:
            return TaskMedia.objects.filter(task_id=task_id).order_by("-created_on")
        return super().get_queryset()

    # def create(self, request, *args, **kwargs):
    #     task_id = request.data.get("task")
    #     file = request.FILES.get("file")
    #     try:
    #         task = TaskAssign.objects.get(id=task_id)
    #     except TaskAssign.DoesNotExist:
    #         return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        
    #     if task.is_complete:
    #         return Response({"detail": "Task is already completed."}, status=status.HTTP_400_BAD_REQUEST)
        
    #     file_type = None
    #     if file:
    #         mime_type, _ = mimetypes.guess_type(file.name)
    #         if mime_type:
    #             if mime_type.startswith("image"):
    #                 file_type = "image"
    #             elif mime_type.startswith("video"):
    #                 file_type = "video"
    #             elif mime_type.startswith("application/pdf"):
    #                 file_type = "pdf"
    #             else:
    #                 file_type = "other"

    #     if not file_type:
    #         return Response({"detail": "Could not determine file type."}, status=status.HTTP_400_BAD_REQUEST)
        
    #     data = {
    #         "task": task.id,
    #         "file_type": file_type,
    #         "file": file,
    #         "created_by": request.user.id,
    #     }
    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def create(self, request, *args, **kwargs):
        task_id = request.data.get("task")
        file = request.FILES.get("file")
        try:
            task = TaskAssign.objects.get(id=task_id)
        except TaskAssign.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        if task.is_complete:
            return Response({"detail": "Task is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine file type
        file_type = None
        if file:
            mime_type, _ = mimetypes.guess_type(file.name)
            if mime_type:
                if mime_type.startswith("image"):
                    file_type = "image"
                elif mime_type.startswith("video"):
                    file_type = "video"
                elif mime_type.startswith("application/pdf"):
                    file_type = "pdf"
                else:
                    file_type = "other"

        if not file_type:
            return Response({"detail": "Could not determine file type."}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "task": task.id,
            "file_type": file_type,
            "file": file,
            "created_by": request.user.id,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        saved_object = serializer.save()
        thumblane_path = saved_object.file.path.replace(".mp4",".jpg").replace("task_media","thumbnail")
        if file_type == "video":
            cap = cv2.VideoCapture(saved_object.file.path)
            ret, frame = cap.read()
            if ret:
                print("First frame extracted successfully")
                print("*"*20,thumblane_path)
                resize_and_save_image(frame,thumblane_path)
                # cv2.imwrite(thumblane_path, frame)
            else:
                print("Failed to extract the first frame")
            cap.release()

        if file_type=="image":
            output_path = saved_object.file.path.replace("task_media","thumbnail")
            resize_and_save_image(saved_object.file.path,output_path)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Task media deleted successfully."}, status=status.HTTP_200_OK)

