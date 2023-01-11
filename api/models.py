from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class MasterCodeCategory (models.Model):
    category = models.CharField(db_column='category', max_length=32)

    class Meta:
        db_table='MasterCodeCategory'

    def __str__(self):
        return self.category

class MasterCodes (models.Model):
    category_code = models.ForeignKey(MasterCodeCategory, on_delete=models.CASCADE, db_column='CategoryCode',related_name='category_code')
    code = models.CharField(db_column='code', max_length=2, unique=True)
    description = models.CharField(db_column='description', max_length=256)
    is_selectable = models.BooleanField(db_column='IsSelectable', default=1)

    class Meta:
        db_table='MasterCodes'

    def __str__(self):
        return self.description

#standard master codes like Pincodes will have their own models. Also could be loaded along with client side installation.

class Pincodes(models.Model):
    pincode = models.CharField(max_length=6)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    class Meta:        
        db_table = 'Pincodes'

class VyadhiCode (models.Model):
    code = models.CharField(db_column='code',max_length=9)
    language = models.ForeignKey(MasterCodes,to_field='code', null=True,on_delete=models.SET_NULL,db_constraint=False, db_column='LanguageCode', related_name='language_code')
    script = models.ForeignKey(MasterCodes, to_field= 'code', null=True,on_delete=models.SET_NULL,db_constraint=False, db_column='ScriptCode', related_name='script_code')
    description = models.CharField(db_column='description', max_length=256)
    status = models.SmallIntegerField(db_column='status', default=1) #0-non selectable 1-selectable

    class Meta:
        db_table = 'VyadhiCode'

gender = [
    ('M','Male'),
    ('F','Female'),
    ('U','Unknown')
]

class Doctor (models.Model):
    def registration_doc_path(self,filename):
        if not self.pk:
            return 'vaidya/temp/{}'.format(filename)
        else:
            return 'vaidya/{}/registration_doc/{}'.format(self.pk,filename)

    def profile_img_path (self, filename):
        if not self.pk:
            return 'vaidya/temp/{}'.format(filename)
        else:
            return 'vaidya/{}/profile_img/{}'.format(self.pk,filename)

    email = models.EmailField(db_column='email', blank=False, null=False, unique=True, )
    first_name = models.CharField(db_column='FirstName', max_length=64, blank=True)
    last_name = models.CharField(db_column='LastName', max_length=64, blank=True)
    gender = models.CharField(db_column='gender', choices=gender, max_length=1, blank=True) # M/F/U
    dob = models.DateField(db_column='dob', blank=True)
    phone = models.BigIntegerField(db_column='phone',blank=True)
    registration_no = models.CharField(db_column='RegistrationNo', max_length=32, blank=True)
    registration_doc = models.FileField(db_column='RegistrationDoc', upload_to=registration_doc_path)
    verification_status = models.SmallIntegerField(db_column='VerificationStatus', default=0) # 0 - not verified, 1 - verified
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')
    profile_img = models.ImageField(db_column='ProfileImg',blank=True,upload_to=profile_img_path)

    class Meta:
        db_table = 'Doctor'

    def save(self, *args, **kwargs):

        if not self.pk:
            #print (str(self.pk) + ' is the primary key')
            super(Doctor, self).save(*args, **kwargs)#this saves file to /temp dir
            #print (str(self.pk) + ' is the primary key after saving the object')
            #print (self.registration_doc.name)
            #print (self.registration_doc)
            registration_doc = self.registration_doc
            o_path_file = self.registration_doc.name
            p = '{}/registration_doc'.format(self.pk)
            n_path_file = o_path_file.replace('temp',p)
            self.registration_doc.storage.delete(n_path_file)
            self.registration_doc.storage.save(n_path_file,registration_doc)
            self.registration_doc.close()
            self.registration_doc.storage.delete(o_path_file)

            profile_img = self.profile_img
            img_old_file = self.profile_img.name
            i = '{}/profile_img'.format(self.pk)
            img_new_file = img_old_file.replace('temp', i)
            self.profile_img.storage.delete(img_new_file)
            self.profile_img.storage.save(img_new_file,profile_img)
            self.profile_img.close()
            self.profile_img.storage.delete(img_old_file)

            super(Doctor, self).save(*args, **kwargs)

        else:
            #print (self.registration_doc.name + ' is name')
            #print (self.registration_doc)
            super().save(*args, **kwargs)

    def delete (self, *args, **kwargs):
        self.registration_doc.delete() #this will not work when trying bulk delete like books.object.all().delete(). For this need to run loop for each book delete.
        self.profile_img.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.email

