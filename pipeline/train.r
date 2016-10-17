#train.r
#helper that trains our particular model and serializes it

#imports

library(readr)
library(dplyr)
library(sourcetools)

#functions

train <- function(formulaFilename,trainFilename,modelFilename){
    #helper that trains a given logistic regression and serializes the trained
    #model
    #load in our training assets
    formula = read(formulaFilename)
    trainSet = read_csv(trainFilename)
    #train our model
    trainedMod.logr = glm(formula,data = trainSet,family = "binomial") #for logr
    #then serialize it
    saveRDS(trainedMod.logr,modelFilename)
    return(trainedMod.logr)
}
