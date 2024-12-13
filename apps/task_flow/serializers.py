from .models import TaskAssign ,AssosiatedUsersLandmark,TaskReAllocation
from apps.structure.models import Landmark
from rest_framework import serializers
from apps.accounts.models import User 


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
    landmarks = LandmarkSerializer(many=True)
    created_by = UserSerializer()
    class Meta:
        model = TaskAssign
        fields = [
            'id', 'name', 'landmarks', 'estimate_ex_date', 'note', 'assigned_users',
            'is_started', 'started_on', 'is_complete', 'completed_on', 'conversation',
            'created_on', 'updated_on', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_by', 'updated_by', 'created_on', 'updated_on', 'conversation']

class TaskAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssign
        fields = [
            'id', 'name', 'landmarks', 'estimate_ex_date', 'note', 'assigned_users',
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
    

class TaskReAllocationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReAllocation
        fields = ['task', 're_allocate_to', 'message']
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssign
        fields = ['id', 'name', 'estimate_ex_date', 'note', 'is_started', 'is_complete']

class TaskReAllocationRetrieveSerializer(serializers.ModelSerializer):
    task = TaskSerializer()  # Nested Task details
    user = UserSerializer()  # Nested User details (who performed the re-allocation)
    re_allocate_to = UserSerializer()  # Nested User details (to whom the task was re-allocated)

    class Meta:
        model = TaskReAllocation
        fields = ['id', 'task', 'user', 're_allocate_to', 'message', 'created_on', 'updated_on']
