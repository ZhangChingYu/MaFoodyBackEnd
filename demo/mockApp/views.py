from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import Http404

from mockApp.models import DBTest, Pictures, Avatar
from mockApp.serializers import DBTestSerializer
from datetime import datetime
import json
import random
# Create your views here.


@csrf_exempt
def dbTestApi(request, id=0):
    if request.method=='GET':
        tests = DBTest.objects.all()
        test_sserializer = DBTestSerializer(tests, many=True)
        return JsonResponse(test_sserializer.data,safe=False)
    elif request.method=='POST':
        dbTest_data = JSONParser().parse(request)
        test_sserializer=DBTestSerializer(data=dbTest_data)
        if test_sserializer.is_valid():
            test_sserializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method=='PUT':
        dbTest_data=JSONParser().parse(request)
        test=DBTest.objects.get(TestId=dbTest_data['TestId'])
        test_sserializer=DBTestSerializer(test, data=dbTest_data)
        if test_sserializer.is_valid():
            test_sserializer.save()
            return JsonResponse('Update Successfully', safe=False)
        return JsonResponse('Failed to Update')
    elif request.method=='DELETE':
        test=DBTest.objects.get(TestId=id)
        test.delete()
        return JsonResponse('Delete Successfully', safe=False)

# 處理圖片更新，不能直接修改ImageField的值
# 所以要先上傳新的圖片，在將圖片地址返回並賦值給食譜，然後再將原本的圖片刪除
@csrf_exempt
def picture(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        picture = Pictures.objects.get(id=id)
        if picture is not None:
            return JsonResponse({'status':200, 'data':{'url':picture.image.url}})
        else:
            raise Http404('Picture does not exist.')
    elif request.method == 'POST':
        # 將圖片名稱改為 食譜名稱_上傳時間.後綴 (.jpg, .png, .jpeg...), 時間的格式為 年月日時分秒 全部連在一起
        name = request.POST.get('name')
        file = request.FILES.get('image')
        if file:
            source_type = str(file.name).split('.')[-1]
            file_name = name+'_'+datetime.now().strftime("%Y%m%d%H%M%S")+'.'+source_type
            file.name = file_name
            model = Pictures(image=file)
            model.save()
            print(model.image.url)
            return JsonResponse({'status':200, 'data':{'url':model.image.url}})
        elif request.method == 'DELETE':
            data = jsonRequestDecode(request=request)
            recipeId = data['id']
            check = Pictures.objects.get(id=recipeId).delete()
            if check[0]>0:
                return JsonResponse({'status':200, 'data':{'msg':'Picture Deleted!'}})
            else:
                return JsonResponse({'status':500, 'data':{'msg':'Picture Delelte Failed!'}})
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})
    
@csrf_exempt
def CommentPicture(request):
    if request.method=='POST':
        name = request.POST.get('name')
        file = request.FILES.get('image')
        print(type(file))
        print(file.name, file.size)
        print(name)
        return JsonResponse({'status':200, 'data':{'url':'url'}})
    
@csrf_exempt
def AvatarUpload(request):
    if request.method=='POST':
        name = request.POST.get('name')
        file = request.FILES.get('image')
        print(file.name, file.size)
        if file:
            source_type = str(file.name).split('.')[-1]
            file_name = name+'_'+datetime.now().strftime("%Y%m%d%H%M%S")+'.'+source_type
            file.name = file_name
            model = Avatar(image=file)
            model.save()
            print(model.image.url)
            return JsonResponse({'status':200, 'data':{'url':model.image.url}})
    elif request.method == 'DELETE':
        data = jsonRequestDecode(request=request)
        recipeId = data['id']
        check = Avatar.objects.get(id=recipeId).delete()
        if check[0]>0:
            return JsonResponse({'status':200, 'data':{'msg':'Picture Deleted!'}})
        else:
            return JsonResponse({'status':500, 'data':{'msg':'Picture Delelte Failed!'}})
    elif request.method=='GET':
        avatars = Avatar.objects.all()
        url_list = []
        for avatar in avatars:
            url_list.append(avatar.image.url)
        random.shuffle(url_list)
        return JsonResponse({'status':200, 'data':{'avatar':url_list[0]}})

    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})


@csrf_exempt
def PictureUpdate(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        file = request.FILES.get('image')
        source_type = str(file.name).split('.')[-1]
        picture = Pictures.objects.get(id=id)
        name = picture.image.name.split('_')[0]
        file_name  = name + '_' + datetime.now().strftime("%Y%m%d%H%M%S")+'.'+source_type
        file.name = file_name
        picture.image = file
        picture.save()
    return JsonResponse({'status':200, 'data':{'msg':file.name}})


def jsonRequestDecode(request):
    body = request.body
    body_str = body.decode()
    data = json.loads(body_str)
    return data