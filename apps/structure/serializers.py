from rest_framework import serializers
from .models import Zone, District, Landmark, Junction, Pole, Equipment,LandmarkLog


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class LandmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landmark
        fields = '__all__'


class JunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Junction
        fields = '__all__'


class PoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pole
        fields = '__all__'


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'



class DistrictSerializerLog(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']  # Specify the fields you need

class LandmarkLogSerializer(serializers.ModelSerializer):
    district = DistrictSerializerLog()  # Include the District serializer

    class Meta:
        model = LandmarkLog
        fields = ['id', 'landmark_name', 'district', 'other_fields']