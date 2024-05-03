from rest_framework import serializers

class FlightSerializer(serializers.Serializer):
    airline = serializers.CharField()
    price = serializers.CharField()
    flight_time = serializers.DateField()