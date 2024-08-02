from rest_framework import serializers
from mockApp.models import DBTest, Pictures, Avatar

class DBTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DBTest
        fields = ('TestId','TestName')

class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pictures
        fields = ('id','image')

class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ('id','image')

