from django.shortcuts import render
from threading import Timer, Event

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

import json,requests,base64

from portal.models import Device,Personnel,Rule
from portal.models import HealthScan,SafetyScan,Event
from api.serialisers import EventSerializer,RuleSerializer,EventSerializerx


# Create your views here.
def every_so_often():
    Events = Event.objects.filter(safetyprocessed = False,processed = False)
    for event in Events:
        try:
            EventsSerial = EventSerializerx(event)#, many=True
            ue = json.loads(json.dumps(EventsSerial.data))
            print(ue)
            #print(requests.get('http://127.0.0.1:8000/media/scans/1.jpg').content)
            response = requests.get('http://127.0.0.1:8000' + ue['Photo'])
            image = ("data:" + response.headers['Content-Type'] + ";" +"base64," + base64.b64encode(response.content).decode("utf-8"))
            url = 'http://127.0.0.1:8080/api/v3/scan/'
            data = {"image": image}
            r = requests.post(url = url, json = data)
            result = json.loads(r.text)
            sscan = SafetyScan()
            sscan.EventID = event
            sscan.Hat = result['Hat']
            sscan.Gloves = result['Gloves']
            sscan.Vest = result['Vest']
            sscan.Boot = result['Boot']
            sscan.Glasses = result['Glasses']
            sscan.Mask = result['Mask']
            sscan.save()
            event.safetyprocessed = True
            event.save()
        except:
            print('Problem Occured while processing safety data')

    Events = Event.objects.filter(healthprocessed = False,processed = False)
    for event in Events:    
        try:
            EventsSerial = EventSerializerx(event)#, many=True
            ue = json.loads(json.dumps(EventsSerial.data))
            print(ue)
            url = 'http://127.0.0.1:5000/api/v3/qr/'
            data = {"qr": ue['Health']}
            r = requests.post(url = url, json = data)
            result = json.loads(r.text)
            print(result)
            hscan = HealthScan()
            hscan.EventID = event
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
            event.healthprocessed = True
            event.save()
        except:
            print('Problem Occured while processing health data')

        
    Timer(10.0, every_so_often).start() 
#Timer(10.0, every_so_often).start() 

class Schedule(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        return Response(status=status.HTTP_200_OK)