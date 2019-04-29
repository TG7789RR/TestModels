# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 08:27:29 2019

@author: Thurstan.Green
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
pd.set_option('display.max_columns', 15) ##set number of cols you wnat to display
pd.options.display.max_rows = 100


wd = 'Z:/Thurstan/190416F1casestudy/'





#-------------------------------------------------------------load races
races = pd.read_csv(wd + 'f1db_csv/races.csv'
                     ,sep=','
                     ,parse_dates=['date']
                     )

#races[0:6].T
#races.columns
#races.groupby(['year'])
races.set_index('raceId',inplace=True)
'''
a= races.groupby(['year']).agg({'raceId': [pd.Series.nunique, np.count_nonzero]})
a.columns = a.columns.droplevel(0)
a[a['nunique']!=a['count_nonzero']]
del a
'''


#-------------------------------------------------------------load results 

results = pd.read_csv(wd + 'f1db_csv/results.csv'
                     ,sep=',')

#results[0:7].T
a= results.groupby(['raceId']).agg({'driverId': [pd.Series.nunique, np.count_nonzero], 'resultId':np.min})
a.columns = a.columns.droplevel(0)
b = list(a[a['nunique']!=a['count_nonzero']]['amin'])

results.drop(results[results['resultId'].isin(b)].index,inplace=True) #drop 30 rows 

results.set_index('raceId',inplace=True)

'''
a[a['nunique']!=a['count_nonzero']] #there are a small number of duplicate 
results.shape
results[results['raceId']==839].sort_values(by='driverId',ascending=False)
a.loc[838:839,:]
'''


#------------------------------------------------------------create base table 1 

BT1 = results.merge(races[['round','year','circuitId', 'name', 'date']],on='raceId')

'''
BT1.shape 24217
results.shape #all good
BT1[0:3].T
'''


#-------------------------------------------------------------if required add status to results


#---------------------------------------------------------------add driver names 

drivers  = pd.read_csv(wd + 'f1db_csv/driver.csv'
                     ,sep=','
                     ,parse_dates=['dob'])

drivers.set_index('driverId',inplace=True)
BT1 = BT1.reset_index().set_index('driverId')


#drivers[0:3].T

BT2 = BT1.merge(drivers[['driverRef','dob']]
               ,how='inner'
               ,on='driverId')

#BT2.shape 24217
#BT2[0:3].T

BT2 = BT2.reset_index().set_index(['raceId','driverId'])


#--------------------------------------------------------------add driver standings
driver_stand = pd.read_csv(wd + 'f1db_csv/driver_standings.csv'
                     ,sep=',')

driver_stand.set_index(['raceId','driverId'],inplace=True)

#driver_stand.columns

driver_stand.rename(columns={'points':'champ_points','position':'champ_position'},inplace=True)

#driver_stand[0:3]

BT3 = BT2.merge(driver_stand[['champ_points','champ_position','wins']]
                ,how='left'
                ,on=['raceId','driverId'])

#BT3.shape
#BT3[700:705].T

#-------------------------------------------------------------find the final round
mround = pd.DataFrame(BT3.groupby('year')['round'].max())
mround.rename(columns={'round':'num_rounds'},inplace=True)

BT3 = BT3.reset_index()

BT4 = BT3.merge(mround
                ,how='inner'
                ,on=['year'])

#BT4.shape #24217
#BT4[6763:6769].T


#-------------------------------------------------------------flag the winner 

winner = BT4[['driverId','year']][(BT4['round']==BT4['num_rounds']) & (BT4['champ_position']==1)]

#winner.sort_values(by='year',ascending=False)

winner['ischampwinner'] = 'Yes'

BT5 = BT4.merge(winner
                ,how= 'left'
                ,on=['driverId','year'])

#BT5.shape 24226 small number of dups have appeared 
#BT5.T

BT5['ischampwinner'] = BT5['ischampwinner'].fillna('No')
#BT5.groupby(['year','ischampwinner']).size()

BT5[BT5['year']>=2000].T


BT5[BT5['fastestLap']!=r'''\N''']['year'].min() #2004 first year 

        

BT5.groupby(['fastestLap','year']).size()


