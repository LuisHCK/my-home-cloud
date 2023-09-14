"""Serializers for Document Center"""
from django.contrib.auth.models import User
from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = User
        fields = ('id', )


class FileSerializer(serializers.ModelSerializer):
    """File Serializer"""
    create_user_obj = UserSerializer(source='create_user', read_only=True)
    size = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = models.File
        fields = '__all__'

    def get_size(self, obj):
        try:
            return obj.file.size
        except Exception:
            return 0

    def get_extension(self, obj):
        filename = obj.name.split('.')
        return filename[-1]

    def get_url(self, obj):
        if obj:
            return obj.file.url

    def get_location(self, obj):
        return obj.folder.name or 'Root folder'


class FileUpdateSerializer(serializers.ModelSerializer):
    """File serialzer for update only"""
    class Meta:
        model = models.File
        fields = '__all__'
        read_only_fields = ('file',)


class FolderListSerializer(serializers.ModelSerializer):
    """Folder List Serializer"""
    files = serializers.SerializerMethodField()
    create_user_obj = UserSerializer(source='create_user', read_only=True)
    location = serializers.SerializerMethodField()

    class Meta:
        model = models.Folder
        fields = '__all__'

    def get_files(self, obj):
        return obj.file_set.all().count()

    def get_location(self, obj):
        if obj.parent_folder:
            return obj.parent_folder.name
        else:
            return 'Root folder'


class FolderSerializer(serializers.ModelSerializer):
    """Folder serializer"""
    files = FileSerializer(source='file_set', many=True, read_only=True)
    sub_folders = serializers.SerializerMethodField()
    create_user_obj = UserSerializer(source='create_user', read_only=True)

    class Meta:
        model = models.Folder
        fields = '__all__'

    def get_sub_folders(self, obj):
        folders = obj.folder_set.all()\
            .filter(is_deleted=False)\
            .order_by('name')
        return FolderListSerializer(folders, many=True).data
