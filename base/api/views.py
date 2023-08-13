# Json API Response
from django.http import JsonResponse
# Django Rest framework
from rest_framework.response import Response
# To restrict only for GET request
from rest_framework.decorators import api_view
from base.models import Room
# Import Serializers
from .serializers import RoomSerializer

# Create views here
@api_view(["GET"])
def getRoutes(response):
    routes = [
        "GET /api",
        "GET /api/rooms",
        "GET /api/rooms/:id",
    ]
    # safe=false changes it to a JSON list
    return Response(routes)


@api_view(["GET"])
def getRooms(response):
    rooms = Room.objects.all()
    # Many means "are they multiple objects";
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getRoom(response, pk):
    room = Room.objects.get(id=pk)
    # Many means "are they multiple objects";
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)
