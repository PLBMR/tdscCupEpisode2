#process.py
#helper script for panelizing our data to represent household i on week t with
#our relevant predictors
#adapted from ../codeNotebooks/getHouseholdFrame.py
#takes in two command line arguments
#imports

import pandas as pd
import numpy as np
import sys #for command line arguments

#helpers

def makeEggVar(purchaseFrame):
    #helper for making egg variable
    purchaseFrame["isEggPurchase"] = 0
    purchaseFrame.loc[purchaseFrame["COMMODITY_DESC"] == "EGGS",
                        "isEggPurchase"] = 1
    return purchaseFrame

def makeEggLagVar(householdFrame,purchaseFrame,numLag):
    #designed to get lag variables for egg variable
    def atLeastOne(x):
        #checks to see if sum of x is at least one
        if (np.sum(x) >= 1): return 1
        else: return 0
    #get variables that occur in this week
    maxDay = purchaseFrame["DAY"].max()
    numDaysInWeek = 7
    #get our timeRange
    consideredMaxDay = maxDay - (numLag * numDaysInWeek)
    consideredMinDay = consideredMaxDay - (numDaysInWeek - 1)
    timePurchaseFrame = purchaseFrame[(
        purchaseFrame["DAY"] <= consideredMaxDay) &
        (purchaseFrame["DAY"] >= consideredMinDay)]
    #get us our household frame for this seciton
    householdInTimeFrame = timePurchaseFrame.groupby("household_key",
            as_index = False).agg({"isEggPurchase":atLeastOne})
    #then merge with householdFrame
    householdFrame = householdFrame.merge(householdInTimeFrame,how = "left",
                                            on = "household_key")
    #then do some data cleanup
    eggPurchaseVarName = "eggPurchase_week" + str(numLag)
    householdFrame = householdFrame.rename(columns={"isEggPurchase":
                                        "eggPurchase_week" + str(numLag)})
    householdFrame.loc[householdFrame[eggPurchaseVarName].isnull(),
                        eggPurchaseVarName] = 0
    return householdFrame

def generateLagsOnWeeks(householdFrame,purchaseFrame,numWeeks,numLags):
    #generate lags for information based on week I
    maxDay = purchaseFrame["DAY"].max()
    numDaysInWeek = 7
    numHouseholds = householdFrame["household_key"].shape[0]
    for week in xrange(numWeeks):
        #consider purchases up to this day
        consideredMaxDay = maxDay - (week * numDaysInWeek)
        consideredPurchaseFrame = purchaseFrame[purchaseFrame["DAY"] <=
                                                consideredMaxDay]
        #get a temporary frame
        tempHouseholdFrame = householdFrame.loc[0:(numHouseholds-1),
                            ["household_key","numBaskets","weekOf"]].copy()
        tempHouseholdFrame["weekOf"] = consideredMaxDay
        #then generate lags for this subset
        for lagNum in xrange(numLags):
            tempHouseholdFrame = makeEggLagVar(tempHouseholdFrame,
                                                consideredPurchaseFrame,
                                                lagNum)
        if (week == 0): #let us initialize this process
            householdFrame = tempHouseholdFrame
        else:
            householdFrame = householdFrame.append(tempHouseholdFrame,
                                                    ignore_index = True)
    return householdFrame

def makeHouseholdLevVar(householdFrame,purchaseFrame,varName):
    #helper that makes household level information for particular variables
    givenPurchaseFrame = purchaseFrame[purchaseFrame[varName].notnull()]
    #get aggregation function
    def givenVarNameLev(x):
        return x.iloc[0]
    householdVarNameFrame = givenPurchaseFrame.groupby("household_key",
                                as_index = False).agg({varName:givenVarNameLev})
    #then merge
    householdFrame = householdFrame.merge(householdVarNameFrame,
                                         how = "left",
                                         on = "household_key")
    return householdFrame

def getNumWeeksConsidered(numLags,purchaseFrame):
    #helper for getting the number of weeks considered
    #get number of days
    maxDay = np.max(purchaseFrame["DAY"])
    minDay = np.min(purchaseFrame["DAY"])
    numDays = maxDay - minDay + 1 #to account for first day
    #number of weeks within these days
    daysInWeek = 7
    numWeeks = int(np.floor(float(numDays) / daysInWeek))
    #account for lags available
    numWeeksConsidered = numWeeks - numLags + 1 #numLags includes target
    return numWeeksConsidered

def makeLoyaltyCardVar(householdFrame,purchaseFrame):
    #generates variable that indicates average loyalty discounts per basket of
    #individual
    basketFrame = purchaseFrame.groupby(["BASKET_ID","household_key"],
            as_index = False)["LOY_CARD_DISC"].sum()
    discPerHousehold = basketFrame.groupby("household_key",as_index = False)[
                                "LOY_CARD_DISC"].mean()
    discPerHousehold = discPerHousehold.rename(columns = {"LOY_CARD_DISC":
                                                "avgBasketLoyaltyDiscount"})
    householdFrame = householdFrame.merge(discPerHousehold,how = "left",
                                            on = "household_key")
    return householdFrame

def getNetSpendAmtWithoutEggs(householdFrame,purchaseFrame):
    #get the average net spending amount without eggs
    withoutEggsFrame = purchaseFrame[purchaseFrame["COMMODITY_DESC"] != "EGGS"]
    basketFrame = withoutEggsFrame.groupby(["BASKET_ID","household_key"],
                                as_index = False)["NET_SPEND_AMT"].sum()
    householdMeanPurchaseFrame = basketFrame.groupby("household_key",
            as_index = False)["NET_SPEND_AMT"].mean()
    householdMeanPurchaseFrame = householdMeanPurchaseFrame.rename(
            columns = {"NET_SPEND_AMT":"avgSpendAmtPerBasket"})
    householdFrame = householdFrame.merge(householdMeanPurchaseFrame,
            how = "left",on = "household_key")
    return householdFrame

def processDataset(rawFilename,processedFilename):
    #main method for processing our data
    #quick check to make sure our files are appropriately named
    if ("/" not in rawFilename):
        rawFilename = "../data/raw/" + rawFilename
    elif ("/" not in processedFilename):
        processedFilename = "../data/processed/" + processedFilename
    #then import dataset
    purchaseFrame = pd.read_csv(rawFilename)
    purchaseFrame = makeEggVar(purchaseFrame)
    #get group of household purchases along with number of trips
    householdFrame = purchaseFrame.groupby("household_key",as_index = False)[
                                    "BASKET_ID"].count()
    householdFrame = householdFrame.rename(columns={"BASKET_ID":"numBaskets"})
    householdFrame["weekOf"] = 0 #will build on this information
    numLags = 4 #including target
    numWeeksConsidered = getNumWeeksConsidered(numLags,purchaseFrame)
    householdFrame = generateLagsOnWeeks(householdFrame,purchaseFrame,
                                         numWeeksConsidered,numLags)                
    #then export
    householdFrame.to_csv(processedFilename,index = False)
    print "Processing Done!"

#main process

if __name__ == "__main__":
    #get filenames
    print "Processing Data..."
    rawFilename = sys.argv[1]
    processedFilename = sys.argv[2]
    processDataset(rawFilename,processedFilename)

