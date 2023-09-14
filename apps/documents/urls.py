"""URLS for Document Center"""
from rest_framework.routers import DefaultRouter
from . import views


# Create a router and register API Routes
ROUTER = DefaultRouter()
ROUTER.register(r'', views.RootFolderView)
ROUTER.register(r'search', views.SearchView)
ROUTER.register(r'folders', views.FoldersViews)
ROUTER.register(r'folders/(?P<folder_id>\d+)/files', views.FilesViews)

urlpatterns = ROUTER.urls
