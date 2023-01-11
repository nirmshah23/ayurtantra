##from os import set_inheritable
from django.shortcuts import render
from api import models, serializers
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, APIException
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.storage import FileSystemStorage
from .functions import get_slots

# Create your views here.

@api_view(['GET'])
def appt_slots(request):
    
    if request.method == 'GET':
        clinic_id = request.query_params.get('clinic_id')
        dt = request.query_params.get('date')
        slots = get_slots(clinic_id=clinic_id,dt=dt)
        #print (slots)
        #data = json.dumps(slots)
        #print (data)
    return Response(slots, status=status.HTTP_200_OK)

def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        #print (uploaded_file.name)
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
    return render (request, 'upload.html')

class MasterCodeCategoryList (generics.ListCreateAPIView):
    #permission_classes = [permissions.AllowAny]
    queryset = models.MasterCodeCategory.objects.all()
    serializer_class = serializers.MasterCodeCategorySerializer

class MasterCodeCategoryDetail (generics.RetrieveUpdateAPIView):
    #permission_classes = [permissions.AllowAny]
    queryset = models.MasterCodeCategory.objects.all()
    serializer_class = serializers.MasterCodeCategorySerializer

class  MasterCodesList (generics.ListCreateAPIView):
    #permission_classes = [permissions.AllowAny]
    queryset = models.MasterCodes.objects.all()
    serializer_class = serializers.MasterCodesSerializer

    def get_queryset(self):
        cc = self.request.query_params.getlist('cc')
        print (cc)
        if len(cc) != 0:
            queryset = models.MasterCodes.objects.filter(is_selectable=1,category_code__pk__in = cc)
            if queryset.exists():
                return queryset
            else:
                raise NotFound('No master code(s) found')
        else:
            raise APIException(detail='cc query parameter is required')

class MasterCodesDetail (generics.RetrieveUpdateAPIView):
    #permission_classes = [permissions.AllowAny]
    queryset = models.MasterCodes.objects.all()
    serializer_class = serializers.MasterCodesSerializer

class VyadhiCodeList (generics.ListCreateAPIView):
    queryset = models.VyadhiCode.objects.all()
    serializer_class = serializers.VyadhiCodeSerializer

    def get_queryset(self):
        language = self.request.query_params.get('language')
        script = self.request.query_params.get('script')
        code_like = self.request.query_params.get('code_like',None)
        code_not_like = self.request.query_params.get('code_not_like',None)
        description = self.request.query_params.get('description',None)

        if language is None or script is None:
            raise APIException(detail='both language and script query parameter are required')
        else:
            queryset = models.VyadhiCode.objects.filter(language=language, script=script, status=1)

        if code_like:
            queryset = queryset.filter(code__contains=code_like,)
        if code_not_like:
            queryset = queryset.exclude(code__contains=code_not_like)
        if description:
            queryset = queryset.filter(description__contains=description)

        return queryset

class VyadhiCodeDetail (generics.RetrieveUpdateAPIView):
    queryset = models.VyadhiCode.objects.all()
    serializer_class = serializers.VyadhiCodeSerializer

class DoctorList (generics.ListCreateAPIView):
    queryset = models.Doctor.objects.all()
    serializer_class = serializers.DoctorSerializer

class DoctorDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Doctor.objects.all()
    serializer_class = serializers.DoctorSerializer

class ClinicList (generics.ListCreateAPIView):
    queryset = models.Clinic.objects.all()
    serializer_class = serializers.ClinicSerializer

class ClinicDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Clinic.objects.all()
    serializer_class = serializers.ClinicSerializer

class DoctorsClinicsList (generics.ListAPIView):
    serializer_class = serializers.ClinicSerializer

    def get_queryset (self):
        drID = self.request.query_params.get('drID')
        if drID is not None: 
            queryset = models.Clinic.objects.filter(doctor_id=drID)
            #print (queryset.exists())
            if queryset.exists():
                #print (queryset)
                #print ('returning queryset')
                return queryset
            else:
                #print ('returning error')
                raise NotFound('No Facility Found')
        else:
            #print ('drid is none')
            raise APIException(detail='drID query parameter is required')
            #return Response('drID query parameter is required', status=status.HTTP_400_BAD_REQUEST)

