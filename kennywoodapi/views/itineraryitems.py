"""View module for handling requests about park areas"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from kennywoodapi.models import  Itinerary, ParkArea, Attraction, Customer


class ItineraryItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for park areas

    Arguments:
        serializers
    """
    # searializer is trying to create

    class Meta:
        model = Itinerary
        url = serializers.HyperlinkedIdentityField(
            view_name='itinerary',
            lookup_field='id'
        )
        fields = ('id', 'url', 'starttime', 'attraction')
        # specify depth tu build objects on objects that use f
        depth = 2


class ItineraryItems(ViewSet):
    """Itinerary Items for Kennywood Customers"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized Itinerary Item instance
        """
# MAKE SURE YOU ARE ASSIGNING THE AREA OBJECT TO THE new_itenary.area property instead of just they FK value
        new_itinerary_item = Itinerary()
        new_itinerary_item.starttime = request.data["starttime"]
        new_itinerary_item.customer = Customer.objects.get(user=request.auth.user)
        new_itinerary_item.attraction = Attraction.objects.get(pk=request.data["ride_id"])

        new_itinerary_item.save()
# Saves the new thing to the DB in JSON
        serializer = ItineraryItemSerializer(new_itinerary_item, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single itinerary item

        Returns:
            Response -- JSON serialized itinerary item instance
        """
        try:
            itinerary_item = Itinerary.objects.get(pk=pk)
            serializer = ItineraryItemSerializer(itinerary_item, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a park area attraction

        Returns:
            Response -- Empty body with 204 status code
        """
        attraction = Attraction.objects.get(pk=pk)
        area = ParkArea.objects.get(pk=request.data["area_id"])
        attraction.name = request.data["name"]
        attraction.area = area
        attraction.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single itinerary item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            item = Itinerary.objects.get(pk=pk)
            item.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Itinerary.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to Itineraries resource

        Returns:
            Response -- JSON serialized list of Itinerary Items
        """
        customer = Customer.objects.get(user=request.auth.user)
        items = Itinerary.objects.filter(customer=customer)


        serializer = ItineraryItemSerializer(
            items, many=True, context={'request': request})
        return Response(serializer.data)
