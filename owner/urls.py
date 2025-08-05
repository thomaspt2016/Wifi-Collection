"""
URL configuration for wificollection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from owner import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'owner'

urlpatterns = [
    path('ownerhome',views.Ownerhomeview.as_view(),name='ownerhome'),
    path('ownclients',views.OwnerClientsView.as_view(),name='ownclients'),
    path('collectionagents',views.CollectionAgentsView.as_view(),name='collectionagents'),
    path('internetplans', views.InternetplansView.as_view(), name='internetplans'),
    path('codeupload', views.CodeUploadView.as_view(), name='codeupload'),
    path('codepoolstat', views.CodePoolStatView.as_view(), name='codepoolstat'),
    path('payments', views.PaymentsView.as_view(), name='payments'),
    path('activecheck/<int:id>', views.AcountDisable.as_view(), name='activecheck'),
    path('searchuser',views.SearchUserView.as_view(),name='searchuser'),
    path('download/<int:upload_id>/', views.download_file_view, name='downloadfile'),
    path('codesearch',views.SearchViewCodes.as_view(),name='codesearch' ),
    path('codedeactivation/<str:invid>', views.CodeDeactivation.as_view(), name='codedeactivation'),
    path('userupanddown/<int:id>',views.UserPromotions.as_view(),name='userupanddown'),
    path('profiledetail/<int:id>', views.ProfiledetailView.as_view(), name='profiledetails'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)