class Facility (generics.ListCreateAPIView):
    queryset = models.Clinic.objects.all()
    serializer_class = serializers.FacilitySerializer
    
    def get_queryset (self):
        drID = self.request.query_params.get('drID')
        if drID is not None: 
            queryset = models.Clinic.objects.filter(doctor_id=drID)
            if queryset.exists():
                return queryset
            else:
                raise NotFound('No Facility Found')
        else:
            raise APIException(detail='drID query parameter is required')

class UpdateFacility (generics.UpdateAPIView):
    queryset = models.Clinic.objects.all()
    serializer_class = serializers.FacilitySerializer
    
    def patch(self, request, *args, **kwargs):
        print (request.body)
        print ('above is request body')
        return super().patch(request, *args, **kwargs)


class ClinicTimingsList (generics.ListCreateAPIView):
    queryset = models.ClinicTimings.objects.all()
    serializer_class = serializers.ClinicTimingsSerializer

class ClinicTimingsDetail (generics.RetrieveUpdateAPIView):
    queryset = models.ClinicTimings.objects.all()
    serializer_class = serializers.ClinicTimingsSerializer

class MemberList (generics.ListCreateAPIView):
    queryset = models.Member.objects.all()
    serializer_class = serializers.MemberSerializer

    def get_queryset(self):
        drID = self.request.query_params.get('drID')

        if drID is not None:
            queryset = models.Member.objects.filter(members__dr_id = drID) #members is the related field name of the foreign key field of doctormember model
            return queryset
        else:
            raise APIException('drID query parameter is required')
        #return super().get_queryset()

class MemberDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Member.objects.all()
    serializer_class = serializers.MemberSerializer

class DoctorMemberList (generics.ListAPIView):
    queryset = models.DoctorMember.objects.all()
    serializer_class = serializers.DoctorMemberViewSerializer

    def get_queryset(self):
        drID = self.request.query_params.get('drID')
        memberID = self.request.query_params.get('memberID')

        if drID is None and memberID is None:
            raise APIException(detail='Either drID or memberID query parameter is required')
        else:
            if drID is not None:
                queryset = models.DoctorMember.objects.filter(dr_id = drID)
                if queryset.exists():
                    return queryset
                else:
                    raise NotFound('No members found')

class DoctorMemberCreate (generics.CreateAPIView):
    queryset = models.DoctorMember.objects.all()
    serializer_class = serializers.DoctorMemberCreateSerializer

class DoctorMemberDetail (generics.RetrieveUpdateAPIView):
    queryset = models.DoctorMember.objects.all()
    serializer_class = serializers.DoctorMemberViewSerializer

class LifeStyleManagementList (generics.ListCreateAPIView):
    queryset = models.LifeStyleManagement.objects.all()
    serializer_class = serializers.LifeStyleManagementSerializer

class LifeStyleManagementDetail (generics.RetrieveUpdateAPIView):
    queryset = models.LifeStyleManagement.objects.all()
    serializer_class = serializers.LifeStyleManagementSerializer

class AppointmentList (generics.ListCreateAPIView):
    queryset = models.Appointment.objects.all()
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        appt_date = self.request.query_params.get('appt_date', None)
        dr_id = self.request.query_params.get('dr_id', None)

        if dr_id is None or appt_date is None:
            raise APIException(detail='both dr_id and appt_date query parameter are required')
        else:
            return models.Appointment.objects.filter(dr_id=dr_id, appt_date_time__date = appt_date)

class AppointmentDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Appointment.objects.all()
    serializer_class = serializers.AppointmentSerializer

class KalpaList (generics.ListCreateAPIView):
    queryset = models.Kalpa.objects.all()
    serializer_class = serializers.KalpaSerializer

    def get_queryset(self):
        description = self.request.query_params.get('description')
        language = self.request.query_params.get('language')
        script = self.request.query_params.get('script')

        if description is None or language is None or script is None:
            raise APIException(detail='description, language and script query parameters are required')
        else:
            queryset = models.Kalpa.objects.filter(description__contains=description, language=language, script=script)
            return queryset

class KalpaDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Kalpa.objects.all()
    serializer_class = serializers.KalpaSerializer

class KalpaKalpanaList (generics.ListCreateAPIView):
    queryset = models.KalpaKalpana.objects.all()
    serializer_class = serializers.KalpaKalpanaSerializer

class VisitList (generics.ListCreateAPIView):
    queryset = models.Visit.objects.all()
    serializer_class = serializers.VisitSerializer

class VisitDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Visit.objects.all()
    serializer_class = serializers.VisitSerializer

class ClinicalPresentationList (generics.ListCreateAPIView):
    queryset = models.ClinicalPresentation.objects.all()
    serializer_class = serializers.ClinicalPresentationSerializer

    def get_queryset(self):
        visit_id = self.request.query_params.get('visit_id')

        if visit_id is None:
            raise APIException(detail='visit_id query parameter is required')
        else:
            queryset = models.ClinicalPresentation.objects.filter(visit_id=visit_id)
            return queryset

class ClinicalPresentationDetail (generics.RetrieveUpdateAPIView):
    queryset = models.ClinicalPresentation.objects.all()
    serializer_class = serializers.ClinicalPresentationSerializer

class HetuList (generics.ListCreateAPIView):
    queryset = models.Hetu.objects.all()
    serializer_class = serializers.HetuSerializer

    def get_queryset(self):
        visit_id = self.request.query_params.get('visit_id')

        if visit_id is None:
            raise APIException(detail='visit_id query parameter is required')
        else:
            return models.Hetu.objects.filter(visit_id=visit_id)


class HetuDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Hetu.objects.all()
    serializer_class = serializers.HetuSerializer 

class ExaminationList (generics.ListCreateAPIView):
    queryset = models.Examination.objects.all()
    serializer_class = serializers.ExaminationSerializer

    def get_queryset(self):
        visit_id = self.request.query_params.get('visit_id')

        if visit_id is None:
            raise APIException(detail='visit_id query parameter is required')
        else:
            queryset = models.Examination.objects.filter(visit_id=visit_id)
            return queryset

class ExaminationDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Examination.objects.all()
    serializer_class = serializers.ExaminationSerializer

class VyadhiHeaderList (generics.ListCreateAPIView):
    queryset = models.Vyadhi.objects.all()
    serializer_class = serializers.VyadhiSerializer

    def get_queryset(self):
        visit_id = self.request.query_params.get('visit_id')

        if visit_id is None:
            raise APIException(detail='visit_id query parameter is required')
        else:
            queryset = models.Vyadhi.objects.filter(visit_id=visit_id)
            return queryset

class VyadhiHeaderDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Vyadhi.objects.all()
    serializer_class = serializers.VyadhiSerializer

class VyadhiLineList (generics.ListCreateAPIView):
    queryset = models.VyadhiDetail.objects.all()
    serializer_class = serializers.VyadhiDetailSerializer

    def get_queryset(self):
        vyadhi_header_id = self.request.query_params.get('vyadhi_header_id')

        if vyadhi_header_id is None:
            raise APIException(detail='vyadhi_header_id query parameter is required')
        else:
            queryset = models.VyadhiDetail.objects.filter(vyadhi_header_id=vyadhi_header_id)
            return queryset

class VyadhiLineDetail (generics.RetrieveUpdateDestroyAPIView):
    queryset = models.VyadhiDetail.objects.all()
    serializer_class = serializers.VyadhiDetailSerializer

class ChikitsaList (generics.ListCreateAPIView):
    queryset = models.Chikitsa.objects.all()
    serializer_class = serializers.ChikitsaSerializer

    def get_queryset(self):
        member_id = self.request.query_params.get('memberId', None)
        dr_id = self.request.query_params.get('dr_id', None)

        if dr_id is None or member_id is None:
            raise APIException (detail='both dr_id and memberId query parameter are required')
        else:
            return models.Chikitsa.objects.filter(dr_id=dr_id, member_id=member_id)

class ChikitsaDetail (generics.RetrieveUpdateAPIView):
    queryset = models.Chikitsa.objects.all()
    serializer_class = serializers.ChikitsaSerializer

class ChikitsaKaalaList (generics.ListCreateAPIView):
    queryset = models.ChikitsaKaala.objects.all()
    serializer_class = serializers.ChikitsaKaalaSerializer

class PincodeList (generics.ListAPIView):
    #code = request.query_params.get('code')
    #queryset = Pincodes.objects.filter(pincode=code)
    serializer_class = serializers.PincodeSerializer

    def get_queryset (self):
        code = self.request.query_params.get('code')
        if code is None:
            raise APIException(detail='code query parameter is required')
        else:
            return models.Pincodes.objects.filter(pincode__startswith=code)