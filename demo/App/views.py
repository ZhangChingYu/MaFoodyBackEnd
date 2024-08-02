from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from App.models import Recipe, User, CookedComment, RecipeUser, RecipeCategory, UserLike, Subscribe
from App.serializers import RecipeSerializer, RecipeOutlineSerializer,UserSerializer,CookedCommentSerializer, RecipeUserSerializer
from App.serializers import RecipeCategorySerializer, UserLikeSerializer, SubscirbeSerializer
import json
import random
import time
import os
 
# /Users/sunny/Desktop/MaFoodyBackEnd/demo
current_working_dir = os.getcwd()

# Create your views here.

# RESTful API Views

@csrf_exempt
def RecipeApi(request, id=0):
    # 根據id獲取食譜
    if request.method=='GET':
        reicpes=Recipe.objects.get(id=id)
        serializer=RecipeSerializer(reicpes)
        return JsonResponse(serializer.data, safe=False)
    return JsonResponse({'msg':'Success','reques type':request.method})

'''
Sign Up
'''
@csrf_exempt
def SignUpApi(request):
    # 新用戶註冊
    if request.method == 'POST':
        # {'phone': '', 'email': '', 'password': '', 'userName': '', 'age': '', 'gender': 0}
        # fields=('id','user_name','password','real_name','phone','email','age','address','gender','avatar','bg')
        data = jsonRequestDecode(request=request)
        # 檢查手機號是否重複
        try:
            result = User.objects.get(phone = data['phone'])
            return JsonResponse({'status':204, 'data':{'msg':'Existing User', 'userName':result.user_name}})
        except:
            model = User(user_name = data['userName'], password=data['password'], phone=data['phone'],
                          email=data['email'], age=data['age'], gender=data['gender']
            )
            model.save()
            # 確認是否添加成功
            try:
                result = User.objects.get(phone = data['phone'])
                return JsonResponse({'status':200, 'data':{'userId':result.id, 'userName':result.user_name}})
            except:
                return JsonResponse({'status':500, 'data':{'msg':'Server Error. Please Try Again Later.'}})
    return JsonResponse({'hello':400, 'data':{'msg':'Request Error!'}})

'''Login'''

@csrf_exempt
def AuthenticationApi(request):
    # 輸入帳號密碼登入並返回用戶信息
    if request.method=='GET':
        userName=request.GET.get('userName')
        password=request.GET.get('password')
        try:
            user=User.objects.get(user_name=userName)
        except:
            return JsonResponse({'status':500,'data':{'msg':'User Not Exist, Please Try Sign In.'}}, safe=False)
        serializer=UserSerializer(user)
        if(serializer.data['password']==password):
            return JsonResponse({'status':200,'data':{'msg':'Log in success', 'user':serializer.data}}, safe=False)
        return JsonResponse({'status':502, 'data':{'msg':'Wrong Password'}}, safe=False)


'''Recommendation''' 

@csrf_exempt
def RecommendApi(request):
    # 返回食譜Icon需要的數據
    if request.method=='GET':
        # 先隨便拿一個
        userId=request.GET.get('userId')
        index = int(request.GET.get('index'))
        if(userId!=None):
            recipe_ids = getRecommendIdList(userId=userId)
            recipe_numbers = read_feature_reverse('recipe', recipe_ids[index:index+40])
            random.shuffle(recipe_numbers)
            target_list = []
            for number in recipe_numbers:
                target_list.append(Recipe.objects.get(number=str(number)+'\n'))
            serializer=RecipeOutlineSerializer(target_list, many=True)
            recipe_list = recipeOutlineHandler(serializer=serializer, user=userId)
            return JsonResponse({'status':200, 'data':{'recommend':recipe_list}}, safe=False)
        
        return JsonResponse({'status':400, 'data':{'msg':'User Id Dose NOT Exist!'}})

