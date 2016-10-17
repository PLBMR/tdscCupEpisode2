#predict.r
#helper to predict our outcomes based on a particular model and some
#tests of accuracy

#imports

library(dplyr)
library(readr)

#prediction functions

customPredict <- function(givenMod,predictorSet,decisionRule = NA){
    #helper that returns predictions for our model given a particular
    #predictor set
    probPredictions = predict(givenMod,newdata = predictorSet,type = "response")
    if (!is.na(decisionRule)){
        #means we can make an if-else prediction with our logistic regression
        classPredictions = ifelse(probPredictions < decisionRule,0,1)
        return(classPredictions)
    }
    else {
        #just return the probabilities
        return(probPredictions)
    }
}

predictNextWeek <- function(givenMod,thisWeekFrame,decisionRule = NA){
    #helper for predicting outcomes for next week given this week's data
    #first, shift to next week for prediction
    farthestLag = 3 #based on the model
    for (i in 0:(farthestLag-1)){
        #capture the past week and the future week
        pastWeekVar = paste0("eggPurchase_week",farthestLag - i)
        nextWeekVar = paste0("eggPurchase_week",farthestLag - i - 1)
        #then shift future week information to past week
        thisWeekFrame[pastWeekVar] = thisWeekFrame[nextWeekVar]
    }
    #then predict
    predictions = customPredict(givenMod,thisWeekFrame,decisionRule)
    return(predictions)
}

predictAndSave <- function(givenMod,processedFrame,predictionFilename,
                           decisionRule = NA,predictFuture = FALSE){
    #helper that acts as an overall predictor method
    #check if target variable is in there
    exportableFeatures = c("household_key","predictions")
    if ("eggPurchase_week0" %in% colnames(processedFrame)){
        #means we have a target variable
        processedFrame$target = processedFrame$eggPurchase_week0
        exportableFeatures = c(exportableFeatures,"target")
    }
    if (predictFuture){
        #section of considered observations to most recent ones
        processedFrame = processedFrame[which(processedFrame["weekOf"]
                                        == max(processedFrame["weekOf"])),]
        processedFrame$predictions = predictNextWeek(givenMod,processedFrame,
                                                     decisionRule)
            }
    else { #do not need inductive predictions
        processedFrame$predictions = customPredict(givenMod,processedFrame,
                                                   decisionRule)
    }
    exportableFrame = processedFrame[,exportableFeatures]
    write_csv(exportableFrame,predictionFilename)
    return(exportableFrame)
}

#performance functions

getAccuracy <- function(predictedClasses,actualClasses){
    #function that is meant to check our accuracy score
    numCorrect = length(which(predictedClasses == actualClasses))
    return(numCorrect / length(predictedClasses))
}

getBrierScore <- function(predictedProbabilities,actualClasses){
    #helper for calculate the brier score, or the mean response residual
    sumSRR = sum((predictedProbabilities - actualClasses)^2)
    meanResidualResponse = (1 / length(predictedProbabilities)) * sumSRR
    return(meanResidualResponse)
}

#test
newMod = readRDS("../models/trainedMods/finalMod.rds")
givenFrame = read.csv("../data/processed/pipelineLagFrame_test.csv")
predictionFilename = "../data/predictions/testSetProbPredictions.csv"
predictAndSave(newMod,givenFrame,predictionFilename)
predictionFilename = "../data/predictions/testSetFutureProbPredictions.csv"
outcomeFrame = predictAndSave(newMod,givenFrame,predictionFilename,
                              predictFuture = TRUE)
getBrierScore(outcomeFrame$predictions,outcomeFrame$target)
