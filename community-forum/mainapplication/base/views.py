from django.shortcuts import redirect, render
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message
from .forms import RoomForm

# USER PROFILE VIEW
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = { 
        'user': user, 
        'rooms': rooms, 
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)

# REGISTER VIEW
def registerUser(request):
    form = UserCreationForm

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        # VLAIDATING FORM
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
        else:
            messages.error(request, 'Something went wrong during registration')

    context = {'form': form}
    return render(request, 'base/login_register.html', context=context)

# LOGIN VIEW
def loginUser(request):
    page = 'login'
    # IF THE USER IS ALREADY LOGGED IN 
    # REDIRECT HIM TO DASHBOARD
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # QUERY THE USERNAME FROM DATABASE
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User doesn't exist")

        # AUTHENTICATE THE USER
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username and Password doesn't match")

    context={'page': page}
    return render(
        request,
        'base/login_register.html',
        context
    )

# LOGOUT VIEW
def logoutUser(request):
    logout(request)
    return redirect('home')

# ROOT VIEW
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms': rooms, 
        'topics': topics,
        'room_messages': room_messages,
        'room_count': room_count
    }

    return render(
        request, 'base/home.html',
        context
    )

# ROOM VIEW 
def room(request, id):
    room = Room.objects.get(id=id)

    # GETTING ALL THE MESSAGES FROM THE ROOM
    # SYNTAX: parentTable.childTable_set.all()
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        room_message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', id=room.id)

    context = {
        'room': room, 
        'room_messages': room_messages,
        'participants': participants
    }

    return render(
        request, 'base/room.html',
        context
    )

# CREATE ROOM VIEW
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            # GETTING THE INSTANCE OF THE FORM (ROOM FORM) 
            # WE WILL EDIT IT UPDATE IT LATER. LIKE WE NEED TO ADD DEFAULT HOST TO DATABASE AS WE ARE NOT HAVE ANY OPTION FOR SELECT THE HOST ON FORM.
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
    context = {'form': form}

    return render(
        request, 'base/room-form.html', 
        context
    )

# UPDATE ROOM INFO VIEW
@login_required(login_url='login')
def updateRoom(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)

    # CHECK IF THE USER IS THE CREATOR OF THE ROOM
    if request.user != room.host:
        return HttpResponse('You are not allowed here')


    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(
        request, 'base/room-form.html',
        context
    )

# DELETE ROOM VIEW
@login_required(login_url='login')
def deleteRoom(request, id):
    room = Room.objects.get(id=id)

    # CHECK IF THE USER IS THE CREATOR OF THE ROOM
    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    context = {'obj': room}

    return render(
        request, 'base/delete.html',
        context=context
    )


# DELETE MESSAGE VIEW
@login_required(login_url='login')
def deleteMessage(request, id):
    message = Message.objects.get(id=id)

    # CHECK IF THE USER IS THE CREATOR OF THE ROOM
    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    context = {'obj': message}

    return render(
        request, 'base/delete.html',
        context=context
    )