#-------------------------------------------------------------how many races to win championship and which is first race

#BT5[(BT5['ischampwinner']=='Yes') & (BT5['year']==2018) ].T


firstwin = (BT5[(BT5['ischampwinner']=='Yes') & (BT5['position']=='1') ]
                .groupby('year')
                .agg({'round':np.min}))

firstwin.rename(columns={'round':'First Win'},inplace=True)

##
firstpod = (BT5[(BT5['ischampwinner']=='Yes') & (BT5['position'].isin(['1','2','3']))]
                .groupby('year')
                .agg({'round':np.min}))
firstpod.rename(columns={'round':'First Podium'},inplace=True)

##
numwins =(BT5[(BT5['ischampwinner']=='Yes')]
            .groupby('year')
            .agg({'wins':np.max
                  ,'num_rounds':np.max}))

numwins['% Won']= round(numwins['wins'] / numwins['num_rounds'],2)


##
numwinners = (BT5[(BT5['position']=='1') ]
                .groupby('year')
                .agg({'driverId':pd.Series.nunique}))

numwinners.rename(columns={'driverId':'Number of Winners'},inplace=True)
##

numwinnersF5 = (BT5[(BT5['position']=='1') & (BT5['round'].isin(['1','2','3','4','5']))]
                .groupby('year')
                .agg({'driverId':pd.Series.nunique}))

numwinnersF5.rename(columns={'driverId':'Race 5 Winners'},inplace=True)

numwinnersF10 = (BT5[(BT5['position']=='1') & (BT5['round'].isin(['1','2','3','4','5','6','7','8','9','10']))]
                .groupby('year')
                .agg({'driverId':pd.Series.nunique}))

numwinnersF10.rename(columns={'driverId':'Race 10 Winners'},inplace=True)





winout = numwins.merge(firstwin
                       ,how='inner'
                       ,on=['year'])

winout = winout.merge(firstpod
                       ,how='inner'
                       ,on=['year'])


winout = winout.merge(numwinners
                       ,how='inner'
                       ,on=['year'])

winout = winout.merge(numwinnersF5
                       ,how='inner'
                       ,on=['year'])


winout = winout.merge(numwinnersF10
                       ,how='inner'
                       ,on=['year'])

#----------------------------------------------------------------------------chart for first winner
b1= winout.loc[1990:2018,'% Won':'% Won']
b2= winout.loc[1990:2018,'First Win':'First Win']

i1 = list(b1.index)
lbl = list(map(str, i1)) #conver the ints to str to stop them plotting missing values
fig, ax1 = plt.subplots()

ax1 = b1.plot.bar(color=['gold'],legend=False, figsize=(10,5))
#ax1.legend(bbox_to_anchor=(1.5,1), edgecolor = 'white')
yval = ax1.get_yticks()
ax1.set_yticklabels(['{:,.0%}'.format(x) for x in yval])
plt.ylabel('% Won (bar)')
plt.xlabel('F1 Season',weight='bold')           

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(lbl, b2,color = 'red')

ax2.set_ylim([0,5])
#ax2.set_yticklabels([0,1,2,3,4],minor=False)
plt.ylabel('First Win (line)')


plt.title('% of Races Won by Champion with First Win',weight='bold',  fontsize=10)
plt.show()

b1.mean() #avearge win rate 
b2.groupby('First Win').size()
b2.shape


#----------------------------------------------------------------------------chart for first podium
b1= winout.loc[1990:2018,'% Won':'% Won']
b2= winout.loc[1990:2018,'First Podium':'First Podium']

i1 = list(b1.index)
lbl = list(map(str, i1)) #conver the ints to str to stop them plotting missing values
fig, ax1 = plt.subplots()

ax1 = b1.plot.bar(color=['gold'],legend=False, figsize=(10,5))

yval = ax1.get_yticks()
ax1.set_yticklabels(['{:,.0%}'.format(x) for x in yval])
plt.ylabel('% Won (bar)')
plt.xlabel('F1 Season',weight='bold')           

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(lbl, b2,color = 'blue')

ax2.set_ylim([0,6])
plt.ylabel('First Podium (line)')


