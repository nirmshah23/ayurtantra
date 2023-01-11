import pandas as pd
import datetime as d
from rest_framework.exceptions import NotFound

from rest_framework import status
from .models import ClinicTimings, Appointment

def get_slots(clinic_id, dt):
    apptDate = d.datetime.strptime(dt, '%Y-%m-%d').date()

    weekday = apptDate.isoweekday()
    weekday = 0 if weekday == 7 else weekday

    #clinic_id = 1
    #weekday = 1

    df = pd.DataFrame(columns=['StartTime','EndTime'])

    clinic_timings = ClinicTimings.objects.filter(clinic_id = clinic_id, weekday=weekday, status=1).values_list('start_time','end_time')
    print (clinic_timings)
    if clinic_timings.exists():

        for r in clinic_timings:
            st = d.datetime.combine(apptDate,r[0])
            et = d.datetime.combine(apptDate,r[1]) - d.timedelta(hours=0,minutes=30)
            start_time = pd.date_range(st,et,freq='30T')

            st = st + d.timedelta(hours=0,minutes=30)
            et = et + d.timedelta(hours=0,minutes=30)
            end_time = pd.date_range(st,et,freq='30T')

            y = {'StartTime': start_time, 'EndTime': end_time}

            df = df.append(pd.DataFrame(y), ignore_index=True)
        
    df['Available'] = True
    
    existing_appts = Appointment.objects.filter(clinic_id=clinic_id, appt_date_time__date = apptDate).values_list('appt_date_time')
    print (existing_appts)

    if existing_appts.exists():

        for appt in existing_appts:
            apptNaive = appt[0].replace(tzinfo=None)
            #print (apptNaive)
            df['Available'] = df.apply(lambda x: not(x['StartTime'] <= apptNaive < x['EndTime']) if x['Available'] == True else x['Available'], axis=1)

    if not df.empty:
        print (type(df['StartTime'][0]))
        df['StartTime'] = pd.to_datetime(df['StartTime'])
        appt_dict = dict(zip(df['StartTime'].dt.strftime('%Y-%m-%d %H:%M:%S').apply(lambda x: x.split()[1]),df['Available']))
    else:
        appt_dict = {}

    return appt_dict