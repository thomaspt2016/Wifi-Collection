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
    path('reports', views.ReportsView.as_view(), name='reports'),
    path('generalsetting', views.GeneralSettingView.as_view(), name='generalsetting'),
    path('apisetting', views.APISettingView.as_view(), name='apisetting'),
    path('activecheck/<int:id>', views.AcountDisable.as_view(), name='activecheck'),
    path('searchuser',views.SearchUserView.as_view(),name='searchuser')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)