@csrf_exempt
def TranddApi(request):
    # 返回點贊最多的食譜
    if request.method == 'GET':
        userId = request.GET.get('id')
        max_len = 1000 # 返回點讚數最多的1000個食譜
        reicpe = Recipe.objects.all().order_by('-like_count')[0:max_len]
        serializer = RecipeOutlineSerializer(reicpe, many=True)
        trend_list = recipeOutlineHandler(serializer=serializer, user=userId)
        random.shuffle(trend_list) # 打亂順序
        return JsonResponse({'status':200, 'data':{"recipe":trend_list}},safe=False)
    return JsonResponse({'status':404, 'data':{'msg':'Page Not Found!'}})

@csrf_exempt
def SubsrcibeApi(request):
    # 返回訂閱作者的食譜
    if request.method=='GET':
        userId = request.GET.get('id')
        author_name = request.GET.get('author')
        if author_name:
            author_name = 'https://icook.tw/users/'+author_name
            recipes = Recipe.objects.filter(author=author_name)
            serializer = RecipeOutlineSerializer(recipes, many=True)
            recipe_list = recipeOutlineHandler(serializer=serializer, user=userId)
            return JsonResponse({'status':200, 'data':{'recipe_list':recipe_list}}, safe=False)
        else:
            max_len = 1000
            recipe_list = []
            subscribes = Subscribe.objects.filter(user=userId)
            for subscribe in subscribes:
                recipes = Recipe.objects.filter(author__contains=subscribe.author)[0:max_len]
                serializer = RecipeOutlineSerializer(recipes, many=True)
                recipe_list += recipeOutlineHandler(serializer=serializer, user=userId)
            random.shuffle(recipe_list)
            return JsonResponse({'status':200, 'data':{'recipe_list':recipe_list}})
    elif request.method=='PUT':
        # {'user':1, 'author':1djlf, 'timestamp':'2023-05-11 10:13:34'}
        # fields={'id', 'user', 'author', 'timestamp'}
        data=jsonRequestDecode(request=request)
        # 避免重複添加
        try:
            history = Subscribe.objects.get(user=data['user'], author=data['author'])
            history.delete()
            try:
                check = Subscribe.objects.get(user=data['user'], author=data['author'])
                return JsonResponse({'status':500, 'data':{'msg':'Server Error, Please Try Again!'}})
            except:
                return JsonResponse({'status':200, 'data':{'msg':'Subscribe Deleted!'}})
        except:
            model = Subscribe(user=data['user'], author=data['author'], timestamp=data['timestamp'])
            model.save()
            # 確認是否添加成功
            try:
                history = Subscribe.objects.get(user=data['user'], author=data['author']) 
                return JsonResponse({'status':200, 'data':{'msg':'Subscribe Added!'}})
            except:
                return JsonResponse({'status':500, 'data':{'msg':'Server Error, Please Try Again!'}})
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found'}})

'''Recipe Information'''

@csrf_exempt
def RecipeDetail(request):
    # 返回食譜詳細信息
    recipeId = request.GET.get('recipeId')
    if(recipeId!=None):
        target = Recipe.objects.get(id=recipeId)
        serializer = RecipeSerializer(target)
        data = recipeDetailHandler(serializer=serializer)
        return JsonResponse({'status':200,'data':{'recipe':data}}, safe=False)
    else:
        return JsonResponse({'status':404, 'data':{'msg':'Recipe Not Found!'}})
    
@csrf_exempt
def ShowRecipeCommentApi(request):
    # 通過之前獲取的comment ids獲取評論
    if request.method=='GET':      
        recpeId = request.GET.get('recipeId')
        recipe = Recipe.objects.get(id=recpeId)
        serializer = RecipeSerializer(recipe)
        recipeNumber = serializer.data['number']
        if recipeNumber:
            recipeNumber = recipeNumber.replace('\n','')
            try:
                comment = CookedComment.objects.filter(recipe=recipeNumber)
            except:
                return JsonResponse({'status':400, 'data':{'msg':'Requested Comment Dose Not Exist!'}})
            serializer = CookedCommentSerializer(comment, many=True)
            comment_list = recipeCommentHandler(serializer.data)
        else:
            comment_list = []
        return JsonResponse({'status':200,'data':{'comment':comment_list}})

