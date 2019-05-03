
#load libs
library("rpart")
library("rpart.plot")
library("Ggplot2")

telco<-read.table("C:/Users/thurstan.green/OneDrive - PERFORM GROUP/KaggleDatasets/telco-churn/WA_Fn-UseC_-Telco-Customer-Churn.csv"
                  ,sep=",",header = T)

#telco[1:10,]
#colnames(telco)


#aggregate(telco$TotalCharges, by=list(Category=telco$Churn), FUN=sum) #useless but does work
#aggregate(telco$customerID, by=list(Category=telco$Churn), FUN=length) #actual count
#think dplyr maybe better for this, seems to come up a lot on stackoverflow

#alternativly add a count
telco["Counter"] <-1
aggregate(telco$Counter, by=list(Category=telco$Churn), FUN=sum) #actual count


#I couldn't get the drop variable woring on rpart so subsetted the df instead
telco1 = subset(telco, select = -c(customerID)) 
telco1 = subset(telco, select = c(PaperlessBilling,PaymentMethod,Churn)) 
colnames(telco1)


aggregate(telco1$Counter, by=list(Category=telco$Contract), FUN=sum )
aggregate(telco1$Counter, by=list(Category=telco$InternetService), FUN=sum )
aggregate(telco1$Counter, by=list(telco1$InternetService,telco1$Churn), FUN=sum )

telco1[1:10,]

#telco_t1 <- rpart(Churn ~. -PhoneService, data = telco1) #not working but should be, would be v useful
#telco_t1 <- rpart(Churn ~ tenure+PhoneService, data = telco)

telco_t1 <- rpart(Churn ~InternetService+MultipleLines, data = telco1)

#running the model using R part
telco_t1 <- rpart(Churn ~ ., data = telco1)

'''this control the tree, sitll havent found a way to stop it switching between yes and no though
rpart.control(minsplit = 20, minbucket = round(minsplit/3), cp = 0.01, 
              maxcompete = 4, maxsurrogate = 5, usesurrogate = 2, xval = 10,
              surrogatestyle = 0, maxdepth = 30, …)
'''

#10x give the size of the split pop, not the number of targets in that pop
rpart.plot((telco_t1))
rpart.plot((telco_t1), extra = 1)
rpart.plot((telco_t1), extra = 101)
rpart.plot((telco_t1), extra = 104)
rpart.plot((telco_t1), extra = 108)


rm(telco)
rm(telco1)
rm(telco_t1)



##a scatter plot ##############################################







