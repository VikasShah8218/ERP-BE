from .serializers import (ZoneSerializer,DistrictSerializer, LandmarkSerializer,JunctionSerializer,PoleSerializer, EquipmentSerializer,)
from .models import Zone, District, Landmark, Junction, Pole, Equipment
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Q
import datetime
from .log import *

class Test(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0].strip()  if x_forwarded_for else request.META.get('REMOTE_ADDR')
    def post(self, request, *args, **kwargs):
        client_ip = self.get_client_ip(request)
        return Response({"client_ip": client_ip})
    
class BaseViewSet(ModelViewSet):
    """
    A base viewset to handle soft-deleted records with is_delete checks.
    """

    def get_queryset(self):
        """
        Override get_queryset to include deleted records for specific actions.
        """
        if self.action == "undelete":
            # Include all records for the undelete action
            return super().get_queryset()
        # Exclude deleted records for all other actions
        return super().get_queryset().filter(is_delete=False)
    
    def get_object(self):
        """
        Override get_object to allow access to soft-deleted objects for the `undelete` action.
        """
        obj = super().get_object()
        if obj.is_delete and self.action != "undelete":
            raise Response({"detail": "Selected object is deleted."}, status=status.HTTP_404_NOT_FOUND)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_delete:
            return Response({"detail": "Selected object is deleted."}, status=status.HTTP_404_NOT_FOUND)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_delete:
            return Response({"detail": "Selected object is deleted."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_delete:
            return Response({"detail": "Selected object is deleted."}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_delete:
            return Response({"detail": "Selected object is already deleted."}, status=status.HTTP_400_BAD_REQUEST)
        # Soft delete the record by setting is_delete to True
        instance.is_delete = True
        instance.save()
        return Response({"detail": "Object deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='undelete')
    def undelete(self, request, pk=None):
        """
        Endpoint to undelete a soft-deleted record.
        """
        instance = self.get_object()
        if not instance.is_delete:
            return Response({"detail": "Selected object is not deleted."}, status=status.HTTP_400_BAD_REQUEST)
        
        # previous_values = get_model_data(instance)
        # current_values = get_model_data(instance)

        # ZoneLog.objects.create(
        #     zone=instance,
        #     action='undelete',
        #     previous_values=previous_values,
        #     current_values=current_values
        # )
        instance.is_delete = False
        instance.save()
        return Response({"detail": "Object restored successfully."}, status=status.HTTP_200_OK)


class ZoneViewSet(BaseViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer


class DistrictViewSet(BaseViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class LandmarkViewSet(BaseViewSet):
    queryset = Landmark.objects.all()
    serializer_class = LandmarkSerializer


class JunctionViewSet(BaseViewSet):
    queryset = Junction.objects.all()
    serializer_class = JunctionSerializer


class PoleViewSet(BaseViewSet):
    queryset = Pole.objects.all()
    serializer_class = PoleSerializer


class EquipmentViewSet(BaseViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class FilterLogsByDate(APIView):
    def get(self, request):  # Add self here
        date_str = request.GET.get("date")
        if not date_str:
            return JsonResponse({'detail': "Date parameter is required."}, status=400)
        try:
            # Parse the date from the client
            filter_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            return JsonResponse({'detail': "Invalid date format. Use DD-MM-YYYY."}, status=400)

        start_of_day = timezone.make_aware(datetime.datetime.combine(filter_date, datetime.datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.datetime.combine(filter_date, datetime.datetime.max.time()))

        # Filter logs for each model by the date range
        zone_logs = ZoneLog.objects.filter(timestamp__range=(start_of_day, end_of_day)).values()
        pole_logs = PoleLog.objects.filter(timestamp__range=(start_of_day, end_of_day)).values()
        equipment_logs = EquipmentLog.objects.filter(timestamp__range=(start_of_day, end_of_day)).values()
        district_logs = DistrictLog.objects.filter(timestamp__range=(start_of_day, end_of_day)).values()
        landmark_logs = LandmarkLog.objects.filter(timestamp__range=(start_of_day, end_of_day)).values()

        data = {
            "zones": list(zone_logs),
            "poles": list(pole_logs),
            "equipments": list(equipment_logs),
            "districts": list(district_logs),
            "landmarks": list(landmark_logs),
        }
        return JsonResponse(data, safe=False)
