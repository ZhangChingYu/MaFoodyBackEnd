from django.urls import re_path as url
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from mockApp import views
from django.views.static import serve

urlpatterns=[
    url(r'^test$',views.dbTestApi),
    url(r'^test/([0-9]+)$',views.dbTestApi),
    url(r'^mafoody/pictureupload$', views.picture),
    url(r'^mafoody/avatar$', views.AvatarUpload),
    url(r'^mafoody/pictureupdate', views.PictureUpdate),
    url(r'^mafoody/comment/picture', views.CommentPicture),
    #url(r"^files/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}, name="files"),
    url(r"^(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
