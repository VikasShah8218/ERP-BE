from .models import TaskAssign ,AssosiatedUsersLandmark,TaskReAllocation,TaskLandmarkComplete,TaskMedia
from rest_framework.serializers import SerializerMethodField
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
    landmarks = SerializerMethodField() 
    created_by = UserSerializer()

    class Meta:
        model = TaskAssign
        fields = [
            'id', 'name', 'landmarks', 'estimate_ex_date', 'note', 'assigned_users',
            'is_started', 'started_on', 'is_complete', 'completed_on','latitude','longitude', 'conversation',
            'created_on', 'updated_on', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_by', 'updated_by', 'created_on', 'updated_on', 'conversation']

    def get_landmarks(self, obj):
        """
        Returns landmarks with completion status from TaskLandmarkComplete model.
        """
        landmarks = obj.landmarks.all()

        landmark_complete_data = TaskLandmarkComplete.objects.filter(task=obj)
        completion_map = {lc.landmark.id: lc.is_complete for lc in landmark_complete_data}

        serialized_landmarks = LandmarkSerializer(landmarks, many=True).data
        for landmark in serialized_landmarks:
            landmark['is_complete'] = completion_map.get(landmark['id'], False)
        
        return serialized_landmarks

class TaskAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssign
        fields = [
            'id', 'name', 'landmarks', 'estimate_ex_date', 'note', 'assigned_users',
            'is_started', 'started_on', 'is_complete','latitude','longitude',  'completed_on',
            'created_on', 'updated_on', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_by', 'updated_by', 'created_on', 'updated_on','conversation']

class TaskConversationSerializer(serializers.ModelSerializer):
    conversation = serializers.CharField()

    class Meta:
        model = TaskAssign
        fields = ['conversation','latitude','longitude']

class AssosiatedUsersLandmarkCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssosiatedUsersLandmark
        fields = ['id', 'landmark', 'user','latitude','longitude',  'created_on', 'updated_on']
        read_only_fields = ['created_on', 'updated_on']

class AssosiatedUsersLandmarkRetrieveSerializer(serializers.ModelSerializer):
    landmark = LandmarkSerializer()
    user = UserSerializer()

    class Meta:
        model = AssosiatedUsersLandmark
        fields = ['id', 'landmark', 'user', 'created_on','latitude','longitude',  'updated_on']

class UserWithLandmarksSerializer(serializers.ModelSerializer):
    landmarks = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'landmarks']

    def get_landmarks(self, obj):
        associated_landmarks = AssosiatedUsersLandmark.objects.filter(user=obj)
        landmarks = [assoc.landmark for assoc in associated_landmarks]
        return LandmarkSerializer(landmarks, many=True).data
    
class TaskReAllocationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReAllocation
        fields = ['task', 're_allocate_to', 'message','latitude','longitude']
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssign
        fields = ['id', 'name', 'estimate_ex_date', 'note','latitude','longitude',  'is_started', 'is_complete']

class TaskReAllocationRetrieveSerializer(serializers.ModelSerializer):
    task = TaskSerializer() 
    user = UserSerializer() 
    re_allocate_to = UserSerializer() 

    class Meta:
        model = TaskReAllocation
        fields = ['id', 'task', 'user', 're_allocate_to', 'message', 'created_on', 'updated_on','latitude','longitude']

class TaskLandmarkCompleteRetrieveSerializer(serializers.ModelSerializer):
    task = TaskAssignSerializer() 
    landmark = LandmarkSerializer()  

    class Meta:
        model = TaskLandmarkComplete
        fields = ['id', 'task', 'landmark', 'is_complete', 'created_on','latitude','longitude',  'updated_on', 'created_by', 'updated_by']

class TaskLandmarkCompleteCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLandmarkComplete
        fields = ['task', 'landmark', 'latitude','longitude', 'is_complete']

class TaskMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMedia
        fields = ['id', 'task', 'file_type', 'file', 'created_on','latitude','longitude',  'updated_on', 'created_by']
        read_only_fields = ['created_on', 'updated_on']