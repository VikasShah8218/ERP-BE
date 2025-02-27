from rest_framework import serializers, viewsets, routers
from django.urls import path, include
from .models import Category, Location,Group,Product,StoreRequest, DailyEntry
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

    def create(self, validated_data): return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class ProductListViewSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id","name", "category", "group", "quantity",  
            "model", "location", "status","product_image"
           ]
    def get_location(self, obj): return obj.location.name
    def get_group(self, obj): return obj.group.name

class ProductViewSerializer(serializers.ModelSerializer):
    # category = serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField()
    # group = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id","name", "description", "category", "group", "price", "quantity",  
            "serial_number", "model", "location", "status",  "created_on",
            "updated_on","product_image",
            "bill_image","other_document"
            ]
        
    # def get_category(self, obj): return obj.category.name
    # def get_location(self, obj): return obj.location.name
    # def get_group(self, obj): return obj.group.name
    def get_created_on(self, obj):
        if obj.created_on: return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")
        return None
    def get_created_on(self, obj):
        if obj.created_on: return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")
        return None
    def get_updated_on(self, obj):
        if obj.updated_on: return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")
        return None
    


class StoreRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreRequest
        fields = '__all__'

class StoreRequestListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    approver = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()

    class Meta:
        model = StoreRequest
        fields = ['id','employee','approver', 'status','created_on','note','subject']
    def get_employee(self, obj): return obj.employee.first_name if obj.employee else None
    def get_approver(self, obj): return obj.approver.first_name if obj.approver else None
    def get_created_on(self, obj): return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")  if obj.created_on else None
    
    
class StoreRequestRetriveSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField() 
    approver = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()

    class Meta:
        model = StoreRequest
        fields = ['id','subject','employee','employee_id','approver_id','approver','items','conversation','note', 'status','created_on']
    def get_employee(self, obj): return obj.employee.first_name if obj.employee else None
    def get_approver(self, obj): return obj.approver.first_name if obj.approver else None
    def get_created_on(self, obj): return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")  if obj.created_on else None


class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        fields = '__all__'

class DailyEntryListSerializer(serializers.ModelSerializer):
    created_on = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    class Meta:
        model = DailyEntry
        fields = ['id','employee','note','location','created_on']

    def get_location(self, obj): return obj.location.name
    def get_employee(self, obj): return obj.employee.first_name
    def get_created_on(self, obj): return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")  if obj.created_on else None
    
class DailyEntryRetriveSerializer(serializers.ModelSerializer):
    created_on = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta:
        model = DailyEntry
        fields = ['id','employee','items','note','location','description','created_on']

    def get_location(self, obj): return obj.location.name
    def get_employee(self, obj): return obj.employee.first_name
    def get_created_on(self, obj): return localtime(obj.created_on).strftime("%Y-%m-%d %I:%M %p")  if obj.created_on else None
    