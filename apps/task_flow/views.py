from .serializers import (TaskAssignSerializer,GetTaskAssignSerializer, UserWithLandmarksSerializer,TaskMediaSerializer,
AssosiatedUsersLandmarkCreateUpdateSerializer, AssosiatedUsersLandmarkRetrieveSerializer,
TaskReAllocationCreateUpdateSerializer,TaskReAllocationRetrieveSerializer,
TaskLandmarkCompleteCreateUpdateSerializer,TaskLandmarkCompleteRetrieveSerializer)
from .models import TaskAssign,AssosiatedUsersLandmark,TaskReAllocation,TaskLandmarkComplete,TaskMedia
from django.db.models import Case, When, Value, IntegerField
from utilities.image_size_scale import resize_and_save_image
from utilities.send_message import send_message_task
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.structure.models import Landmark
from rest_framework.views import APIView
from apps.accounts.models import User
from django.http import JsonResponse
from ws.utils import send_message
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
    
    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:  
            return GetTaskAssignSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        user_id = self.request.user.id
        queryset = TaskAssign.objects.raw(f''' SELECT t.*, u.user_id FROM public.tbl_task_assign t LEFT JOIN (SELECT taskassign_id, user_id FROM  tbl_task_assign_assigned_users WHERE user_id = {user_id}) u ON t.id = u.taskassign_id WHERE is_private = false or ( is_private = true and user_id = {user_id} ) ORDER BY  user_id ASC ,updated_on DESC  ''')
        return queryset
    
    def get_object(self):
        user_id = self.request.user.id
        queryset = TaskAssign.objects.get(id=self.kwargs.get('pk'))
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data["assigned_users"].append(request.user.id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        assigned_users_ids = data.get("assigned_users", [])
        eligible_users = User.objects.filter(id__in=assigned_users_ids, client_id__isnull=False)
        client_id,users_name = [], ""
        for user in eligible_users:
            if user.client_id:
                client_id.append(user.client_id) 
                users_name += (str(user.first_name)+"\n")
        if len(client_id)>0: send_message_task.delay(client_id, str(data.get("name"))+"\n"+str(data.get("note"))+"\n"+users_name)
        task = serializer.save(created_by=request.user)
        send_message({"EVENT":"New Task was Created"})  
        return Response({"detail": "Task created successfully.", "data": TaskAssignSerializer(task).data},status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='accept-task')
    def task_accepted(self, request, pk=None):
        task = self.get_object()
        data = request.data

        if not task.assigned_users.filter(id=request.user.id).exists():
            return Response({"detail": "You are not assosiated with this task"},status=status.HTTP_403_FORBIDDEN)
        
        if task.depends_on and not task.depends_on.is_complete:
            return Response(
                {"detail": f"{task.depends_on.name} is not completed yet, first complete that task."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if task.is_started: return Response({"detail": "Task is already accepted."}, status=status.HTTP_400_BAD_REQUEST)
        task.updated_by = request.user
        task.is_started = True
        task.conversation = (task.conversation or "") + f"\n {request.user.username}  : {data.get('conversation', '')}"
        task.started_on = timezone.now()
        task.save()

        client_id = task.assigned_users.values_list('client_id', flat=True).filter(client_id__isnull=False)
        if client_id:
            message = (
                f"{task.name}\n"
                f"Accepted: {request.user.username}\n"
                f"Details \n {data.get('conversation', '')} \n"
            )
            send_message_task.delay(list(client_id), message)
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
        send_message({"CONVERSATION":"New message"})  
        return Response({"detail": "Message Send"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='complete-task')
    def task_completed(self, request, pk=None):
        """
        Mark a task as completed and update the conversation field.
        """
        task = self.get_object()

        if not task.assigned_users.filter(id=self.request.user.id).exists():  return Response({'detail':"You are not Assigned in this task"},status=status.HTTP_404_NOT_FOUND)
        if task.is_complete : return Response({'detail':"Task is Completed"},status=status.HTTP_409_CONFLICT)
        if task.depends_on and not task.depends_on.is_complete:
            return Response({"detail": f"{task.depends_on.name} is not completed yet, first complete that task."},status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        task.is_complete = True
        task.conversation = (task.conversation or "") + f"\n {request.user.username} : {data.get('conversation', '')}"
        task.completed_on = timezone.now()  # Ensure you import `timezone` from Django
        task.updated_by = request.user
        task.save()
        return Response({"detail": "Task marked as completed."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='update-users')
    def update_users(self, request, pk=None):
            """
            Add or remove users from the task's assigned_users.
            Return lists of already existing users and non-existing users.
            """
            task = self.get_object()
            if task.assigned_users.filter(id=self.request.user.id).exists():
                pass
            else:
                return Response({'detail':"You are not Assigned in this task"},status=status.HTTP_404_NOT_FOUND)
            
            if task.is_complete :
                return Response({'detail':"Task is Completed"},status=status.HTTP_409_CONFLICT)
            user_ids_to_add = request.data.get("add_users", [])
            user_ids_to_remove = request.data.get("remove_users", [])

            if task.created_by in user_ids_to_add or request.user.id in user_ids_to_remove:
                return Response({'detail':"You can't remove Task Creator"},status=status.HTTP_403_FORBIDDEN)

            already_assigned_users = []
            non_existing_users = []
            if task.depends_on and not task.depends_on.is_complete:
                return Response(
                    {"detail": f"{task.depends_on.name} \n is not completed yet, first complete that task."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            added_users = ""
            if user_ids_to_add:
                users_to_add = User.objects.filter(id__in=user_ids_to_add)
                existing_user_ids = set(task.assigned_users.values_list('id', flat=True))
                for user in users_to_add:
                    if user.id in existing_user_ids:
                        already_assigned_users.append(user.id)
                    else:
                        added_users += (user.first_name + ",  ")
                        task.assigned_users.add(user)

            removed_user = ""
            if user_ids_to_remove:
                existing_user_ids = set(task.assigned_users.values_list('id', flat=True))
                for user_id in user_ids_to_remove:
                    if user_id not in existing_user_ids:
                        non_existing_users.append(user_id)
                    else:
                        user = User.objects.filter(id=user_id).first()
                        if user:
                            removed_user += (user.first_name + ",  ")
                            task.assigned_users.remove(user)

            task.updated_by = request.user
            task.save()
            client_id = task.assigned_users.values_list('client_id', flat=True).filter(client_id__isnull=False)
            if user_ids_to_add and client_id:
                message = (
                    f"---{task.name}--- \n \n"
                    f"{request.user.username} Add User { added_users }\n \n \n"
                )
                send_message_task.delay(list(client_id), message)

            if user_ids_to_remove and client_id:
                message = (
                    f"---{task.name}--- \n \n"
                    f"{request.user.username} Remove User { removed_user }\n \n \n"
                )
                send_message_task.delay(list(client_id), message)

            return Response({
                "detail": "Users updated successfully.",
                "assigned_users": list(task.assigned_users.values_list('id', flat=True)),
                "already_assigned_users": already_assigned_users,
                "non_existing_users": non_existing_users
            }, status=status.HTTP_200_OK)

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
        try:
            task = TaskAssign.objects.get(id=data["task"])
            if task.is_complete:
                return Response({"detail": "Task is already completed. You cannot reallocate."}, status=status.HTTP_400_BAD_REQUEST)
        except TaskAssign.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        
        existing_reallocation = TaskReAllocation.objects.filter(task_id=data["task"], user_id=request.user.id).exists()
        if existing_reallocation:return Response({"detail": "You can't reallocate again."},status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        data["detail"] = "Re-Allocated"
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='filter-by-task')
    def filter_by_task(self, request):
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
        data["is_complete"] = True
        if not all(key in data for key in ["task", "landmark"]):
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
        data = serializer.data
        data["detail"] = "Landmark Completed"
        return Response(data, status=status.HTTP_201_CREATED)

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

    def create(self, request, *args, **kwargs):
        task_id = request.data.get("task")
        try:
            task = TaskAssign.objects.get(id=task_id)
            if task.depends_on and not task.depends_on.is_complete:
                return Response(
                    {"detail": f"{task.depends_on.name} is not completed yet, first complete that task."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except TaskAssign.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


        if not task.assigned_users.filter(id=self.request.user.id).exists():  return Response({'detail':"You are not Assigned in this task"},status=status.HTTP_404_NOT_FOUND)
        if task.is_complete : return Response({'detail':"Task is Completed"},status=status.HTTP_409_CONFLICT)

        # Determine file type
        file = request.FILES.get("file")
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
                    file_type = False

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
        data =  serializer.data
        data["detail"] = "File Uploaded"
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Task media deleted successfully."}, status=status.HTTP_200_OK)

