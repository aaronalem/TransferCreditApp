from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('sisapi/', views.sisapi, name='sisapi'), #this is for testing
    path('search/', views.search, name='search'),
    path('searchresults/', views.equivalencies, name='equivalencies'),
    path('request/', views.request, name='request'),
    path('addrequest/', views.addRequest, name='addRequest'),
    path('viewrequest/<int:id>', views.viewRequest, name='viewrequest'),
    path('updaterequest/', views.update_request, name="update_request"),
    path('viewallrequests/', views.viewAllRequests, name="viewallrequests"),
    path('viewcourseinfo/<str:department>/<str:catalog_number>/', views.viewCourseInfo, name='viewcourseinfo'),
]