@csrf_exempt
def RecipeLikeStateApi(request):
    # 查看當前用戶對該食譜的收藏狀態
    if request.method=='GET':
        userId = request.GET.get('userId')
        recipeId = request.GET.get('recipeId')
        try:
            like_state = UserLike.objects.get(user=userId, recipe=recipeId)
            return JsonResponse({'status':200, 'data':{'state':True}})
        except:
            return JsonResponse({'status':200, 'data':{'state':False}})
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})

@csrf_exempt
def CommentPublishApi(request):
    # 用戶發布評論
    if request.method == 'POST':
        #{'id', 'user','recipe','content','timestamp','rating', 'img'}
        data = jsonRequestDecode(request)
        print(data)
        recipe = Recipe.objects.get(id=data['recipe'])
        comment = CookedComment(user=data['user'], recipe=recipe.number.replace('\n',''), content=data['content'], timestamp=data['timestamp'], rating=data['rating'], img=data['img'])
        comment.save()
        check = CookedComment.objects.filter(user=data['user'], recipe=recipe.number.replace('\n',''), timestamp=data['timestamp'])
        if(len(check)>0):
            if recipe.cooked==None:
                print('Null')
                recipe.cooked ='SilviaChang%'
                print('Ok')
            else:
                print('Not Null')
                recipe.cooked = recipe.cooked+'SilviaChang%'
            recipe.save()
            print('Here')
            return JsonResponse({'status':200, 'data':{'msg':'Comment Publish Success!'}})
        return JsonResponse({'status':500, 'data':{'msg':'Server Error, Please Try Again'}})
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})

'''User Center'''
@csrf_exempt
def UserCommentApi(request):
    # 根據用戶id獲取用戶評論紀錄
    if request.method == 'GET':
        userId = request.GET.get('id')
        if userId != None or userId !=0:
            try:
                user = RecipeUser.objects.get(id=userId)
                user_number = user.number
                
            except:
                return JsonResponse({'status':404,'data':{'msg':'Missing user id!'}}, safe=False) 
            # 根據用戶編號找評論
            # 現在推薦的用戶是地16個用戶，對應的用戶編號是：8801839daec61027
            comments = CookedComment.objects.filter(user='8801839daec61027')
            mycomments = CookedComment.objects.filter(user='1')
            #print(comment)
            comment_list = []
            for mycomment in mycomments:
                try:
                    recipe = Recipe.objects.get(number = mycomment.recipe+'\n')
                    data = {
                        'recipeId':recipe.id,
                        'recipeName':recipe.name,
                        'rating':mycomment.rating,
                        'comment':mycomment.content,
                        'img':recipe.img
                    }
                    comment_list.append(data)
                except:
                    print('Can not found recipe: ', mycomment.recipe)
            for comment in comments:
                try:
                    recipe = Recipe.objects.get(number = comment.recipe+'\n')
                    data = {
                        'recipeId':recipe.id,
                        'recipeName':recipe.name,
                        'rating':comment.rating,
                        'comment':comment.content,
                        'img':recipe.img
                    }
                    comment_list.append(data)
                except:
                    print('Can not found recipe: ', comment.recipe)
            
            return JsonResponse({'status':200, 'data':{'comment_list':comment_list}}, safe=False)
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})

