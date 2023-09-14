"""Document models"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import JSONField
from datetime import datetime
from uuid import uuid4

class Folder(models.Model):
    """Folder model"""
    name = models.CharField(max_length=100)
    comment = models.TextField(blank=True, null=True)
    parent_folder = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=50, default='r-w')
    is_sys = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    create_user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        permissions = ()

    def save(self, *args, **kwargs):
        """Override save method"""
        self.updated_at = datetime.now()
        super().save()

    def get_all_children(self, include_self=True):
        """Return al child folders"""
        folder_list = []

        if include_self:
            folder_list.append(self)

        for child in Folder.objects.filter(parent_folder=self):
            _folder_list = child.get_all_children(include_self=True)
            if 0 < len(_folder_list):
                folder_list.extend(_folder_list)

        return folder_list

    def get_parents(self, name_only=True):
        """Retrieve parent folders"""
        if self.parent_folder:
            return Folder.objects.filter(id=self.parent_folder_id) | self.parent_folder.get_parents()
        else:
            return Folder.objects.none()


def upload_path_handler(instance, filename):
    """Upload file in custom storage"""
    extension = filename.split('.')[-1]
    random_uuid = uuid4()
    random_name = "{}.{}".format(random_uuid, extension)
    return "./storage/documents/files/{filename}".format(
        filename=random_name
    )


class File(models.Model):
    """File Model"""
    name = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    folder = models.ForeignKey(Folder, null=True, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=255, default='r-w')
    is_sys = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    file = models.FileField(upload_to=upload_path_handler, max_length=255)
    create_user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    meta_data = JSONField(default=dict)

    class Meta:
        permissions = ()

    def save(self, *args, **kwargs):
        """Override save method"""
        self.updated_at = datetime.now()
        # Set file name as default name
        if not self.pk:
            if not self.name:
                self.name = self.file.name
            else:
                self.file.name = self.name

        super().save()

    def __str__(self):
        return self.name

    def extension(self):
        return self.name.split('.')[-1]
