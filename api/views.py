from django.shortcuts import render,redirect
from django.db.models import Q
import random
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login,logout,authenticate
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Room,Topic,Message,User
from api.serializers import RoomSerializer,UserSerializer,MessageSerializer,TopicSerializer
from .forms import EditUserForm

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer

@api_view(['GET'])
def rooms(request):
    q=request.GET.get('q') if request.GET.get('q') else ''
    rooms=Room.objects.filter(Q(name__icontains=q)| Q(host__username__icontains=q)| Q(topic__name__icontains=q)|Q(description__icontains=q))
    roomLength=len(rooms)

    # user=if (request.user.id) return User.objects.get(pk=request.user.id) else None

    serializer=RoomSerializer(rooms[:15],many=True)
    def get_random_users(count):
    # Get the total number of users in the User model
        total_users = User.objects.count()
        # Generate a list of random indexes without repetition
        random_indexes = random.sample(range(total_users), min(count, total_users))
        # Fetch users at the random indexes
        random_users = User.objects.filter(pk__in=random_indexes)
        return random_users
    random_users = get_random_users(4)

    topics=Topic.objects.all()[:5]
    topics_ser=TopicSerializer(topics,many=True)
    activities=Message.objects.all()[:3]
    activities_ser=MessageSerializer(activities,many=True)
    discover_people=UserSerializer(random_users,many=True)
    data={'rooms':serializer.data,'topics':topics_ser.data,'room_count':roomLength,'messages':activities_ser.data,'discover_users':discover_people.data}
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUser(request):
    user=User.objects.get(id=request.user.id)
    serializer=UserSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
def roomViewApi(request,pk):
    roomItem=Room.objects.get(pk=pk)
    room_messages=roomItem.message_set.all().order_by('-created')
    room_messages_serializer=MessageSerializer(room_messages,many=True)
    room_serializer=RoomSerializer(roomItem)

    data = {
        'roomItem': room_serializer.data,
        'room_messages': room_messages_serializer.data,
    }
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_message(request,pk):
    roomItem=Room.objects.get(pk=pk)
    message=Message.objects.create(
        user=request.user,
        room=roomItem,
        body=request.data.get('message')
    )
    roomItem.participants.add(request.user)
    message.save()
    serializer=MessageSerializer(message)

    return Response(serializer.data)  #return to the specific room where message was added


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_room(request):
    print(request.user)
    if not request.user.is_authenticated:
        return Response('unauthorized')
    data=request.data
    roomName=data.get('name')
    roomDescription=data.get('description')
    roomTopic=data.get('topic')
    topic,created=Topic.objects.get_or_create(name=roomTopic)
    roomHost=request.user
    created_room = Room.objects.create(name=roomName,description=roomDescription,topic=topic,host=roomHost)
    if created_room is not None:
        created_room.save()
        serializer=RoomSerializer(created_room)
        return Response(serializer.data)
    return (False)



@api_view(["POST","GET"])
# @permission_classes([IsAuthenticated])
def update_room(request,pk):
    room=Room.objects.get(pk=pk)
    if request.method == 'POST':
        serializer=RoomSerializer(instance=room,data=request.data,partial=True) #set host (search)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else : return Response(serializer.errors)

    if request.method == 'GET':
        serializer=RoomSerializer(room)
        return Response(serializer.data)    
        


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def delete_room(request,pk):
    if not request.user.is_authenticated:
        return Response('unauthorized')
    room=Room.objects.get(pk=pk)
    if request.user != room.host:
        return Response('This is not your room..!!')
    room.delete()
    return redirect('rooms')

@api_view(["POST"])
def login_user(request):
    data=request.data
    if request.user.is_authenticated:
        return Response('active')   
    username=data.get('username') 

    password=data.get('password')

    try:
        user=User.objects.get(username=username)
    except:
        return Response(False)

    user=authenticate(request,username=username,password=password)

    if user is not None:
        login(request,user)
        serializer=UserSerializer(request.user)
        return Response(serializer.data)
    else :
        return Response(False)

@api_view(["POST"])
def register_user(request):
    data=request.data
    username=data.get('username')
    name=data.get('name')
    avatar=data.get('avatar')
    email=data.get('email')
    password=data.get('password')
    confirm_password=data.get('confirm-password')
    if password!= confirm_password :
        return Response("Passwords do not match")
    user=User.objects.create_user(username,password=password,email=email,name=name,avatar=avatar)
    if user is not None :
        user.username=user.username.lower()
        user.save()
        return Response("registered")
    else :
        return Response(False)

@api_view(['GET'])
def logout_user(request):
    return logout(request)

@api_view(["GET"])
def user_profile(request,pk):
    user=User.objects.get(pk=pk)
    serializer=UserSerializer(user)

    topics=Topic.objects.all()
    topics=TopicSerializer(topics,many=True)

    messages=user.message_set.all()
    messages=MessageSerializer(messages,many=True)

    rooms=user.room_set.all()
    room_count=len(rooms)
    rooms=RoomSerializer(rooms[:15],many=True)

    user_profile_data={'topics': topics.data,'messages': messages.data,'room_count':room_count,'rooms': rooms.data,'host':serializer.data}

    return Response(user_profile_data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    data=request.data
    user=request.user
    form =EditUserForm(data,instance=user)
    if form.is_valid():
        user=form.save()
        return redirect('rooms')
    else: return Response(False)

@api_view(["GET"])
def topics_view(request):
    rooms=Room.objects.all()
    roomLength=len(rooms)
    topics=Topic.objects.all()
    serializer=TopicSerializer(topics,many=True)
    return Response({'room_count':roomLength, 'topics':serializer.data})

@api_view(["GET"])
def activities_view(request):
    activities=Message.objects.all()[:15]
    serializer=MessageSerializer(activities,many=True)
    return Response({'messages':serializer.data})