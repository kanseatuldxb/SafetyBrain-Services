from django.db import models
import uuid

def scan_upload_to(instance, filename):
    return 'scans/{filename}'.format(filename=filename)

def image_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

def processed_image_upload_to(instance, filename):
    return 'processed/{filename}'.format(filename=filename)
class Rule(models.Model):
    #RuleBase = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,)
    Name = models.CharField(max_length=50, blank=False, null=False)
    Hat = models.BooleanField(default=False)
    Gloves = models.BooleanField(default=False)
    Vest = models.BooleanField(default=False)
    Boot = models.BooleanField(default=False)
    Glasses = models.BooleanField(default=False)
    Mask = models.BooleanField(default=False) 

    def __str__(self):
        return  self.Name



class Personnel(models.Model):
    Name = models.CharField(max_length=64, blank=False, null=False)
    Photo = models.ImageField(upload_to=image_upload_to, blank=True, null=True)
    UniqueID = models.CharField(max_length=50, blank=False, null=True, default="")
    EmiratesID = models.CharField(max_length=16, blank=False, null=True, default="")
    ContactNo = models.CharField(max_length=13, blank=False, null=True, default="")
    Created = models.DateTimeField(auto_now_add=True)
    Modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.Name


class Device(models.Model):
    Name = models.CharField(max_length=64, blank=True, null=False, default="")
    UniqueID = models.CharField(max_length=50, blank=False, null=True,unique=True, default="")
    Enable = models.BooleanField(default=False)
    Created = models.DateTimeField(auto_now_add=True)
    Modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.Name
        
class Event(models.Model):
    EventID = models.CharField(max_length=50, blank=False, null=True, default=uuid.uuid4())
    Person = models.ForeignKey(Personnel,on_delete=models.CASCADE,blank=True, null=True)
    Rule = models.ForeignKey(Rule,on_delete=models.CASCADE,blank=True, null=True)
    Photo = models.ImageField(upload_to=scan_upload_to, blank=True, null=True)
    Health = models.CharField(max_length=300, blank=True, null=True, default="")
    Device = models.ForeignKey(Device,on_delete=models.CASCADE,blank=True, null=True)
    Lattitude = models.FloatField(default=0.0)
    Longitude = models.FloatField(default=0.0)

    action = models.BooleanField(default=False)

    processed = models.BooleanField(default=False)
    healthprocessed = models.BooleanField(default=False)
    safetyprocessed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
	    return self.EventID

    def save(self, *args, **kwargs):
	    super(Event, self).save(*args, **kwargs)

class HealthScan(models.Model):
    EventID = models.ForeignKey(Event,on_delete=models.CASCADE,blank=True, null=True)
    Name = models.CharField(max_length=50, blank=True, null=True, default="")
    IDn = models.CharField(max_length=20, blank=True, null=True, default="")
    Mobile = models.CharField(max_length=20, blank=True, null=True, default="")
    CodeType = models.CharField(max_length=20, blank=True, null=True, default="")
    Typex = models.CharField(max_length=20, blank=True, null=True, default="")
    Category = models.IntegerField(default=0)
    
    GenTime = models.DateTimeField(null=True)
    ExpTime = models.DateTimeField(null=True)
    
    DPIDate = models.DateTimeField(null=True)
    PCRDate = models.DateTimeField(null=True)
    
    DPIResult = models.CharField(max_length=20, blank=True, null=True)
    PCRResult = models.CharField(max_length=20, blank=True, null=True)
    
    Excemption = models.BooleanField(default=False)
    Junior = models.BooleanField(default=False)
    Senior = models.BooleanField(default=False)
    Vaccinated = models.BooleanField(default=False)
    Visitor = models.BooleanField(default=False)
    Volunteer = models.BooleanField(default=False)


    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
	    return self.Name

    def save(self, *args, **kwargs):
	    super(HealthScan, self).save(*args, **kwargs)


class SafetyScan(models.Model):
    EventID = models.ForeignKey(Event,on_delete=models.CASCADE,blank=True, null=True)
    Photo = models.ImageField(upload_to=processed_image_upload_to, blank=True, null=True)
    Hat = models.BooleanField(default=False)
    Gloves = models.BooleanField(default=False)
    Vest = models.BooleanField(default=False)
    Boot = models.BooleanField(default=False)
    Glasses = models.BooleanField(default=False)
    Mask = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
	    return str(self.pk)

    def save(self, *args, **kwargs):
	    super(SafetyScan, self).save(*args, **kwargs)