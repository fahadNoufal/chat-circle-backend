from rest_framework import serializers
from .models import Room,Message,Topic,User
from django.utils.timesince import timesince
from rest_framework import serializers

class TopicSerializer(serializers.ModelSerializer):
    room_count = serializers.SerializerMethodField()
    class Meta:
        model=Topic
        fields=['name','room_count']
    def get_room_count(self, obj):
        return Room.objects.filter(topic=obj).count()

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'username','avatar']#add profile pic



class RoomSerializer(serializers.ModelSerializer):
    timesince_field = serializers.SerializerMethodField()
    topic=TopicSerializer()
    host=HostSerializer()
    participants = serializers.SerializerMethodField() 

    class Meta:
        model=Room
        fields=['id','name','description','host','topic','timesince_field','participants']
        read_only_fields = ['host']
    def get_timesince_field(self, obj):
        return timesince(obj.created).split(',')[0]
    def get_participants(self, obj):
        return [HostSerializer(participant).data for participant in obj.participants.all()]
    
    def update(self, instance, validated_data):
        topic_data = validated_data.pop('topic', None)
        if topic_data:
            topic_name = topic_data.get('name')
            topic, created = Topic.objects.get_or_create(name=topic_name)
            instance.topic = topic
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'username','first_name','last_name','email','bio','avatar','name','date_joined']

    
class MessageSerializer(serializers.ModelSerializer):
    timesince_field = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()  # Use SerializerMethodField for the 'user_id' field
    room = serializers.SerializerMethodField()  # Use SerializerMethodField for the 'user_id' field

    class Meta:
        model = Message
        fields = ['id', 'user_id', 'body', 'timesince_field','room']

    def get_timesince_field(self, obj):
        return timesince(obj.created).split(',')[0]


    def get_user_id(self, obj):
        return HostSerializer(obj.user).data if obj.user else None

    def get_room(self, obj):
        return {'name':obj.room.name,'id':obj.room.id} if obj.room else None  