@csrf_exempt
def UserLikeApi(request):
    # 獲取用戶收藏食譜列表
    if request.method=='GET':
        id = request.GET.get('id')
        try:
            like_records = UserLike.objects.filter(user=id).order_by('-timestamp')
            serializer = UserLikeSerializer(like_records, many=True)
            like_list = []
            for like in like_records:
                try:
                    recipe = Recipe.objects.get(id=like.recipe)
                    like_list.append(oneRecipeOutlineHandler(recipe=recipe))
                except:
                    pass
            # return {'id': 0, 'author':'', 'title':'', 'img':''}
            return JsonResponse({'status':200, 'data':{'like_list':like_list}})
        except:
            return JsonResponse({'status':201, 'data':{'msg':'No Data Yet!'}})
    elif request.method=='PUT':
        # {'user':1, 'recipe':1, 'timestamp':'2023-05-11 10:13:34'}
        # fields={'id', 'user', 'recipe', 'timestamp'}
        data=jsonRequestDecode(request=request)
        # 避免重複添加
        try:
            history = UserLike.objects.get(user=data['user'], recipe=data['recipe'])
            history.delete()
            try:
                check = UserLike.objects.get(user=data['user'], recipe=data['recipe'])
                return JsonResponse({'status':500, 'data':{'msg':'Server Error, Please Try Again!'}})
            except:
                return JsonResponse({'status':200, 'data':{'msg':'Like Deleted!'}})
        except:
            model = UserLike(user=data['user'], recipe=data['recipe'], timestamp=data['timestamp'])
            model.save()
            # 確認是否添加成功
            try:
                history = UserLike.objects.get(user=data['user'], recipe=data['recipe']) 
                return JsonResponse({'status':200, 'data':{'msg':'Like Added!'}})
            except:
                return JsonResponse({'status':500, 'data':{'msg':'Server Error, Please Try Again!'}})
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})

@csrf_exempt    
def UserRecipeApi(request):
    # 管理用戶發布的食譜
    if request.method == 'GET':
        # 獲取用戶發布的食譜列表
        userId = request.GET.get('id')
        user = User.objects.get(id=userId)
        publishes = Recipe.objects.filter(author=user.user_name)
        publish_list = recipeMyHandler(publishes=publishes, user_name=user.user_name)
        return JsonResponse({'status':200, 'data':{'recipe_list':publish_list}})
    elif request.method == 'PUT':
        # 更改食譜信息
        data = jsonRequestDecode(request=request)
        recipeId = data['id']
        keys = data['keys']
        datas = data['datas']
        recipe = Recipe.objects.get(id=recipeId)
        #{'name':'', 'category':[''], 'author':'', 'step':[''], 'component':[''], 'intro':'', 'img':''}
        for key, data in zip(keys, datas):
            if key == 'name':
                recipe.name = data
            elif key == 'category': 
                recipe.category = ListToString(list=data)
            elif key == 'step':
                recipe.step = ListToString(list=data)
            elif key == 'component':
                recipe.component = ListToString(list=data)
            elif key == 'intro':
                recipe.intro = data
        recipe.save()
        updated_recipe = Recipe.objects.get(id=recipeId)
        serializer = RecipeSerializer(updated_recipe)
        return JsonResponse({'status':200, 'data':{'recipe':serializer.data}})
    elif request.method == 'DELETE':
        # 刪除食譜
        data = jsonRequestDecode(request=request)
        recipeId = data['id']
        try:
            check = Recipe.objects.get(id=recipeId).delete()
            if check[0] > 0:
                return JsonResponse({'status':200, 'data':{'msg':'Recipe Deleted!'}})
            else:
                return JsonResponse({'status':500, 'data':{'msg':'No Data Been Deleted, Please Try Again!'}})
        except:
            return JsonResponse({'status':200, 'data':{'msg':'Recipe Has Already Been Deleted!'}})
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})

