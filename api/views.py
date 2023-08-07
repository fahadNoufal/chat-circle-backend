from django.shortcuts import render,redirect
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Room,Topic,Message
from api.serializers import RoomSerializer,UserSerializer,MessageSerializer,TopicSerializer
from .forms import EditUserForm
# Create your views here.

@api_view(['GET'])
def rooms(request):
    q=request.GET.get('q') if request.GET.get('q') else ''
    rooms=Room.objects.filter(Q(name__icontains=q)| Q(host__username__icontains=q)| Q(topic__name__icontains=q)|Q(description__icontains=q))
    serializer=RoomSerializer(rooms,many=True)
    topics=Topic.objects.all()[:5]
    topics_ser=TopicSerializer(topics,many=True)
    activities=Message.objects.all()[:3]
    activities_ser=MessageSerializer(activities,many=True)
    data={'rooms':serializer.data,'topics':topics_ser.data,'messages':activities_ser.data}
    return Response(data)

@api_view(['GET','POST'])
def roomViewApi(request,pk):
    roomItem=Room.objects.get(pk=pk)
    if request.method == 'POST':
        message=Message.objects.create(
            user=request.user,
            room=roomItem,
            body=request.data.get('message')
        )
        roomItem.participants.add(request.user)
        message.save()
        return redirect('room-api',roomItem.id)  #return to the specific room where message was added
    room_messages=roomItem.message_set.all().order_by('-created')
    room_messages_serializer=MessageSerializer(room_messages,many=True)
    room_serializer=RoomSerializer(roomItem)
    
    data = {
        'roomItem': room_serializer.data,
        'room_messages': room_messages_serializer.data,
    }
    return Response(data)

@api_view(["POST"])
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


@api_view(["POST"])
def update_room(request,pk):
    if not request.user.is_authenticated:
        return Response('unauthorized') 
    room=Room.objects.get(pk=pk)
    serializer=RoomSerializer(instance=room,data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(["GET"])
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
    password=data.get('password')
    confirm_password=data.get('confirm_password')
    if password!= confirm_password :
        return Response("Passwords do not match")
    user=User.objects.create_user(username,password=password)
    if user is not None :
        user.username=user.username.lower()
        user.save()
        login(request,user)
        return redirect('rooms')
    else :
        return Response(False)

@api_view(['GET'])
def logout_user(request):
    logout(request)
    return redirect('rooms')

@api_view(["GET"])
def user_profile(request,pk):
    user=User.objects.get(pk=pk)
    print(user)
    serializer=UserSerializer(user)

    topics=Topic.objects.all()
    topics=TopicSerializer(topics,many=True)

    messages=user.message_set.all()
    messages=MessageSerializer(messages,many=True)

    rooms=user.room_set.all()
    rooms=RoomSerializer(rooms,many=True)

    user_profile_data={'topics': topics.data,'messages': messages.data,'rooms': rooms.data,'host':serializer.data}

    return Response(user_profile_data)

@api_view(["POST"])
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
    topics=Topic.objects.all()
    serializer=TopicSerializer(topics,many=True)
    return Response(serializer.data)

@api_view(["GET"])
def activities_view(request):
    activities=Message.objects.all()
    serializer=MessageSerializer(activities,many=True)
    return Response(serializer.data)
