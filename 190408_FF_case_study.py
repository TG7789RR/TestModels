"""
@author: Thurstan.Green
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
pd.set_option('display.max_columns', 15) ##set number of cols you wnat to display
pd.options.display.max_rows = 100


wd = 'Z:/Thurstan/190408 Farfetch Case Study/'

FFin = pd.read_csv(wd + 'FarfetchPPC.csv'
                     ,sep=','
                     )
#FFin.shape -- 33960

#----------------------------------------------------------------------------data cleaning


#remove any multi linked keywords to ad groups
kw = pd.DataFrame(FFin.groupby(['Search keyword'])['Ad group'].nunique())

#kw.groupby('Ad group').size() #limited volume of dups
vals = kw[kw['Ad group']>1].index.tolist()

FFin.drop(FFin[FFin['Search keyword'].isin(vals)].index,inplace=True)
#FFin.shape -- 33026
del vals
del kw


#looks at adwords and remove any campaign where same adwords have been linked to more than 4 campaigns 

ag = pd.DataFrame(FFin.groupby('Ad group')['Campaign'].nunique())
#ag.groupby(['Campaign']).size() 
vals = ag[ag['Campaign']>4].index.tolist()

#check who many impresssion this will affect 
#FFin[FFin['Ad group'].isin(vals)]['Impressions'].sum() #21k 
#FFin[FFin['Ad group'].isin(vals)]['Conv. value'].sum() #3k in sales 
FFin.drop(FFin[FFin['Ad group'].isin(vals)].index,inplace=True)
#FFin.shape -32318
del vals
del ag

'''
#add a column for CTR
not working yet, need a limit for impression < clicks 
FFin['CTR']= round((FFin['Clicks'] /FFin['Impressions']).fillna(0),3)
FFin.sort_values(by='CTR',ascending=False)
'''

#remove unneccary text
FFin['Campaign'] = FFin['Campaign'].str.replace('Search:Google:UK:EN:', '')




#FFin[FFin['Impressions']<FFin['Clicks']].shape



#------------------------------------------show which factor is more relavant in the Quality score
aa =FFin.groupby(['Landing page experience','Expected click-through rate','Ad relevance','Quality score']).size()
aa.to_excel(wd+'qs_score.xlsx')



#Landing page experience,  Expected click-through rate,  Ad relevance in that order 


ag = pd.DataFrame(FFin.groupby('Ad group')['Campaign'].nunique())
ag.rename(columns={'Campaign':'CampaignsRun'},inplace=True)
#ag[0:5]



FF1 = pd.merge(FFin,ag,how='left', on='Ad group')
#FF1[0:8].T

FF1.groupby('CampaignsRun').agg({'Impressions':np.sum, 'Clicks':np.sum,'Conversions':np.sum
               , 'Conv. value':np.sum, 'Search keyword' : np.count_nonzero })


#FF1[FF1['CampaignsRun']==4].sort_values(by='Search keyword',ascending=True)[0:20].T

#------------------recode the Landing page experience,  Expected click-through rate,  Ad relevance to be numbers 

def changetonum(x):
    if x == 'Below average':
        return 1
    elif x == 'Average':
        return 2      
    elif x == 'Above average':
        return 3
    else:
        return 0

collist = ('Landing page experience','Expected click-through rate','Ad relevance')

for x in collist:
    FF1[x+'N'] = FF1[x].apply(changetonum)


#FF1.iloc[:,np.r_[4:7,15:18]][0:5].T


#-------------------------------------------------------------find average for 3 + 4 times campaign
    
#FF1.columns

agav = (FF1[FF1['CampaignsRun']>=2]
            .groupby(['Ad group','Search keyword'])
            .agg({'Landing page experienceN':np.mean
                  , 'Expected click-through rateN':np.mean
                  ,'Ad relevanceN':np.mean
                  ,'Quality score':np.mean}))


agav.rename(columns={'Landing page experienceN':'Landing page experienceN_av'
                     ,'Expected click-through rateN':'Expected click-through rateN_av'
                     ,'Ad relevanceN':'Ad relevanceN_av'
                     ,'Quality score':'Quality score_av'
                     },inplace=True)
    
#agav[0:7].T


FF2 = pd.merge(FF1,agav,how='inner', on=['Ad group','Search keyword'])
FF2.shape



def ishigher(x,y):
    if x>y:
        return 'a.lower'
    elif x==y:
        return 'b.same'
    elif x<y:
        return 'c.higher'
    else:
        return 'err'
    



FF2['Quality score_UD']= FF2.apply(lambda x: ishigher(x['Quality score_av'], x['Quality score']), axis=1)    
FF2['Landing page experience_UD']= FF2.apply(lambda x: ishigher(x['Landing page experienceN_av'], x['Landing page experienceN']), axis=1)    
FF2['Expected click-through rate_UD']= FF2.apply(lambda x: ishigher(x['Expected click-through rateN_av'], x['Expected click-through rateN']), axis=1)    
FF2['Ad relevance_UD']= FF2.apply(lambda x: ishigher(x['Ad relevanceN_av'], x['Ad relevanceN']), axis=1)        


#FF2[0:6].T    


#--------------------------------------------------------------create grouped campaign field 

FF2['Campaign_Group'] = FF2['Campaign'].str.split('_').str[0]
FF2['Campaign_Type'] = FF2['Campaign_Group'].str.split(':').str[0]



#FF2.groupby(['Campaign_Group']).size()



#-----------------------------------------------------------------------analyse a campaign type level 

camptypequal = pd.pivot_table(data=FF2
                         ,values = ['Search keyword']
                         ,index = ['Campaign_Type'] 
                         ,columns = ['Quality score_UD']
                         ,aggfunc=np.count_nonzero
                         ,fill_value = 0)

camptypequal.columns = camptypequal.columns.droplevel(0)


collist = list(camptypequal.columns.values)
camptypequal['ag_kw_count'] = 0

for x in collist:
    camptypequal['ag_kw_count'] = camptypequal['ag_kw_count'] + camptypequal[x]   

for x in collist:
    camptypequal[str(x)+'%'] = camptypequal[x]/camptypequal['ag_kw_count']

#camptypequal
camptypequal[['ag_kw_count','a.lower%','b.same%','c.higher%']].sort_values(by='c.higher%',ascending=False)



CTfigs = FF2.groupby(['Campaign_Type']).agg({'Impressions':np.sum, 'Clicks':np.sum
                        ,'Conversions':np.sum, 'Conv. value':np.sum, 'Cost':np.sum})
CTfigs['avg_conv_val']  = round(CTfigs['Conv. value'] / CTfigs['Conversions'],0).fillna(0)
CTfigs['CTR']  = round(CTfigs['Clicks'] / CTfigs['Impressions'],3).fillna(0)
CTfigs['ROI']  = round(CTfigs['Conv. value'] / CTfigs['Cost'],3).fillna(0)

CTfigs1 = pd.merge(camptypequal[['ag_kw_count','a.lower%','b.same%','c.higher%']]
                    ,CTfigs[['Impressions','CTR','ROI','Conversions','avg_conv_val']]
                    ,how='inner',on=['Campaign_Type'])

CTfigs1.sort_values(by='c.higher%',ascending=False).to_excel(wd+'qs_score.xlsx')

#chart by improvement
ax = (CTfigs1.loc[:,'a.lower%':'c.higher%'].sort_values(by='c.higher%',ascending=False)
    .plot.bar(stacked = True
    ,color=['lightblue','cornflowerblue','darkblue']))

xcount = {}    #define dict for loading the heights, works with stacked as well
for i in ax.patches:
    
    if i.get_x() in xcount: #check if the x value is present and either add the height to current val or load
        xcount[i.get_x()] += i.get_height()
    else:
        xcount[i.get_x()] = i.get_height()
    
    if i.get_height() > 0.03:
        ax.text((i.get_x() + i.get_width()/2), #middle of the bar
                (xcount[i.get_x()]) - (i.get_height()/2) , #middle of the bar verically + the height of the bar if using stacked 
                str(int(round((i.get_height()*100),0))) +'%', #the value add text format here
                ha='center' #needed to align label centerally
                ,color = 'white'
                ,fontsize = 8
                ,rotation = 90 #if you want rotataion
                )


plt.legend(bbox_to_anchor=(1,1), edgecolor = 'white')
plt.title('QS Change by high level campaign group',weight='bold',  fontsize=10)
plt.xlabel(' ')   

locs, labels = plt.yticks()
locs = locs[locs<=1]
plt.yticks( locs,['{:,.0%}'.format(x) for x in locs])

plt.show()


#CTfigs1['Conversions'].sum()







#-----------------------------------------------------------------------analyse a campaign group level 

campgroupqual = pd.pivot_table(data=FF2
                         ,values = ['Search keyword']
                         ,index = ['Campaign_Group']
                         ,columns = ['Quality score_UD']
                         ,aggfunc=np.count_nonzero
                         ,fill_value = 0)

campgroupqual.columns = campgroupqual.columns.droplevel(0)


collist = list(campgroupqual.columns.values)
campgroupqual['ag_kw_count'] = 0

for x in collist:
    campgroupqual['ag_kw_count'] = campgroupqual['ag_kw_count'] + campgroupqual[x]   

for x in collist:
    campgroupqual[str(x)+'%'] = campgroupqual[x]/campgroupqual['ag_kw_count']

#campgroupqual
campgroupqual[['ag_kw_count','c.higher%']].sort_values(by='c.higher%',ascending=False)





CTfigs = FF2.groupby(['Campaign_Group']).agg({'Impressions':np.sum, 'Clicks':np.sum
                        ,'Conversions':np.sum, 'Conv. value':np.sum, 'Cost':np.sum})
CTfigs['avg_conv_val']  = round(CTfigs['Conv. value'] / CTfigs['Conversions'],0).fillna(0)
CTfigs['CTR']  = round(CTfigs['Clicks'] / CTfigs['Impressions'],3).fillna(0)
CTfigs['ROI']  = round(CTfigs['Conv. value'] / CTfigs['Cost'],3).fillna(0)

CTfigs1 = pd.merge(campgroupqual[['ag_kw_count','a.lower%','b.same%','c.higher%']]
                    ,CTfigs[['Impressions','CTR','ROI','Conversions','avg_conv_val']]
                    ,how='inner',on=['Campaign_Group'])

CTfigs1.to_excel(wd+'Campaign_groups.xlsx')








#------------------------------------------------------------------------------ notes 

'''
#is unique across this combination. 
uq = pd.DataFrame(FFin.groupby(['Campaign','Ad group','Search keyword']).size())
uq.shape
uq.groupby([0]).size()
'''


