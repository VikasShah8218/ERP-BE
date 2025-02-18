from .serializers import CategorySerializer , LocationSerializer ,GroupSerializer,ProductCreateSerializer,StoreRequestRetriveSerializer,StoreRequestListSerializer,ProductViewSerializer,ProductListViewSerializer,StoreRequestSerializer
from .models import Category, Location ,Group,Product,StoreRequest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from django.utils import timezone
import json

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

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListViewSerializer
        elif self.action == "retrieve":
            return ProductViewSerializer
        return ProductCreateSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        location_id = self.request.query_params.get("location_id")
        category_id = self.request.query_params.get("category_id")
        group_id = self.request.query_params.get("group_id")
        print( self.request.query_params)
        if location_id: queryset = queryset.filter(location_id=location_id)
        if category_id: queryset = queryset.filter(category_id=category_id)
        if group_id   : queryset = queryset.filter(group_id=group_id)

        return queryset
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

class StoreRequestViewSet(ModelViewSet):
    queryset = StoreRequest.objects.all()
    serializer_class = StoreRequestSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return StoreRequestListSerializer
        elif self.action == "retrieve":
            return StoreRequestRetriveSerializer
        return StoreRequestSerializer
    
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
    
    @action(detail=True, methods=['patch'], url_path='change-status')
    def change_status(self, request, *args, **kwargs):
        store_request = self.get_object()
        user = request.user.first_name
        status = request.data.get("status", "")

        if not status:return Response({"detail": "Status cannot be empty."}, status=400)

        store_request.status = status
        store_request.save()

        return Response({"detail": "Status Updated."}, status=200)