''' Recipe Publish '''
@csrf_exempt
def PublishApi(request):
    # 食譜發布
    if request.method=='GET':
        return JsonResponse({'status':200, 'data':{'msg':'GET Request'}}, safe=False)
    elif request.method=='POST':
        # {'name':'', 'category':[''], 'author':'', 'step':[''], 'component':[''], 'intro':'', 'img':''}
        data = jsonRequestDecode(request=request)
        print(data)
        number = str(int(time.time()))   # 為了避免與當前的食譜編號重複，使用時間戳作為編號
        name = data['name']
        categoryList = data['category']
        category = ListToString(list=categoryList)
        author = data['author']
        componentList = data['component']
        component = ListToString(list=componentList)
        stepList = data['step']
        step = ListToString(list=stepList)
        intro = data['intro']
        like_count = 0
        img = data['img']
        if img :
            print('Start Inserting New Recipe...')
            print(intro)
            model = Recipe(number=number, name = name, category=category, author=author, component=component, step=step,like_count=like_count, intro=intro, img=img)
            model.save()
            print('Insert Compelete.')
            # 檢查是否成功添加
            try:
                history = Recipe.objects.get(number=number)
                return JsonResponse({'status':200, 'data':{'msg':'Publish Success!'}})
            except:
                return JsonResponse({'status':500, 'data':{'msg':'Server Error!'}})
        return JsonResponse({'status':404, 'data':{'msg':'Picture Upload Failed!'}}) 
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}}, safe=False)


'''
Search
'''
@csrf_exempt
def SearchApi(request):
    # 關鍵字查詢
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        userId = request.GET.get('userId')
        # 標題查詢
        title_result = Recipe.objects.filter(name__contains=keyword).order_by('-like_count')
        serializer = RecipeOutlineSerializer(title_result, many=True)
        recipe_list = recipeOutlineHandler(serializer=serializer, user=userId)
        return JsonResponse({'status':200, 'data':{'recipe_list':recipe_list}}, safe=False)
        # 分類查詢
        # 食材查詢
        # 簡介查詢
        # 步驟茶訓
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}}, safe=False)

'''Category'''

@csrf_exempt
def CategorySearchApi(request):
    # 食譜分類查詢
    if request.method=='GET':
        categoryId = request.GET.get('categoryId')
        userId = request.GET.get('userId')
        if categoryId is None:
            category_list = RecipeCategory.objects.all()
            serializer = RecipeCategorySerializer(category_list, many=True)
            category_list = categoryHandler(serializer=serializer)
            return JsonResponse({'status':200, 'data':{'category_list':category_list}}, safe=False)
        else:
            try:
                category = RecipeCategory.objects.get(id=categoryId)
                name = category.name
                recipes = Recipe.objects.filter(category__contains=name).order_by('-like_count')
                serializer = RecipeOutlineSerializer(recipes, many=True)
                recipe_list = recipeOutlineHandler(serializer=serializer, user=userId)
                return JsonResponse({'status':200, 'data':{'recipe_list':recipe_list}}, safe=False)
            except:
                return JsonResponse({'status':500, 'data':{'msg':'Server Error!'}})
    return JsonResponse({'status':404, 'data':{'msg':'Page Not Found!'}}, safe=False)

@csrf_exempt
def CategoryBlurApi(request):
    # 模糊查詢分類
    if request.method=='GET':
        keyword = request.GET.get('key')
        category_result = RecipeCategory.objects.filter(name__contains=keyword)
        serializer = RecipeCategorySerializer(category_result, many=True)
        return JsonResponse({'status':200, 'data':{'category_list':serializer.data}}, safe=False)
    return JsonResponse({'status':400, 'data':{'msg':'Page Not Found!'}})
'''
Utils and Handlers
'''


import numpy as np
import pandas as pd
import faiss
import csv

#user_path = '/Users/sunny/Desktop/MaFoodyBackEnd/demo/App/embedding/user_embedding2.npy'
user_path = current_working_dir+ '/App/Final_Results/Embeddings/user_embedding.npy'
#item_path = '/Users/sunny/Desktop/MaFoodyBackEnd/demo/App/embedding/item_embedding2.npy'
item_path = current_working_dir + '/App/Final_Results/Embeddings/item_embedding.npy'
feature_path = current_working_dir + '/App/feature_dict/'