class Clinic (models.Model):
    doctor_id = models.ForeignKey(Doctor ,null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='DoctorId')
    name = models.CharField(db_column='name', max_length=256)
    address = models.CharField(db_column='address', max_length=2048)
    pincode = models.IntegerField(db_column='pincode')
    city = models.CharField(db_column='city', max_length=256)
    state = models.CharField(db_column='state', max_length=64)
    phone = models.BigIntegerField(db_column='phone', blank=True)
    status = models.SmallIntegerField(db_column='status', default=0) # 0 - active
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')    

    class Meta:
        db_table = 'DoctorsClinic'

    def __str__(self):
        return self.name

weekdays = [
    (0,'Sun'),
    (1,'Mon'),
    (2,'Tue'),
    (3,'Wed'),
    (4,'Thu'),
    (5,'Fri'),
    (6,'Sat'),    
    ]

class ClinicTimings (models.Model):
    clinic_id = models.ForeignKey(Clinic, null=True, on_delete = models.SET_NULL, db_constraint= False, db_column='ClinicId', related_name='timings')
    weekday = models.SmallIntegerField(db_column='weekday', choices=weekdays, default='1')
    start_time = models.TimeField(db_column='StartTime')
    end_time = models.TimeField(db_column='EndTime')
    status = models.SmallIntegerField(db_column='Status', blank=True, null=True, default= 1) # 0 - inactive
    #modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    #created_date_time = models.DateTimeField(db_column='CreatedDateTime')
    #lets introduce these two fields only if we treat them independant of their parent table in our APIs. If they are treated as linked then parent's modified/created should suffice

    class Meta:
        db_table = 'ClinicTimings'

class Member (models.Model):
    email = models.CharField(db_column='email',max_length=64, blank=False, null=False, unique=True)
    first_name = models.CharField(db_column='FirstName', max_length=64)
    last_name = models.CharField(db_column='LastName', max_length=64)
    gender = models.CharField(db_column='gender', choices=gender, max_length=1)# M/F/U
    dob = models.DateField(db_column='dob')
    phone = models.BigIntegerField(db_column='phone')
    address = models.CharField(db_column='address', max_length=2048)
    pincode = models.IntegerField(db_column='pincode')
    city = models.CharField(db_column='city', max_length=256)
    state = models.CharField(db_column='state', max_length=64)
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')

    class Meta:
        db_table = 'Member'

    def __str__(self):
        return self.email

class DoctorMember (models.Model):
    dr_id = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL,db_constraint=False, db_column='DoctorId', related_name='doctors')
    member_id = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='MemberId', related_name='members')
    status = models.SmallIntegerField(default=1) # 1 - associated 0 - not associated
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')

    class Meta:
        db_table = 'DoctorMember'

class LifeStyleManagement (models.Model):
    member_id = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL, db_constraint=False,db_column='MemberId')
    note = models.CharField(db_column='note',max_length=2048)
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')
    
    class Meta:
        db_table = 'LifeStyleManagement'

class Appointment (models.Model):
    member_id = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='MemberId')
    dr_id = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL,db_constraint=False, db_column='DoctorId')
    clinic_id = models.ForeignKey(Clinic, null=True, on_delete = models.SET_NULL, db_constraint= False, db_column='ClinicId')
    appt_date_time = models.DateTimeField(db_column='ApptDateTime')
    #end_date_time = models.DateTimeField(db_column='EndDateTime')
    reason_code = models.ForeignKey(MasterCodes,null=True,on_delete=models.SET_NULL,db_constraint=False, db_column='ReasonCode', related_name='ReasonCode') #reason is from patient point of view
    note_type = models.ForeignKey(MasterCodes, null=True,on_delete=models.SET_NULL,db_constraint=False,db_column='NoteType', related_name='ApptNoteType')
    note = models.CharField(db_column='note',max_length=2048, blank=True)
    status = models.SmallIntegerField (default=1) # 1 - scheduled
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')

    class Meta:
        db_table = 'Appointment'

class Kalpa (models.Model):
    #identifier = models.IntegerField(db_column='identifier')
    description = models.CharField(db_column='description', max_length=256)
    proprietory = models.BooleanField(db_column='proprietory',default=0)
    anupan = models.BooleanField(db_column='anupan',default=0)
    language = models.ForeignKey(MasterCodes,to_field='code', null=True,on_delete=models.SET_NULL,db_constraint=False, db_column='LanguageCode', related_name='kalpa_language')
    script = models.ForeignKey(MasterCodes, to_field= 'code', null=True,on_delete=models.SET_NULL,db_constraint=False, db_column='ScriptCode', related_name='kalpa_script')

    class Meta:
        db_table = 'Kalpa'

    def __str__(self):
        return self.description

