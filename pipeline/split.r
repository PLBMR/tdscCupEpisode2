#split.r
#helper script that splits our processed panelized data into train and test sets
#of data
#adapted from the test-train splits found in 
#../codeNotebooks/modelSelectionProcedure.Rmd

#imports

library(sourcetools)
library(dplyr)
library(readr)

#functions

split <- function(processedFrame,percentTrain){
    #helper that splits our data at the level of household keys
    #sample household keys
    householdKeyVec = unique(processedFrame$household_key)
    sampleSize = round(length(householdKeyVec) * percentTrain)
    trainHouseholds = sample(householdKeyVec,sampleSize)
    #make train and test sets
    trainSet = processedFrame[which(
                processedFrame$household_key %in% trainHouseholds),]
    testSet = processedFrame[which(
                !(processedFrame$household_key %in% trainHouseholds)),]
    return(list(train = trainSet,test = testSet))
}

splitAndSave <- function(processedFilename,percentTrain){
    #helper that performs the split and then saves the split to relevant files
    processedFrame = read_csv(processedFilename)
    splitDatasets = split(processedFrame,percentTrain)
    #name new files
    fileTab = substr(processedFilename,1,
                     nchar(processedFilename) - nchar(".csv"))
    trainFilename = paste0(fileTab,"_train.csv")
    testFilename = paste0(fileTab,"_test.csv")
    #save our split
    write_csv(splitDatasets$train,trainFilename)
    write_csv(splitDatasets$test,testFilename)
    #the return our list of split datasets
    return(splitDatasets)
}