plt.title('% of Races Won by Champion with First Podium',weight='bold',  fontsize=10)
plt.show()



b2.groupby('First Podium').size()




#----------------------------------------------------------------------------what % of winners have won 
ww = winout.loc[1990:2018,'Number of Winners':'Race 10 Winners']

ww = ww[['Race 5 Winners','Race 10 Winners','Number of Winners']]

#redo data for a stacked bar instead
ww['Race 10 Winners'] = ww['Race 10 Winners'] - ww['Race 5 Winners'] 
ww['Number of Winners'] = ww['Number of Winners'] - (ww['Race 5 Winners'] + ww['Race 10 Winners'])

ww.rename(columns={'Number of Winners':'Final Number of Winners'},inplace=True)


ww.plot.bar(stacked=True
            ,color = ['lightblue','cornflowerblue','darkblue']
            , figsize=(10,5))

plt.ylabel('Number of unique winners')
plt.xlabel('F1 Season',weight='bold')   
plt.legend(bbox_to_anchor=(1,1), edgecolor = 'white')
plt.title('How Many Drivers Win and When',weight='bold',  fontsize=10)


ww.groupby('Final Number of Winners').size()
ww.groupby('Race 10 Winners').size()


ww.shape





#----------------------------------------------------------------------------how many people win a race in a season


b1= winout.loc[1990:2018,'% Won':'% Won']
b2= winout.loc[1990:2018,'Number of Winners':'F10 Winners']

i1 = list(b1.index)
lbl = list(map(str, i1)) #conver the ints to str to stop them plotting missing values
fig, ax1 = plt.subplots()

ax1 = b1.plot.bar(color=['gold'],legend=False, figsize=(10,5))

yval = ax1.get_yticks()
ax1.set_yticklabels(['{:,.0%}'.format(x) for x in yval])
plt.ylabel('% Won (bar)')
plt.xlabel('F1 Season',weight='bold')           

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(lbl, b2)

ax2.set_ylim([0,9])
plt.ylabel('# of drivers (line)')

plt.legend(bbox_to_anchor=(1,1), edgecolor = 'white')
plt.title('% of Races Won by Champion with # of Drivers who Won',weight='bold',  fontsize=10)
plt.show()


b2.mean()



#------------------------------------------------------------------------------------most dominante driver

#BT5[0:5].T

driver =(BT5[(BT5['ischampwinner']=='Yes') & (BT5['year']>=1990) & (BT5['year']<2019)]
            .groupby('driverRef')
            .agg({'year':pd.Series.nunique
                  ,'num_rounds':np.count_nonzero}))

driver.rename(columns={'year':'Championships', 
                   'num_rounds':'Championship Rounds'},inplace=True)



d1 =(BT5[(BT5['ischampwinner']=='Yes') & (BT5['year']>=1990) & (BT5['year']<2019) & (BT5['position']=='1')]
            .groupby('driverRef')
            .agg({'position':np.count_nonzero}))

d1.rename(columns={'position':'Championship Wins'},inplace=True)


driver = driver.merge(d1,on=['driverRef'])


driver['% Won']= round(driver['Championship Wins'] / driver['Championship Rounds'],2)

driver.sort_values(by='Championships',inplace=True, ascending=False)



b1= driver.loc[:,'% Won':'% Won']
b2= driver.loc[:,'Championships':'Championships']

i1 = list(b1.index)
lbl = list(map(str, i1)) #conver the ints to str to stop them plotting missing values
fig, ax1 = plt.subplots()

ax1 = b1.plot.bar(color=['lightgreen'],legend=False, figsize=(10,5))

yval = ax1.get_yticks()
ax1.set_yticklabels(['{:,.0%}'.format(x) for x in yval])
plt.ylabel('% Races Won (bar)')
plt.xlabel('F1 Season',weight='bold')           

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(lbl, b2)

ax2.set_ylim([0,8])
plt.ylabel('# of Championships (line)')

plt.legend(bbox_to_anchor=(1,1), edgecolor = 'white')
plt.title('In Years Champions Won How Dominant Were They',weight='bold',  fontsize=10)
plt.show()
























