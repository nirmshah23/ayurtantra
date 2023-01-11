from rest_framework import serializers
from api import models
from datetime import datetime

class MasterCodeCategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = models.MasterCodeCategory
        fields = '__all__'

class MasterCodesSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.MasterCodes
        fields = '__all__'

class PincodeSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Pincodes
        fields = '__all__'

class VyadhiCodeSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.VyadhiCode
        fields = '__all__'

class DoctorSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Doctor
        fields = '__all__'

class ClinicSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Clinic
        fields = '__all__'

class ClinicTimingsSerializer (serializers.ModelSerializer):
    #apiID = serializers.
    id = serializers.IntegerField(required=False, allow_null=True) #this is needed so that id is deserialized from the incoming request
    class Meta:
        model = models.ClinicTimings
        fields = '__all__'

class FacilitySerializer (serializers.ModelSerializer):
    timings = ClinicTimingsSerializer (many=True) #timings attribute should be same as the related name of the foreign key of related table
    class Meta:
        model = models.Clinic
        #depth = 1 # to include reverse relationship
        fields = '__all__'

    def create(self, validated_data):
        timings_data = validated_data.pop('timings', None)
        clinic = models.Clinic.objects.create(**validated_data)
        for timing in timings_data:
            #print (timing)
            #print (clinic.id)
            models.ClinicTimings.objects.create(clinic_id=clinic, **timing) #clinic_id is the foreign key model field that relates to parent table
        return clinic

    def update(self, instance, validated_data):

        instance.name = validated_data.get('name',instance.name)
        instance.address = validated_data.get('address',instance.address)
        instance.pincode = validated_data.get('pincode',instance.pincode)
        instance.city = validated_data.get('city',instance.city)
        instance.state = validated_data.get('state',instance.state)
        instance.phone = validated_data.get('phone',instance.phone)
        instance.status = validated_data.get('status',instance.status)
        instance.modified_date_time = validated_data.get('modified_date_time',instance.modified_date_time)
        instance.save()

        timings_data = validated_data.get('timings',None)

        for entry in timings_data:
            print (entry)
            if entry.get('id', None):
                print ('in update section')
                timing_entry = models.ClinicTimings.objects.get(id=entry.get('id', None), clinic_id=instance)
                timing_entry.weekday = entry.get('weekday',timing_entry.weekday)
                timing_entry.start_time = entry.get('start_time',timing_entry.start_time)
                timing_entry.end_time = entry.get('end_time',timing_entry.end_time)
                timing_entry.status = entry.get('status',timing_entry.status)
                #timing_entry.modified_date_time = entry.get('modified_date_time',timing_entry.modified_date_time)
                timing_entry.save()
            else:
                print ('in create section')
                entry.pop('clinic_id')
                models.ClinicTimings.objects.create(clinic_id=instance, **entry)

        return instance        

class MemberSerializer (serializers.ModelSerializer):
    open_visit_id = serializers.SerializerMethodField(read_only=True)    
    class Meta:
        model = models.Member
        fields = '__all__'

    def get_open_visit_id (self, Member):
         """ if Visit.objects.filter(member_id=Member.id, status=1, start_date_time__lt = datetime.now()).count() > 0:
             print ()
             return Visit.objects.filter(member_id=Member.id, status=1, start_date_time__lt = datetime.now()).count()
         else:
             return 0 """
         try:
            return models.Visit.objects.get(member_id=Member.id, status=1, start_date_time__lt = datetime.now()).pk
         except:
            return 0


class DoctorMemberViewSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.DoctorMember
        depth = 1
        fields = '__all__'

class DoctorMemberCreateSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.DoctorMember
        fields = '__all__'

class LifeStyleManagementSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.LifeStyleManagement
        fields = '__all__'


class AppointmentSerializer (serializers.ModelSerializer):
    facility_name = serializers.ReadOnlyField(source='clinic_id.name')
    member_first_name = serializers.ReadOnlyField(source='member_id.first_name')
    member_last_name= serializers.ReadOnlyField(source='member_id.last_name')
    member_dob = serializers.ReadOnlyField(source='member_id.dob')
    member_gender = serializers.ReadOnlyField(source='member_id.gender')
    member_phone = serializers.ReadOnlyField(source='member_id.phone')
    member_open_visit_id = serializers.SerializerMethodField(read_only=True)
    appointment_reason = serializers.ReadOnlyField(source='reason_code.description')

    class Meta:
        model = models.Appointment
        fields = '__all__'

    def get_member_open_visit_id (self, Appointment):
        try:
            return models.Visit.objects.get(member_id=Appointment.member_id, status=1, start_date_time__lt = datetime.now()).pk
        except:
            return 0

class KalpaKalpanaSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.KalpaKalpana
        fields = '__all__'


class KalpaSerializer (serializers.ModelSerializer):
    kalpana = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Kalpa
        fields = '__all__'
        
    def get_kalpana (self, Kalpa):
        try:
            return models.KalpaKalpana.objects.filter(kalpa_id=Kalpa.id,).values_list('kalpana_code', flat=True)
        except:
            return None

class ClinicalPresentationSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.ClinicalPresentation
        fields = '__all__'

class HetuSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Hetu
        fields = '__all__'

class ExaminationSerializer (serializers.ModelSerializer): 
    class Meta:
        model = models.Examination
        fields = '__all__'

class VyadhiSerializer (serializers.ModelSerializer):
    selected_dushya = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Vyadhi
        fields = '__all__'

    def get_selected_dushya (self, Vyadhi):
        try:
            return models.VyadhiDetail.objects.filter(vyadhi_header_id=Vyadhi.id, vyadhiID__code__contains='VY99').count()
        except:
            return 0

class VyadhiDetailSerializer (serializers.ModelSerializer):
    #vyadhi_code_n = serializers.SerializerMethodField(read_only=True)
    vyadhi_description = serializers.ReadOnlyField(source = 'vyadhiID.description')
    vyadhi_code = serializers.ReadOnlyField(source='vyadhiID.code')

    class Meta:
        model = models.VyadhiDetail
        fields = '__all__'
        #depth = 1

class ChikitsaKaalaSerializer (serializers.ModelSerializer):
    bheshaja_kaala_description = serializers.ReadOnlyField(source='bheshaja_kaal_code.description')
    class Meta:
        model = models.ChikitsaKaala
        fields = '__all__'

class ChikitsaSerializer (serializers.ModelSerializer):
    chikitsa_kaala = ChikitsaKaalaSerializer(many=True)
    kalpa_description = serializers.ReadOnlyField(source='kalpa_id.description')
    anupana_description = serializers.ReadOnlyField(source='anupana_id.description')
    kalpana_description = serializers.ReadOnlyField(source='kalpana_code.description')
    class Meta:
        model = models.Chikitsa
        fields = '__all__'

class VisitSerializer (serializers.ModelSerializer):
    class Meta:
        model = models.Visit
        fields = '__all__'