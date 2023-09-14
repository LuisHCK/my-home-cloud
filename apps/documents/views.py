"""Views for document center"""
import os
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.response import Response
from . import models, serializers


class FoldersViews(viewsets.ModelViewSet):
    """
        List directories
    """
    model = models.Folder
    serializer_class = serializers.FolderSerializer
    queryset = models.Folder.objects.filter(is_deleted=False)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FoldersViews, self).dispatch(*args, **kwargs)

    def list(self, request):
        """Retrieve a list of directories"""
        serializer = serializers.FolderListSerializer(self.queryset.filter(parent_folder=None), many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data['create_user'] = self.request.user.id
        return super().create(request, *args, **kwargs)


class SubFolderViews(viewsets.ModelViewSet):
    """
        Sub Folder views
    """
    model = models.Folder
    serializer_class = serializers.FolderSerializer
    queryset = models.Folder.objects\
        .filter(is_deleted=False)\
        .order_by('name')

    def create(self, request, folder_id, *args, **kwargs):
        parent = models.Folder.objects.get(id=folder_id)
        request.data['parent_folder'] = parent.id
        request.data['create_user'] = self.request.user.id
        return super().create(request, *args, **kwargs)


class FilesViews(viewsets.ModelViewSet):
    """
        Views for File
    """
    model = models.File
    serializer_class = serializers.FileSerializer
    queryset = models.File.objects.filter(is_deleted=False)

    def list(self, request, folder_id, *args, **kwargs):
        """Retrieve a list of files in a folder"""
        queryset = self.queryset.filter(
            folder_id=folder_id,
        )
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, folder_id, *args, **kwargs):
        request.data['folder'] = folder_id
        request.data['create_user'] = self.request.user.id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        obj = self.queryset.get(id=self.kwargs['pk'])
        serializer = serializers.FileUpdateSerializer(
            obj, data=request.data, partial=True)

        # Get req file
        req_file = self.request.FILES.get('file')
        print(req_file)
        if req_file:
            # Delete old file
            try:
                path = obj.file.path
                os.remove(path)
                obj.file.delete()
                obj.file = None
                obj.save()
            except:
                print('File not found')

            # update
            obj.file = req_file
            obj.save()

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class SearchView(viewsets.ViewSet):
    queryset = models.Folder.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            is_hidden=False,
            is_deleted=False)

    def list(self, request, *args, **kwargs):
        search_value = self.request.GET.get('value')

        if not search_value:
            return Response({
                'folders': [],
                'files': []
            })

        # Search in available folders
        folder_searchvector = SearchVector(
            'name',
            'comment')

        folder_search_qs = models.Folder.objects\
            .annotate(
                search=folder_searchvector)\
            .filter(
                Q(search__icontains=search_value) | Q(search=search_value)
            )\
            .distinct('id')

        # search in available files
        file_searchvector = SearchVector(
            'name',
            'comment')

        file_search_qs = models.File.objects\
            .annotate(search=file_searchvector)\
            .filter(
                Q(search__icontains=search_value) | Q(search=search_value)
            )\
            .distinct('id')

        return Response({
            'folders': serializers.FolderListSerializer(folder_search_qs, many=True).data,
            'files': serializers.FileSerializer(file_search_qs, many=True).data
        })


class RootFolderView(viewsets.ViewSet):
    queryset = models.Folder.objects.none()

    def list(self, request, format=None):
        folders_queryset = models.Folder.objects\
            .filter(parent_folder=None)
        files_queryset = models.File.objects\
            .filter(folder=None)

        return Response({
            'folders': serializers.FolderListSerializer(folders_queryset, many=True).data,
            'files': serializers.FileSerializer(files_queryset, many=True).data
        })
