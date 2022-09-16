from rest_framework import serializers
from portal.models import Personnel,Rule,Device
from portal.models import HealthScan,SafetyScan,Event

'''        
class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
'''

class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Device
        fields = '__all__'

class HealthScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScan
        fields = '__all__'

class SafetyScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyScan
        fields = '__all__'

class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    HealthResult = HealthScanSerializer(source='healthscan_set',many=True, read_only=True)
    SafetyResult = SafetyScanSerializer(source='safetyscan_set',many=True, read_only=True)
    Person = PersonnelSerializer()
    Rule = RuleSerializer()
    Device = DeviceSerializer()
    #name = serializers.CharField(source='personnel.name')
    #person = PersonnelSerializer(many=True)
    class Meta:
        model = Event
        #fields = ['EventID','Health_Details','Safety_Details','Person_Details']
        fields = '__all__'

class EventSerializerx(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
    

