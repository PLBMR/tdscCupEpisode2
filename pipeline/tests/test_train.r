#test_train.r
#helper that tests out ../train.r

#imports

source("../train.r")

#test procedures
formulaFilename = "../../models/formulae/finalMod.txt"
trainFilename = "../../data/processed/pipelineLagFrame_train.csv"
modelFilename = "../../models/trainedMods/finalMod.rds"
train(formulaFilename,trainFilename,modelFilename)
