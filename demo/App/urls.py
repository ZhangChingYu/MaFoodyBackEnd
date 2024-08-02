from django.urls import re_path as url
from App import views
from django.conf import settings
from django.views.static import serve

urlpatterns=[
    url(r'^mafoody$',views.RecipeApi),
    url(r'^mafoody/([0-9]+)$',views.RecipeApi),
    url(r'^mafoody/recipeoutline/$',views.RecommendApi),
    url(r'^mafoody/trend/$',views.TranddApi),
    url(r'^mafoody/subscirbe/$',views.SubsrcibeApi),
    url(r'^mafoody/login/$',views.AuthenticationApi), 
    url(r'^mafoody/signup/$',views.SignUpApi),
    url(r'^mafoody/recipedetail/$',views.RecipeDetail),
    url(r'^mafoody/recipelikestate/$',views.RecipeLikeStateApi),
    url(r'^mafoody/recipedetail/comment/$',views.ShowRecipeCommentApi),
    url(r'^mafoody/category/$',views.CategorySearchApi),
    url(r'^mafoody/search/$',views.SearchApi),
    url(r'^mafoody/usercenter/comment$',views.UserCommentApi),
    url(r'^mafoody/usercenter/like$',views.UserLikeApi),
    url(r'^mafoody/usercenter/myrecipe$',views.UserRecipeApi),
    url(r'^mafoody/publish/$',views.PublishApi),
    url(r'^mafoody/publish/category/$',views.CategoryBlurApi),
    url(r'^mafoody/comment/publish/$',views.CommentPublishApi),
    #url(r"^(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]