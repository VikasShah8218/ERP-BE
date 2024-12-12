from rest_framework import serializers
from .models import TaskAssign ,AssosiatedUsersLandmark
from apps.accounts.models import User 
from apps.structure.models import Landmark


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = "__all__"
        fields = ['id', 'username', 'first_name','last_name']

class LandmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landmark
        fields = "__all__"


class GetTaskAssignSerializer(serializers.ModelSerializer):
    assigned_users = UserSerializer(many=True)
    landmark = LandmarkSerializer()
    created_by = UserSerializer()
    class Meta:
        model = TaskAssign
        fields = [
            'id', 'name', 'landmark', 'estimate_ex_date', 'note', 'assigned_users',
            'is_started', 'started_on', 'is_complete', 'completed_on', 'conversation',
            'created_on', 'updated_on', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_by', 'updated_by', 'created_on', 'updated_on', 'conversation']

class TaskAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssign
        fields = [
            'id', 'name', 'landmark', 'estimate_ex_date', 'note', 'assigned_users',
            'is_started', 'started_on', 'is_complete', 'completed_on', 'conversation',
            'created_on', 'updated_on', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_by', 'updated_by', 'created_on', 'updated_on', 'conversation']

class TaskConversationSerializer(serializers.ModelSerializer):
    conversation = serializers.CharField()

    class Meta:
        model = TaskAssign
        fields = ['conversation']


class AssosiatedUsersLandmarkCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssosiatedUsersLandmark
        fields = ['id', 'landmark', 'user', 'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']

class AssosiatedUsersLandmarkRetrieveSerializer(serializers.ModelSerializer):
    landmark = LandmarkSerializer()
    user = UserSerializer()

    class Meta:
        model = AssosiatedUsersLandmark
        fields = ['id', 'landmark', 'user', 'created_on', 'updated_on']



class UserWithLandmarksSerializer(serializers.ModelSerializer):
    landmarks = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'landmarks']

    def get_landmarks(self, obj):
        # Fetch associated landmarks for this user
        associated_landmarks = AssosiatedUsersLandmark.objects.filter(user=obj)
        landmarks = [assoc.landmark for assoc in associated_landmarks]
        return LandmarkSerializer(landmarks, many=True).data