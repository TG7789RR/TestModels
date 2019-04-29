# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 14:28:33 2019

@author: Thurstan.Green
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


pd.set_option('display.max_columns', 15) ##set number of cols you wnat to display
pd.options.display.max_rows = 100


wd = 'Z:\Thurstan/190423 car accidents/'


accin = pd.read_csv(wd + 'Accident_Information.csv'
                     ,sep=','
                     ,parse_dates=['Date']
                     )


acc = accin.copy()

'''
acc[0:5].T
acc.columns
'''
acc.drop(['1st_Road_Number'
                          ,'2nd_Road_Number'
                          ,'Location_Easting_OSGR'
                          ,'Location_Northing_OSGR'
                          ,'Latitude'
                          ,'Local_Authority_(District)'
                          ,'Local_Authority_(Highway)'
                          ,'Longitude'
                          ,'Police_Force'
                          ,'InScotland'
                          ,'LSOA_of_Accident_Location'], axis=1, inplace=True)


#acc.groupby(['Accident_Severity']).size()


#--------------------------------------------------------------------------reband is fatal
def istarget(x):
    if x == 'Fatal':
        return 1
    else:
        return 0
    
        
acc['T_isfatal'] = acc['Accident_Severity'].apply(istarget)
acc['month'] = pd.DatetimeIndex(acc['Date']).month  
acc['hour'] = acc['Time'].str[0:2] 


acc.drop(['Date','Time'], axis = 1, inplace = True)
#acc.groupby(['Accident_Severity','T_isfatal']).size()
#acc.groupby(['T_isfatal']).size()
#acc.groupby(['T_isfatal']).size()
#acc[acc['T_isfatal']==1]['T_isfatal'].size / acc[acc['T_isfatal']==0]['T_isfatal'].size



def isfatalsevere(x):
    if x == 'Fatal':
        return 1
    if x == 'Serious':
        return 1
    else:
        return 0

acc['T_fatal_or_serious'] = acc['Accident_Severity'].apply(isfatalsevere)

#acc.groupby(['Accident_Severity','T_fatal_or_serious']).size()

acc.drop(['Accident_Severity'], axis = 1, inplace = True)


#acc.groupby(['T_isfatal','T_fatal_or_serious']).size()

#----------------------------------------------------------------------------- reband num vechiles

def numvech(x):
    if x <= 3:
        return str(x)
    else:
        return '4+'
    
acc['NumberVech'] = acc['Number_of_Vehicles'].apply(numvech)


#acc.groupby(['NumberVech','Number_of_Vehicles']).size()

acc.drop(['Number_of_Vehicles'], axis = 1, inplace = True)

#---------------------------------------------------------------------------others 

#acc.groupby(['1st_Road_Class']).size()
#acc.groupby(['2nd_Road_Class']).size()

acc['2nd_Road_Class'] = acc['2nd_Road_Class'].fillna('None')


acc.rename(columns={'Did_Police_Officer_Attend_Scene_of_Accident':'Police'}, inplace=True)


acc.drop(['Pedestrian_Crossing-Human_Control','Pedestrian_Crossing-Physical_Facilities'], axis = 1, inplace = True)

#acc.groupby(['Junction_Control']).size() #ok
#acc.groupby(['Junction_Detail']).size() #ok


#acc.groupby(['Carriageway_Hazards']).size() #going to drop for moment
acc.drop(['Carriageway_Hazards'], axis = 1, inplace = True)


#acc.groupby(['Special_Conditions_at_Site']).size() #going to drop for moment


#----------------------------------------------------------------------------reband number vech

#acc.groupby(['Number_of_Casualties']).size() #going to band like vehciles

acc['NumberCasualties'] = acc['Number_of_Casualties'].apply(numvech)

#acc.groupby(['NumberCasualties','Number_of_Casualties']).size()
acc.drop(['Number_of_Casualties'], axis = 1, inplace = True)



acc[0:5].T
acc.columns

#-----------------------------------------------------------------------out to csv
'''
acc.to_csv(wd+'acc_Rin.csv', columns=[ '1st_Road_Class', '2nd_Road_Class', 'Day_of_Week',
       'Police', 'Junction_Control', 'Junction_Detail', 'Light_Conditions',
       'Road_Surface_Conditions', 'Road_Type', 'Special_Conditions_at_Site',
       'Speed_limit', 'Urban_or_Rural_Area', 'Weather_Conditions', 'Year',
       'T_isfatal', 'month', 'hour', 'T_fatal_or_serious', 'NumberVech',
       'NumberCasualties'])
'''
acc.to_csv(wd+'acc_Rin.csv')

    
#------------------------------------------------------------------------------some random variables 
    


p1 = pd.pivot_table(data=acc
               ,values = ['Accident_Index']
               ,index = ['Year']
               ,columns = ['T_isfatal']
               ,aggfunc=np.count_nonzero
               )

p1.columns = p1.columns.droplevel(0)
collist = list(p1.columns.values)
p1['total'] = 0


for x in collist:
    p1['total'] = p1['total'] + p1[x]   


for x in collist:
    p1[str(x)] = round(p1[x]/p1['total'],3)

p1






acc.groupby(['T_isfatal','T_fatal_or_serious']).size()

acc.groupby(['T_isfatal','T_fatal_or_serious']).size()











