

library(rpart)
library(rpart.plot)
library(caTools)
library(dplyr)



acc<-read.table("Z:/Thurstan/190423 car accidents/acc_Rin.csv"
                ,comment.char = "", fill=TRUE,sep=",",header = T)




#do a train test split 
sample1 = sample.split(acc$NumberVech, SplitRatio = 0.7)
training_set = subset(acc, sample1 == TRUE)
test_set = subset(acc, sample1 == FALSE)

nrow(training_set)
nrow(test_set)


training_set[0:3,]


summary(training_set$NumberVech)





#below needs fixing for train / test setup

acc[0:3,]
colnames(acc)
nrow(acc)

tree1 <- rpart(T_fatal_or_serious ~ NumberVech+NumberCasualties, data = acc)
rpart.plot(tree1)

T_fatal_or_serious

rm() #removes DF



