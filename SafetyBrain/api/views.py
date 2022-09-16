from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from portal.models import Device,Personnel,Rule
from portal.models import HealthScan,SafetyScan,Event
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serialisers import EventSerializer,RuleSerializer,EventSerializerx,PersonnelSerializer,DeviceSerializer,HealthScanSerializer,SafetyScanSerializer
from portal.models import Event as Events
import json,base64

from django.shortcuts import get_object_or_404
from django.http import Http404

import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

import requests


class Login(APIView):
    def post(self, request, format=None):
        username = self.request.data.get('username')
        password = self.request.data.get("password")
        deviceid = self.request.data.get("deviceid")
        print(username,password,deviceid)
        try:
            post = Device()
            post.Name = deviceid
            post.UniqueID = deviceid
            post.save()
        except:
            pass
        isvaliddevice = Device.objects.filter(UniqueID = deviceid).filter(Enable = True).count()
        if(isvaliddevice == 0):
            return Response({"success": 0 ,"detail": "device not enabled"},status=status.HTTP_401_UNAUTHORIZED)  
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"success": 0 ,"detail": "user not found"},status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        fullname = user.first_name + " " + user.last_name
        return Response({"success": 1,"detail": "","token": token.key,'username':user.username,'fullname':fullname},status=status.HTTP_200_OK)

class Logout(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class Profile(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        fullname = request.user.first_name + " " + request.user.last_name
        return Response({"success": 1,"detail": "",'username':request.user.username,'fullname':fullname},status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})


def decodeDesignImage(data):
    try:
        data = base64.b64decode(data.encode('UTF-8'))
        buf = io.BytesIO(data)
        img = Image.open(buf)
        return img
    except:
        return None

class Event(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = Events.objects.all()
        print(events.values())
        eventsSerial = EventSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        lat = self.request.data.get('lat')
        lng = self.request.data.get("lng")
        deviceid = self.request.data.get("deviceid")
        personid = self.request.data.get("person")
        ruleid = self.request.data.get("rule")
        health = self.request.data.get("health")
        image = self.request.data.get("image")
        device = None
        try:
            device = Device.objects.get(UniqueID = deviceid, Enable=True) 
        except Device.DoesNotExist:
            return Response({"success": 0 ,"detail": "device not enabled"},status=status.HTTP_401_UNAUTHORIZED)
        except Device.MultipleObjectsReturned:
            return Response({"success": 0 ,"detail": "device not enabled"},status=status.HTTP_401_UNAUTHORIZED)

        person = None
        try:
            person = Personnel.objects.get(UniqueID = personid) 
        except Personnel.DoesNotExist:
            person = None
        except Personnel.MultipleObjectsReturned:
            person = None
        
        rule = None
        try:
            rule = Rule.objects.get(Name = ruleid) 
        except Rule.DoesNotExist:
            rule = None
        except Rule.MultipleObjectsReturned:
            rule = None

        img = decodeDesignImage(image)
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        post = Events()
        post.Person = person
        post.Rule = rule
        post.Device = device
        post.Health = health
        post.Lattitude = lat
        post.Longitude = lng
        post.Photo = InMemoryUploadedFile(img_io, field_name=None, name='token'+".jpg", content_type='image/jpeg', size=img_io.tell, charset=None)
        post.processed = True
        post.save()
        print(post.Photo.url)
        try:
            response = requests.get('http://127.0.0.1:8000' + post.Photo.url)
            image = ("data:" + response.headers['Content-Type'] + ";" +"base64," + base64.b64encode(response.content).decode("utf-8"))
            url = 'http://127.0.0.1:8080/api/v3/scan/'
            data = {"image": image}
            r = requests.post(url = url, json = data)
            result = json.loads(r.text)
            sscan = SafetyScan()
            sscan.EventID = post
            sscan.Hat = result['Hat']
            sscan.Gloves = result['Gloves']
            sscan.Vest = result['Vest']
            sscan.Boot = result['Boot']
            sscan.Glasses = result['Glasses']
            sscan.Mask = result['Mask']
            img = decodeDesignImage(result['result'])
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            sscan.Photo = InMemoryUploadedFile(img_io, field_name=None, name='token'+".jpg", content_type='image/jpeg', size=img_io.tell, charset=None)
            sscan.save()
            post.safetyprocessed = True
            post.save()
        except:
            print('Problem Occured while processing safety data')
        
        try:
            url = 'http://127.0.0.1:5000/api/v3/qr/'
            data = {"qr": health}
            r = requests.post(url = url, json = data)
            result = json.loads(r.text)
            print(result)
            hscan = HealthScan()
            hscan.EventID = post
            hscan.Category = 0;
            hscan.Name = result['name'];
            hscan.IDn = result['id'];
            hscan.Mobile = result['mobile'];
            hscan.CodeType = result['code_type'];
            hscan.Category = 0;
            hscan.Typex = result['type'];

            hscan.GenTime = result['gen_time'];
            hscan.ExpTime = result['exp_time'];

            hscan.DPIDate = result['last_dpi_date'];
            hscan.PCRDate = result['last_pcr_date'];

            hscan.DPIResult = result['last_dpi'];
            hscan.PCRResult = result['last_pcr'];

            hscan.Excemption = result['excemption'];
            hscan.Junior = result['junior'];
            hscan.Senior = result['senior'];
            hscan.Vaccinated = result['vaccinated'];
            hscan.Visitor = result['visitor'];
            hscan.Volunteer = result['volunteer'];
            hscan.save()
            post.healthprocessed = True
            post.save()
        except:
            print('Problem Occured while processing health data')
        events = Events.objects.get(pk = post.pk)
        eventsSerial = EventSerializer(events)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
        return Response({"success": 1 ,"detail": "event added"})

class Devices(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = Device.objects.all()
        print(events.values())
        eventsSerial = DeviceSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})

class Devices(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = Device.objects.all()
        print(events.values())
        eventsSerial = DeviceSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})


class HScans(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = HealthScan.objects.all()
        print(events.values())
        eventsSerial = HealthScanSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})

class SScans(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = SafetyScan.objects.all()
        print(events.values())
        eventsSerial = SafetyScanSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})

class Persons(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = Personnel.objects.all()
        print(events.values())
        eventsSerial = PersonnelSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})

class Rules(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        events = Rule.objects.all()
        print(events.values())
        eventsSerial = RuleSerializer(events, many=True)
        return Response(json.loads(json.dumps(eventsSerial.data)),status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        return Response({"success": 0 ,"detail": "request not enabled"})