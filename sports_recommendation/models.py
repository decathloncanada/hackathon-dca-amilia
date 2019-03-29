from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class Location(models.Model):
    locationId = models.IntegerField(default=-1, primary_key=True)
    name = models.CharField(max_length=255, default="", blank=True, null=True)
    fullName = models.CharField(
        max_length=255, default="", blank=True, null=True
    )
    description = models.CharField(
        max_length=255, default="", blank=True, null=True
    )
    telephone = models.CharField(
        max_length=12, default="", blank=True, null=True
    )
    telephoneExtension = models.CharField(
        max_length=6, default="", blank=True, null=True
    )
    parentId = models.IntegerField(default=-1, blank=True, null=True)
    topParentId = models.IntegerField(default=-1, blank=True, null=True)
    ancestorIds = ArrayField(
        models.IntegerField(default=-1, blank=True, null=True)
    )
    address = models.CharField(
        max_length=255, default="", blank=True, null=True
    )
    keywords = JSONField(blank=True, null=True, default=list)

    def __str__(self):
        return self.name