class KalpaKalpana (models.Model):
    kalpa_id = models.ForeignKey(Kalpa, null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='kalpa_id', related_name='kalpa_id')
    kalpana_code = models.ForeignKey(MasterCodes, to_field= 'code', null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='KalpanaCode', related_name='kalpana_code')

    class Meta:
        db_table = 'KalpaKalpana'


class Visit (models.Model):
    #appt_id = models.ForeignKey(Appointment, on_delete=models.CASCADE, db_column='ApptId')
    member_id = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='MemberId')
    dr_id = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL,db_constraint=False, db_column='DoctorId')
    clinic_id = models.ForeignKey(Clinic, null=True, on_delete = models.SET_NULL, db_constraint= False, db_column='ClinicId')
    type_code = models.ForeignKey(MasterCodes,null=True,on_delete=models.SET_NULL,db_constraint=False,db_column='TypeCode',related_name='TypeCode') #visit type is from doctor's point of view
    start_date_time = models.DateTimeField(db_column='StartDateTime')
    end_date_time = models.DateTimeField(db_column='EndDateTime',blank=True, null=True)
    status = models.SmallIntegerField (default=1) #1-Open, 0-Close
    modified_date_time = models.DateTimeField(db_column='ModifiedDateTime')
    created_date_time = models.DateTimeField(db_column='CreatedDateTime')

    class Meta:
        db_table = 'Visit'

class ClinicalPresentation (models.Model):
    visit_id = models.ForeignKey(Visit, on_delete=models.CASCADE, db_column='VisitId', related_name='clinical_presentation')
    note_type = models.ForeignKey(MasterCodes, null=True,on_delete=models.SET_NULL,db_constraint=False,db_column='NoteType', related_name='PresentationNoteType')
    note = models.CharField(db_column='note',max_length=2048, blank=True) 

    class Meta:
        db_table = 'ClinicalPresentation'

class Hetu (models.Model):
    visit_id = models.ForeignKey(Visit, on_delete=models.CASCADE, db_column='VisitId', related_name='hetu')
    note_type = models.ForeignKey(MasterCodes, null=True,on_delete=models.SET_NULL,db_constraint=False,db_column='NoteType', related_name='HetuNoteType')
    note = models.CharField(db_column='note',max_length=2048, blank=True)

    class Meta:
        db_table = 'Hetu'


generic_evaluation_result = (
    (0,'Not Assessed'),
    (1,'Normal'),
    (2,'Abnormal')
)


bala_evaluation_result = (
    (0,'Not Assessed'),
    (1,'Heena'),
    (2,'Madhyam'),
    (3,'Uttam')
)
    

class Examination (models.Model):
    visit_id = models.OneToOneField(Visit, on_delete=models.CASCADE, db_column='VisitId', related_name='examination')
    pulse = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(480)], blank=True, null=True, db_column='pulse')
    systolic_blood_pressure = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(370)], blank=True,null=True,db_column='SystolicBP') #mm of Hg
    diastolic_blood_pressure = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(360)], blank=True,null=True,db_column='DiastolicBP')#mm of Hg
    height = models.DecimalField(validators=[MinValueValidator(50), MaxValueValidator(260)], max_digits=5, decimal_places=2, blank=True,null=True,db_column='height') # in cm
    weight = models.DecimalField(validators=[MinValueValidator(0), MaxValueValidator(635)], max_digits=5, decimal_places=2, blank=True,null=True,db_column='weight') # in kg
    temperature = models.DecimalField(validators=[MinValueValidator(56), MaxValueValidator(115)],  max_digits=5, decimal_places=2, blank=True,null=True,db_column='temperature')#in Fahrenheit
    naadi = models.SmallIntegerField(choices=generic_evaluation_result, default=0,blank=True,null=True,db_column='naadi')#0-not assessed, 1-normal, 2-abnormal
    jeevha = models.SmallIntegerField(choices=generic_evaluation_result, default=0,blank=True,null=True,db_column='jeevha')#0-not assessed, 1-normal, 2-abnormal
    mala = models.SmallIntegerField(choices=generic_evaluation_result, default=0,blank=True,null=True,db_column='mala')#0-not assessed, 1-normal, 2-abnormal
    mutra = models.SmallIntegerField(choices=generic_evaluation_result, default=0,blank=True,null=True,db_column='mutra')#0-not assessed, 1-normal, 2-abnormal
    sveda = models.SmallIntegerField(choices=generic_evaluation_result, default=0,blank=True,null=True,db_column='sveda')#0-not assessed, 1-normal, 2-abnormal
    menstrual_cycle = models.SmallIntegerField(choices=generic_evaluation_result, default=0,blank=True,null=True,db_column='MenstrualCycle')#0-not assessed, 1-no menarche, 2-normal, 3-abnormal, 4-menopause
    sharir_bala = models.SmallIntegerField(choices=bala_evaluation_result, default=0,blank=True,null=True,db_column='SharirBala')#0-not assessed, 1-heen, 2-madhya, 3-uttam
    satva = models.SmallIntegerField(choices=bala_evaluation_result, default=0,blank=True,null=True,db_column='satva')#0-not assessed, 1-heen, 2-madhya, 3-uttam

    class Meta:
        db_table = 'Examination'



