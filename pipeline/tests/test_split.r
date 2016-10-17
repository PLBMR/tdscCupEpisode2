#test_split.r
#helper to test ../split.r

#imports
library(sourcetools)
source("../split.r")

#run some tests
processedFilename = "../../data/processed/pipelineLagFrame.csv"
percentTrain = .7
splitAndSave(processedFilename,percentTrain)
