from .serializers import (CategorySerializer , LocationSerializer ,GroupSerializer,ProductCreateSerializer,StoreRequestRetriveSerializer,
StoreRequestListSerializer,ProductViewSerializer,ProductListViewSerializer,StoreRequestSerializer,DailyEntryListSerializer,DailyEntrySerializer,
DailyEntryRetriveSerializer)
from .models import Category, Location ,Group,Product,StoreRequest,DailyEntry
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import datetime
import json
from .permissions import HasCustomPermission
from rest_framework.exceptions import ValidationError

class Test(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0].strip()  if x_forwarded_for else request.META.get('REMOTE_ADDR')
    def post(self, request, *args, **kwargs):
        client_ip = self.get_client_ip(request)
        return Response({"client_ip": client_ip})
    
    def get(self, request, *args, **kwargs):
        client_ip = self.get_client_ip(request)
        return Response({"client_ip": client_ip})
    
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class ProductGroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [HasCustomPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListViewSerializer
        elif self.action == "retrieve":
            return ProductViewSerializer
        return ProductCreateSerializer
    
    def get_permissions(self):
        print(self.action)
        if self.action == "update":
            self.required_permission = "can_update_product"
        elif self.action == "partial_update":
            self.required_permission = "can_update_product"
        # elif self.action == "destroy":
        #     self.required_permission = "can_delete_product"
        else:
            self.required_permission = None
        return super().get_permissions()

    def get_queryset(self):
        queryset = Product.objects.all()
        
        location_id = self.request.query_params.get("location_id")
        category_id = self.request.query_params.get("category_id")
        group_id = self.request.query_params.get("group_id")
        name = self.request.query_params.get("name")
        
        if location_id: queryset = queryset.filter(location_id=location_id)
        if category_id: queryset = queryset.filter(category_id=category_id)
        if group_id   : queryset = queryset.filter(group_id=group_id)
        if name       : queryset = queryset.filter(name__icontains=name)

        return queryset
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.check_permissions(request)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

class StoreRequestViewSet(ModelViewSet):
    queryset = StoreRequest.objects.all().order_by("-id")
    serializer_class = StoreRequestSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return StoreRequestListSerializer
        elif self.action == "retrieve":
            return StoreRequestRetriveSerializer
        return StoreRequestSerializer
        
    def get_queryset(self):
        queryset = StoreRequest.objects.all().order_by("-id")
        created_on = self.request.query_params.get("date")
        status = self.request.query_params.get("status")
        search_status = int(status) if status is not None and status.isdigit() and int(status) in [0, 1, 2, 3] else None
        if created_on and search_status != None :
            try:  queryset = queryset.filter(created_on__date=datetime.strptime(created_on, "%Y-%m-%d").date(),status=search_status)
            except ValueError: return queryset.none()
        if created_on :
            try:  queryset = queryset.filter(created_on__date=datetime.strptime(created_on, "%Y-%m-%d").date())
            except ValueError: return queryset.none()
        return queryset
    
    def create(self, request, *args, **kwargs):
        request.data["employee"] = request.user.id
        items = request.data.get("items", {})
        if not isinstance(items, dict):
            return Response({"detail": "Items should be in dictionary format with indexes as keys."}, status=400)
        
        for key, value in items.items():
            if not isinstance(value, dict) or not all(k in value for k in ["name", "model", "design", "color"]):
                return Response({"detail": f"Invalid structure for item {key}. Each item must contain 'name', 'model', 'design', and 'color'."}, status=400)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['patch'], url_path='add-conversation')
    def add_conversation(self, request, *args, **kwargs):
        store_request = self.get_object()
        user = request.user.first_name
        new_message = request.data.get("conversation", "")

        if not new_message: return Response({"detail": "Message cannot be empty."}, status=400)

        if isinstance(store_request.conversation, str):
            try: store_request.conversation = json.loads(store_request.conversation)
            except json.JSONDecodeError: store_request.conversation = {}

        conversation_log = store_request.conversation or {}
        conversation_count = len(conversation_log) + 1
        timestamp = timezone.now().strftime("%Y-%m-%d %I:%M %p")

        # Append new conversation
        conversation_log[conversation_count] = {"user": user, "message": new_message, "timestamp": timestamp}
        store_request.conversation = conversation_log
        store_request.save()

        return Response({"detail": "Conversation updated successfully.", "conversation": store_request.conversation}, status=200)
    
    @action(detail=True, methods=['patch'], url_path='change-status', permission_classes=[HasCustomPermission])
    def change_status(self, request, *args, **kwargs):
        self.required_permission = "can_approve_request"
        self.check_permissions(request)
        store_request = self.get_object()
        user = request.user.first_name
        status = request.data.get("status", "")

        if not status:return Response({"detail": "Status cannot be empty."}, status=400)

        store_request.status = status
        store_request.save()

        return Response({"detail": "Status Updated."}, status=200)
    

class StoreDailyEntryViewSet(ModelViewSet):
    queryset = DailyEntry.objects.all().order_by("-id")
    serializer_class = DailyEntrySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return DailyEntryListSerializer
        elif self.action == "retrieve":
            return DailyEntryRetriveSerializer
        return DailyEntrySerializer
        
    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date != None and end_date != None:
            try:
                print("Running ")
                print(start_date,end_date)
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                return queryset.filter(created_on__date__gte=start_date, created_on__date__lte=end_date)
            except ValueError:
                raise ValidationError({"detail": "Invalid date format. Use 'YYYY-MM-DD'."})
        return queryset


    def create(self, request, *args, **kwargs):
        request.data["employee"] = request.user.id
        items = request.data.get("items", {})
        if not isinstance(items, dict):
            return Response({"detail": "Items should be in dictionary format with indexes as keys."}, status=400)
        
        for key, value in items.items():
            if not isinstance(value, dict) or not all(k in value for k in ["name", "model", "design"]):
                return Response({"detail": f"Invalid structure for item {key}. Each item must contain 'name', 'model', 'design'"}, status=400)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['patch'], url_path='add-conversation')
    def add_conversation(self, request, *args, **kwargs):
        store_request = self.get_object()
        user = request.user.first_name
        new_message = request.data.get("conversation", "")

        if not new_message: return Response({"detail": "Message cannot be empty."}, status=400)

        if isinstance(store_request.conversation, str):
            try: store_request.conversation = json.loads(store_request.conversation)
            except json.JSONDecodeError: store_request.conversation = {}

        conversation_log = store_request.conversation or {}
        conversation_count = len(conversation_log) + 1
        timestamp = timezone.now().strftime("%Y-%m-%d %I:%M %p")

        # Append new conversation
        conversation_log[conversation_count] = {"user": user, "message": new_message, "timestamp": timestamp}
        store_request.conversation = conversation_log
        store_request.save()

        return Response({"detail": "Conversation updated successfully.", "conversation": store_request.conversation}, status=200)
    
    @action(detail=True, methods=['patch'], url_path='change-status', permission_classes=[HasCustomPermission])
    def change_status(self, request, *args, **kwargs):
        self.required_permission = "can_approve_request"
        self.check_permissions(request)
        store_request = self.get_object()
        user = request.user.first_name
        status = request.data.get("status", "")

        if not status:return Response({"detail": "Status cannot be empty."}, status=400)

        store_request.status = status
        store_request.save()

        return Response({"detail": "Status Updated."}, status=200)
