# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CookedComment(models.Model):
    user = models.CharField(max_length=100, db_comment='用戶number')
    recipe = models.CharField(max_length=50, db_comment='食譜number')
    content = models.CharField(max_length=1000, blank=True, null=True, db_comment='用戶對食譜的評價')
    timestamp = models.DateTimeField(blank=True, null=True, db_comment='評論時間')
    rating = models.IntegerField(blank=True, null=True, db_comment='BERT模型計算出的得分')
    img = models.CharField(max_length=255, blank=True, null=True, db_comment='評論圖片')

    class Meta:
        managed = False
        db_table = 'cooked_comment'
        db_table_comment = '食譜評價表'


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=255, db_comment='食譜編號')
    name = models.CharField(max_length=255, db_comment='食譜名稱')
    category = models.CharField(max_length=255, db_comment='食譜分類(用%間隔)')
    author = models.CharField(max_length=255, db_comment='作者(url)')
    component = models.CharField(max_length=1000, db_comment='食材(用%間隔)')
    step = models.CharField(max_length=10000, db_comment='步驟(以%間隔)')
    like_count = models.IntegerField(db_comment='收藏數')
    cooked = models.CharField(max_length=1000, blank=True, null=True, db_comment='做過該食譜的用戶(url用%間隔)')
    intro = models.CharField(max_length=255, blank=True, null=True, db_comment='食譜簡介')
    img = models.CharField(max_length=255, blank=True, null=True, db_comment='食譜圖片')

    class Meta:
        managed = False
        db_table = 'recipe'
        db_table_comment = '食譜表'


class RecipeCategory(models.Model):
    number = models.CharField(max_length=255, db_comment='分類編號')
    name = models.CharField(max_length=255, db_comment='分類名稱')
    url = models.CharField(max_length=255, db_comment='分類網址')
    root = models.IntegerField(blank=True, null=True,db_comment='父類Id')

    class Meta:
        managed = False
        db_table = 'recipe_category'
        db_table_comment = '食譜分類表'


class RecipeUser(models.Model):
    number = models.CharField(max_length=100, db_comment='用戶編號')
    name = models.CharField(max_length=100, db_comment='用戶名稱')
    head_pic = models.CharField(max_length=500, blank=True, null=True, db_comment='用戶頭像')

    class Meta:
        managed = False
        db_table = 'recipe_user'
        db_table_comment = '食譜用戶表'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_name=models.CharField(max_length= 50, db_comment='帳戶')
    password=models.CharField(max_length= 50, db_comment='密碼')
    real_name=models.CharField(max_length= 50, db_comment='真實姓名', blank=True, null=True)
    phone=models.CharField(max_length= 100, db_comment="手機號", unique=True)
    email=models.CharField(max_length= 100, db_comment='郵箱', unique=True)
    age=models.IntegerField(blank=True, null=True, db_comment='年齡')
    address=models.CharField(max_length=255, blank=True, null=True, db_comment='地址')
    gender=models.IntegerField( blank=True, null=True, db_comment='性別')
    avatar=models.CharField(max_length=500, blank=True, null=True, db_comment='頭像')
    bg=models.CharField(max_length=500, blank=True, null=True, db_comment='背景圖片')

    class Meta:
        managed=False
        db_table='users'
        db_table_comment='用戶表'

class UserLike(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.IntegerField(db_comment='用戶id')
    recipe = models.IntegerField(db_comment='食譜id')
    timestamp = models.DateTimeField(db_comment='評論時間')

    class Meta:
        managed = False
        db_table = 'user_like'
        db_table_comment = '用戶收藏表'

class Subscribe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.IntegerField(db_comment='用戶id')
    author = models.CharField(max_length=50, db_comment='作者用戶名')
    timestamp = models.DateTimeField(db_comment='時間戳')

    class Meta:
        managed = False
        db_table = 'subscribe'
        db_table_comment = '訂閱表'