# 數據加載
def load_embedding(user_path, item_path):
    user_embedding = np.load(user_path)
    item_embedding = np.load(item_path)
    #print(type(user_embedding), user_embedding.shape)
    #print(type(item_embedding), item_embedding.shape)
    recipe_embedding = pd.DataFrame(data={'id':[i for i in range(1,len(item_embedding)+1)], 'features': [features for features in item_embedding]})
    #print(recipe_embedding.head(4))
    # 理想的存儲格式是 物品id＋embedding向量
    return recipe_embedding

# 構建索引
def build_index(dimension, ids, datas):
    index = faiss.IndexFlatL2(dimension)
    # 封裝自己的id
    index2 = faiss.IndexIDMap(index)
    index2.add_with_ids(datas, ids)
    # 打印數據行數
    #print(index.ntotal)
    return index, index2

# 輸入用戶id，搜索物品列表
def select_by_user_id(user_id, index2):
    user_embedding = np.load(user_path)
    # 暫時以數據本來的順序當作用戶id, 這裡注意shape要（1, 32)
    feature = np.array([user_embedding[user_id]])
    # 格式要求：<class 'numpy.ndarray'> (1, 32) float32
    #print(type(feature), feature.shape, feature.dtype)
    # 設定選取範圍
    topk = 1000
    # 搜索
    D, I = index2.search(feature, topk)
    #print(I.shape, type(I))
    # 這個Ｉ就是食譜的id列表
    #print(I)
    return I

def getRecommendIdList(userId):
    df = load_embedding(user_path=user_path, item_path=item_path)
    # 構建ids，將所有id整合成ndarray，並且每個id都是int64類數據
    ids = df['id'].values.astype(np.int64)
    #print(type(ids), ids.shape, ids.dtype)
    # 記錄一下ids的長度
    ids_size = ids.shape[0]

    # 構建datas
    # 方式不限，但要求是ndarray且數據要是float32
    datas = np.load(item_path)
    #print(type(datas), datas.shape, datas.dtype)
    # 這裡data的維度是（物品數, 特徵數）我之前用DSSM模型抽取的特徵數是32，所以維度就是32
    dimension = datas.shape[1]
    index, index2 = build_index(dimension=dimension, ids=ids, datas=datas)

    # 搜索id為16的用戶
    recommend_list = select_by_user_id(user_id=16, index2=index2)
    recommend_list = recommend_list[0]
    return recommend_list.tolist()