class Vyadhi (models.Model):
    visit_id = models.ForeignKey(Visit, on_delete=models.CASCADE, db_column='VisitId', related_name='vyadhi')
    pradhan_dosha = models.PositiveSmallIntegerField(db_column='PradhanDosha')#1-vaat, 2-pitta, 3-kapha. cannot be none
    anubandha_dosha_1 = models.PositiveSmallIntegerField(db_column='AnubandhaDosha1', default=0)#1-vaat, 2-pitta, 3-kapha, 0-none
    anubandha_dosha_2 = models.PositiveSmallIntegerField(db_column='AnubandhaDosha2', default=0)#1-vaat, 2-pitta, 3-kapha, 0-none
    
    class Meta:
        db_table = 'Vyadhi'    

class VyadhiDetail (models.Model):
    vyadhi_header_id = models.ForeignKey(Vyadhi, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='VyadhiHeaderId', related_name='vyadhi_detail')
    vyadhiID = models.ForeignKey(VyadhiCode, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='VyadhiId', related_name='vyadhi_id')
    #vyadhi_code = models.CharField(db_column='VyadhiCode',max_length=9)
    class Meta:
        db_table = 'VyadhiDetail'

class Chikitsa (models.Model):
    #appt_id = models.ForeignKey(Appointment, on_delete=models.CASCADE, db_column='AppointmentId')
    member_id = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='MemberId')
    dr_id = models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL,db_constraint=False, db_column='DoctorId')
    clinic_id = models.ForeignKey(Clinic, null=True, on_delete = models.SET_NULL, db_constraint= False, db_column='ClinicId')
    kalpa_id = models.ForeignKey(Kalpa, null=True,on_delete=models.SET_NULL,db_constraint=False,db_column='KalpaId',related_name='chikitsa_kalpa_id')
    kalpana_code = models.ForeignKey(MasterCodes, to_field='code', null=True,on_delete=models.SET_NULL,db_constraint=False,db_column='KalpanaCode')
    unit_tab_wt = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, db_column='UnitTabWt')
    unit_tab_unit = models.ForeignKey(MasterCodes, to_field='code', null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='UnitTabUnit', related_name='tab_unit')
    kalpa_dose = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, db_column='KalpaDose')
    kalpa_unit = models.ForeignKey(MasterCodes, to_field='code', null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='KalpaUnit', related_name='kalpa_unit')
    anupana_id = models.ForeignKey(Kalpa, null=True, on_delete=models.SET_NULL,db_constraint=False,db_column='AnupanaId',related_name='anupana_id')
    anupana_dose = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, db_column='AnupanaDose')
    anupana_unit = models.ForeignKey(MasterCodes, to_field='code', null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='AnupanaUnit', related_name='anupana_unit')
    duration = models.PositiveIntegerField(db_column='Duration')
    start_date = models.DateField(db_column='StartDate')
    end_date = models.DateField(db_column='EndDate')
    class Meta:
        db_table = 'Chikitsa'

class ChikitsaKaala (models.Model):
    chikitsa_id = models.ForeignKey(Chikitsa, blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False,db_column='ChikitsaId', related_name='chikitsa_kaala')
    bheshaja_kaal_code = models.ForeignKey(MasterCodes, to_field='code', blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False, db_column='BheshajaKaalaCode')
    class Meta:
        db_table = 'ChikitsaKaala'