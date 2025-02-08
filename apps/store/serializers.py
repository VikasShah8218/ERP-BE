from rest_framework import serializers, viewsets, routers
from django.urls import path, include
from .models import Category, Location,Group,Product
from django.utils.timezone import localtime

# Serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProductViewSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "name", "description", "category", "group", "price", "quantity",  
            "serial_number", "model", "location", "status",  "created_on",
            "updated_on","category_id","location_id","group_id","product_image",
            "bill_image","other_document"
            ]
        
    def get_category(self, obj):
        return obj.name
    def get_location(self, obj):
        return obj.name
    def get_group(self, obj):
        return obj.name
    def get_created_on(self, obj):
        if obj.created_on: return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")
        return None
    def get_created_on(self, obj):
        if obj.created_on: return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")
        return None
    def get_updated_on(self, obj):
        if obj.created_on: return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")
        return None