# 從特徵字典中獲取對應index的原特徵值
def read_feature_reverse(feature_name, target_indexs):
    # 讀取保存的特徵索引文件
    feature_index = {}
    with open(feature_path+feature_name+'.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳過標題行
        # 通過index獲取原本的feature
        for row in reader:
            feature_index[row[1]] = int(row[0])

    # 假設我們有一個新的特徵數據 new_features = ['A', 'B', 'C'] 需要是string類型
    new_features = target_indexs

    # 將新的特徵數據映射到特徵索引
    mapped_features = [feature_index.get(str(feature), -1) for feature in new_features]

    #print(mapped_features)
    return mapped_features

def oneRecipeOutlineHandler(recipe):
    data = {
        "id": recipe.id,
        "name": recipe.name,
        "author": recipe.author.replace('https://icook.tw/users/',''),
        "img": recipe.img
    }
    return data

def recipeOutlineHandler(serializer,user):
    recipe_list = []
    for recipe in serializer.data:
        author_number = recipe['author'].replace('https://icook.tw/users/','')
        data = {
            "id": recipe['id'],
            "name": recipe['name'],
            "author": author_number,
            "img": recipe['img'],
            'isLike':True
        }
        recipe_list.append(data)
    return recipe_list

'''const mockData={
    userName:'Jhon Mayer',
    title:'banana cup cake',
    like: 4,
    view: 10,
    isLike:true,
}'''
def recipeMyHandler(publishes, user_name):
    recipe_list = []
    for publish in publishes[0:30]:
        data ={
            "id":publish.id,
            "title":publish.name,
            "userName":user_name,
            "like":publish.like_count,
            "view":random.choice(range(1,999)),
            "isLike":True,
            "img":publish.img,
        }
        recipe_list.append(data)
    return recipe_list

def recipeDetailHandler(serializer):
    replace_key = ['category','component','step','cooked']
    recipeNumber=serializer.data['number'].replace('\n','')
    replace_dict={}
    cooked_count=0
    rating=5
    for key in replace_key:
        if serializer.data[key] is not None:
            if key=='cooked':
                temp_list= serializer.data[key].split('%')
                temp_list.pop()
                rating_list = []
                user_list = []
                for i in range(len(temp_list)):
                    temp_list[i] = temp_list[i].replace('https://icook.tw/users/','')
                    rating_list.append(getRatingByUserNum(temp_list[i], recipeNumber))
                    if len(rating_list[i]) != 0:
                        user_list.append({'commentId':rating_list[i]['id'],'name':getUserNameByNumber(temp_list[i])})
                replace_dict[key]=user_list
                cooked_count = len(user_list)
                rating = averageRatingCal(rating_list)

            else:
                temp_list= serializer.data[key].split('%')
                temp_list.pop()
                replace_dict[key]=temp_list
        else:
            replace_dict[key]=serializer.data[key]
            if key=='cooked':
                cooked_count=0
                rating=5
    data = {
        "id": serializer.data['id'],
        "name": serializer.data['name'],
        "category": replace_dict["category"],
        "author": serializer.data['author'].replace('https://icook.tw/users/',''),
        "component": replace_dict['component'],
        "step": replace_dict['step'],
        "like_count": serializer.data['like_count'],
        #"cooked": replace_dict['cooked'],
        'cooked':replace_dict['cooked'],
        'cookedCount':cooked_count,
        'rating':rating,
        "intro": serializer.data['intro'],
        "img": serializer.data['img']
    }
    return data
    
def getRatingByUserNum(userNumber, recipeNumber):
    if userNumber=='SilviaChang':
        comment = CookedComment.objects.filter(user='1', recipe=recipeNumber)
    else: 
        comment = CookedComment.objects.filter(user=userNumber, recipe=recipeNumber)
    serializer = CookedCommentSerializer(comment, many=True)
    if len(serializer.data)>0:
            return serializer.data[0]
    return []
    

def averageRatingCal(rating_list):
    sum = 0.0
    count = 0
    for rating in rating_list:
        if rating !=[]:
            sum+=rating['rating']
            count += 1
    if count==0:
        return 0
    else:
        result = sum/count
        return result

def getUserNameByNumber(userNumber):
    print(userNumber)
    if userNumber=='1' or userNumber== 'SilviaChang':
        return 'SilviaChang'
    user = RecipeUser.objects.get(number=userNumber)
    serializer = RecipeUserSerializer(user)
    return serializer.data['name']

def recipeCommentHandler(serializer):
    comment_list = []
    for comment in serializer:
        data={
            'name':getUserNameByNumber(comment['user']),
            'rating':comment['rating'],
            'content':comment['content'],
            'timestamp':comment['timestamp'].replace('T',' ').replace('Z',''),
            'img':comment['img']
        }
        comment_list.append(data)
    return comment_list


def categoryHandler(serializer):
    categories  = serializer.data
    category_list = []
    for category in categories:
        # 大標題
        if category['root']==0:
            id = category['id']
            data = []
            # 子標題
            for item in categories:
                if item['root'] == id:
                    subData=[]
                    # 葉子元素
                    for subItem in categories:
                        if subItem['root'] == item['id']:
                            bottom={
                                'categoryId':subItem['id'],
                                'name':subItem['name'],
                            }
                            subData.append(bottom)
                    sub={
                        'categoryId':item['id'],
                        'name':item['name'],
                        'data':subData
                    }
                    data.append(sub)
            section={
                'id':id,
                'title':category['name'],
                'data':data
            }
            category_list.append(section)
    return category_list

def jsonRequestDecode(request):
    body = request.body
    body_str = body.decode()
    data = json.loads(body_str)
    return data

def ListToString(list):
    line = ''
    for element in list:
        line += element+'%'
    return line