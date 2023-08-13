# Render it to a web page
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Query From Django
from django.db.models import Q

# Model database
from .models import Room, Topic, Message, User

# Forms for create room and User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Messages for User Error
from django.contrib import messages

# Authentication
from django.contrib.auth import authenticate, login, logout

# Decorator for restricted login required
from django.contrib.auth.decorators import login_required

# Import Register forms
# from django.contrib.auth.forms import UserCreationForm

# Create your views here.

# rooms = [
#     {"id": 1, "name": "Lets learn Python!"},
#     {"id": 2, "name": "Lets learn JavaScript!"},
#     {"id": 3, "name": "Lets learn C++!"},
#     {"id": 4, "name": "Lets learn Web Development!"},
# ]


def loginPage(response):
    page = "login"
    # Prevent logged-in user for accessing the login in url
    if response.user.is_authenticated:
        return redirect("index")

    # Get username and password
    if response.method == "POST":
        email = response.POST.get("email").lower()
        password = response.POST.get("password")

        # Check if the user exist
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(response, "User does not exist")

        # Authenticate username and password
        user = authenticate(response, email=email, password=password)

        # If there is a user after authentication
        if user is not None:
            login(response, user)
            return redirect("index")
        else:
            messages.error(response, "Username or Password is invalid")

    context = {"page": page}
    return render(response, "base/login_register.html", context)


def logoutUser(response):
    logout(response)
    return redirect("index")


def registerPage(response):
    page = "register"
    form = MyUserCreationForm

    if response.method == "POST":
        form = MyUserCreationForm(response.POST)
        if form.is_valid():
            # Save the form but freeze it in time to get the user information
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(response, user)
            return redirect("index")
        else:
            messages.error(response, "An error occurred during registration")

    return render(response, "base/login_register.html", {"form": form})


def index(response):
    # If response q has a value, else return blank
    q = response.GET.get('q') if response.GET.get('q') != None else ''
    # What ever value in the title name it contains; "i" means case insensitive
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q)
                                | Q(description__icontains=q))

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:5]

    context = {"rooms": rooms, "topics": topics, "room_count": room_count,
               "room_messages": room_messages}
    return render(response, "base/home.html", context)


def room(response, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if response.method == "POST":
        message = Message.objects.create(
            user=response.user,
            room=room,
            body=response.POST.get("body")
        )
        room.participants.add(response.user)
        return redirect("room", pk=room.id)

    context = {"room": room, "room_messages": room_messages, "participants": participants}
    return render(response, "base/room.html", context)


# Create User Profile
def userProfile(response, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user": user, "rooms": rooms,
               "room_messages": room_messages, "topics": topics}
    return render(response, "base/profile.html", context)


# Login Required for Create Room
@login_required(login_url='login')
def createRoom(response):
    # Form field for room
    form = RoomForm
    # Topic
    topics = Topic.objects.all()

    if response.method == "POST":
        # Add data to the form
        form = RoomForm(response.POST)
        # Get or create unique room, topic
        topic_name = response.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=response.user,
            topic=topic,
            name=response.POST.get("name"),
            description=response.POST.get("description")
        )

        # Check if it is Valid
        # if form.is_valid():
        #     # Hold on the submission
        #     room = form.save(commit=False)
        #     room.host = response.user
        #     room.save()
        return redirect("index")

    context = {"form": form, "topics": topics}
    return render(response, "base/room_form.html", context)


# Login Required for Update Room
@login_required(login_url='login')
def updateRoom(response, pk):
    # Make sure the room is the unique id you're getting
    room = Room.objects.get(id=pk)
    # Get the form of the unique id using "instance=room"
    form = RoomForm(instance=room)
    # topic
    topics = Topic.objects.all()

    # Strictly only user can CRUD their work
    if response.user != room.host:
        return HttpResponse("You're not allowed here!! ")

    # Get the form and save it
    if response.method == "POST":
        # form = RoomForm(response.POST, instance=room)
        # if form.is_valid():
        # Get or create unique room, topic
        topic_name = response.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = response.POST.get("name")
        room.topic = topic
        room.description = response.POST.get("description")
        room.save()

        return redirect("index")

    context = {"form": form, "topics": topics, "room": room}
    return render(response, "base/room_form.html", context)


# Login Required for Delete Room
@login_required(login_url='login')
def deleteRoom(response, pk):
    # Get the room Id
    room = Room.objects.get(id=pk)

    # Delete room
    if response.user != room.host:
        return HttpResponse("You're not allowed here!! ")

    if response.method == "POST":
        # Delete room with the delete function
        room.delete()
        # Return to index page
        return redirect("index")
    return render(response, "base/delete.html", {"obj": room})


# Login Required for Delete Message
@login_required(login_url='login')
def deleteMessage(response, pk):
    # Get the room ID
    message = Message.objects.get(id=pk)

    # Delete room
    if response.user != message.user:
        return HttpResponse("You're not allowed here!! ")

    if response.method == "POST":
        # Delete room with the delete function
        message.delete()
        # Return to index page
        return redirect("index")
    return render(response, "base/delete.html", {"obj": message})


# Update User Profile
@login_required(login_url='login')
def updateUser(response):
    user = response.user
    form = UserForm(instance=user)

    if response.method == "POST":
        form = UserForm(response.POST, response.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(response, "base/update-user.html", {"form": form})


def topicsPage(response):
    # If response q has a value, else return blank
    q = response.GET.get('q') if response.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    return render(response, "base/topics.html", {"topics": topics})


def activityPage(response):
    # If response q has a value, else return blank
    q = response.GET.get('q') if response.GET.get('q') != None else ''
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:5]

    context = {"room_messages": room_messages}
    return render(response, "base/activity.html", context)


def editUser(response):
    user = response.user
    return render(response, "base/edit-user.html")
