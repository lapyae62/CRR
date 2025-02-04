"""
Definition of models.
"""

from django.db import models



class Reports(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    regionname = models.CharField(max_length=50, blank=True, null=True)
    crimetype = models.CharField(max_length=50, blank=True, null=True)
    reportdate = models.DateTimeField(auto_now_add=True)  # Automatically sets the current date and time
    description = models.TextField(blank=True, null=True)  # Changed to TextField for better description storage
    assignedpoliceid = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    casedate = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Reports'


class EvidentImages(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    image = models.ImageField(upload_to='evidence/images/', blank=True, null=True)  # Handles image uploads
    cid = models.ForeignKey(Reports, on_delete=models.CASCADE, related_name='evident_images')

    class Meta:
        managed = True
        db_table = 'EvidentImages'


class EvidentVideos(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    video = models.FileField(upload_to='evidence/videos/', blank=True, null=True)  # Handles video uploads
    cid = models.ForeignKey(Reports, on_delete=models.CASCADE, related_name='evident_videos')

    class Meta:
        managed = True
        db_table = 'EvidentVideos'


class EvidentFiles(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incremented ID
    file = models.FileField(upload_to='evidence/files/', blank=True, null=True)  # Handles file uploads
    cid = models.ForeignKey(Reports, on_delete=models.CASCADE, related_name='evident_files')

    class Meta:
        managed = True
        db_table = 'EvidentFiles'

class Users(models.Model):
    id=models.AutoField(primary_key=True)
    username=models.CharField(max_length=50,blank=True,null=True)
    password=models.CharField(max_length=50,blank=True,null=True)
    policeid=models.IntegerField(max_length=6,blank=True,null=True)
    rank=models.CharField(max_length=20,null=True,blank=True)
    email=models.CharField(max_length=20,null=True,blank=True)
    state=models.CharField(max_length=20,null=True,blank=True)
    city=models.CharField(max_length=20,null=True,blank=True)
    station=models.CharField(max_length=20,null=True,blank=True)

    class Meta:
            managed=True
            db_table='Users'

class RegionChangeRequests(models.Model):
    id=models.AutoField(primary_key=True)
    userid=models.IntegerField(null=True,blank=True)
    name=models.CharField(max_length=20,null=True,blank=True)
    policeid=models.IntegerField(max_length=6,null=True,blank=True)
    rank=models.CharField(max_length=20,null=True,blank=True)
    currentlocation=models.CharField(max_length=30,null=True,blank=True)
    updatelocation=models.CharField(max_length=30,null=True,blank=True)
    confirmation1=models.CharField(null=True,blank=True,max_length=20)
    confirmation2=models.CharField(null=True,blank=True,max_length=20)

    class Meta:
            managed=True
            db_table='RegionChangeRequests'


class RankChangeRequests(models.Model):
    id=models.AutoField(primary_key=True)
    userid=models.IntegerField(null=True,blank=True)
    name=models.CharField(max_length=20,null=True,blank=True)
    policeid=models.IntegerField(max_length=6,null=True,blank=True)
    state=models.CharField(max_length=20,null=True,blank=True)
    city=models.CharField(max_length=20,null=True,blank=True)
    station=models.CharField(max_length=20,null=True,blank=True)
    currentrank=models.CharField(max_length=20,null=True,blank=True)
    confirmation=models.CharField(max_length=20,null=True,blank=True)

    class Meta:
        managed=True
        db_table='RankChangeRequests'

class FeedBack:
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=20,null=True,blank=True)
    email=models.CharField(max_length=20,null=True,blank=True)
    message=models.CharField(max_length=900,null=True,blank=True)

    class Meta:
        managed=True
        db_table='FeedBack'

class CaseReports(models.Model):
    id=models.AutoField(primary_key=True)
    reportid=models.IntegerField(null=True,blank=True)
    state=models.CharField(max_length=20,null=True,blank=True)
    city=models.CharField(max_length=20,null=True,blank=True)
    station=models.CharField(max_length=20,null=True,blank=True)
    suspects=models.CharField(max_length=20,null=True,blank=True)
    culprit=models.CharField(max_length=20,null=True,blank=True)
    casedescription=models.CharField(max_length=1000,null=True,blank=True)
    officer=models.CharField(max_length=20,null=True,blank=True)
    chiefofficer=models.CharField(max_length=20,null=True,blank=True)
    reportdate = models.DateTimeField(auto_now_add=True)
    confirm=models.CharField(max_length=20,null=True,blank=True)

    class Meta:
        managed=True
        db_table='CaseReports'
