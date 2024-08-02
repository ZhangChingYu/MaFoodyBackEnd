from rest_framework import serializers
from App.models import Recipe, RecipeUser, RecipeCategory, CookedComment, User, UserLike, Subscribe

# 管理 JSON 的序列化和 JSON 的反序列化。

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Recipe
        fields=('id','number','name','category','author','component','step','like_count','cooked','intro','img')

class RecipeOutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model=Recipe
        fields=('id','name','author','img')

class RecipeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecipeUser
        fields=('number','name','head_pic')

class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=RecipeCategory
        fields=('id','name', 'root')

class CookedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=CookedComment
        fields=('id', 'user','recipe','content','timestamp','rating', 'img')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','user_name','password','real_name','phone','email','age','address','gender','avatar','bg')

class UserLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserLike
        fields=('id','user','recipe')

class SubscirbeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields=('id','user','author', 'timestamp')