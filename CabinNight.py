import pandas as pd
import sys
import random

class CabinNights:
    
    requests = None
    locations = None
    schedule = None
    potentialLocations = {}     # Dictionary where Cabin Nights are the keys and possible locations are the values
    availableLocations = []     # List of still available locations for cabin nights
    
    DONEWITHREQUESTED = False   # Boolean value to mark when all cabins who requested a cabin night have been assigned
    
    needsLifeguard = []         # List of Cabin Nights that need lifeguards
    
    spikeballOrBucketball = ["Spikeball", "Spikeball", "Bucketball", "Bucketball"]  # List to represent that Spikeball and Bucketball can only be assigned to 2 different cabins
    
    assignments = {}            # Dictionary where key will be cabins (or double cabin combos) and values will be their assignment
    
    staff = None
    campM = None
    camp1 = None    # Camp variables will be updated to contain that camp's assignment for the night, 
    camp2 = None    # i.e. 'cabin night', 'camp night', etc.
    camp3 = None    
    camp4 = None
    
    camps = {}
    cabinsThatRequested = []
    totalCabins = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,27,28,17,18,19,20,21,22,23,24,25,26,29,30,31,32,33,34,35,36,41,42,43,44,45,46,47,48,49,50,51,52,55,56,57,58,59,60,61,62,63,64,65,66,67,68]
    camps["M"] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,27,28]
    camps["1"] = [17,18,19,20,21,22,23,24,25,26]
    camps["2"] = [29,30,31,32,33,34,35,36]
    camps["3"] = [41,42,43,44,45,46,47,48,49,50,51,52]
    camps["4"] = [55,56,57,58,59,60,61,62,63,64,65,66,67,68]
    
    def readCSV(self, requestsFile, locationsFile, scheduleFile, possibleLocationsFile):
        CabinNights.requests = pd.read_csv(requestsFile)
        CabinNights.requests = CabinNights.requests.drop("Timestamp", axis = 1)
        CabinNights.locations = pd.read_csv(locationsFile)
        CabinNights.schedule = pd.read_csv(scheduleFile)
        
        possibleLocations = pd.read_csv(possibleLocationsFile)
        for index, row in possibleLocations.iterrows():
            CabinNights.potentialLocations[row["Cabin Night"]] = []
            for each in row["Location"].split(', '):
                # print(each)
                CabinNights.potentialLocations[row["Cabin Night"]].append(each)
            if row["Lifeguard"] == "Yes":
                CabinNights.needsLifeguard.append(row["Cabin Night"])
                
        # for each in CabinNights.potentialLocations:
            # print(each, CabinNights.potentialLocations[each])
        
        # print(len(CabinNights.schedule.columns))
        
        # print("##########")
        # print(CabinNights.requests)
        # print("##########")
        # print(CabinNights.locations)
        # print("##########")
        # print(CabinNights.schedule)
        
    def whichCamp(self, cabinNumber):
        # Takes in a cabin number from the randomly selected row / cabin result from chooseCabinRandom
        
        if (cabinNumber in self.camps["M"]):
            return 'M'
        
        elif (cabinNumber in self.camps["1"]):
            return '1'
        
        elif (cabinNumber in self.camps["2"]):
            return '2'
        
        elif (cabinNumber in self.camps["3"]):
            return '3'
        
        elif (cabinNumber in self.camps["4"]):
            return '4'
        
        return None
        
    def dictionaryInitializer(self, requestsTable, scheduleTable):
        # Go through requests table and schedule table to create a dictionary where assignments will be stored
        # For example, if a camp has cabin night, all of its cabins will have their own key in the dictionary
        # If a camp has double cabin night, each duplex will have its own key
        # If a camp has camp night, its assignment will already be included in the schedule in the form 
        # 'Camp 2 - Camp Night, Pool'
        # locationsFile should also reflect pre-assigned camp nights, i.e. if Camp 2 has Pool then Pool should not be included 
        # in available locations. This last part is subject to change, working on being able to have static location information
        # that would update depending on the assignments input
        # No return value        

        scheduleList = scheduleTable.values.tolist()
        
        CabinNights.staff = scheduleList[0][0]
        CabinNights.campM = scheduleList[0][1]
        CabinNights.camp1 = scheduleList[0][2]
        CabinNights.camp2 = scheduleList[0][3]
        CabinNights.camp3 = scheduleList[0][4]
        CabinNights.camp4 = scheduleList[0][5]
            
        for index, row in requestsTable.iterrows():
            cabin = row['What cabin are you in?']
            CabinNights.cabinsThatRequested.append(cabin)
            
        for cabin in CabinNights.totalCabins:    
            camp = self.whichCamp(int(cabin))
            if camp == 'M':
                assignment = self.campM
            elif camp == '1':
                assignment = self.camp1
            elif camp == '2':
                assignment = self.camp2
            elif camp == '3':
                assignment = self.camp3
            elif camp == '4':
                assignment = self.camp4
            if assignment == 'Cabin Night':
                CabinNights.assignments[str(cabin)] = None
            elif 'Camp Night' in assignment:
                campNightAssignment = assignment.split(', ')[1]
                CabinNights.assignments[str(cabin)] = campNightAssignment
                CabinNights.availableLocations = list(filter(lambda a: a != campNightAssignment, CabinNights.availableLocations))
            elif assignment == 'Double Cabin Night':
                if (cabin % 2 != 0):
                    doublecabin = cabin + 1
                    CabinNights.assignments[str(cabin)+','+str(doublecabin)] = None
                else:
                    doublecabin = cabin - 1
                    if str(doublecabin)+','+str(cabin) not in CabinNights.assignments.keys():
                        CabinNights.assignments[str(doublecabin)+','+str(cabin)] = None
        
        # print(CabinNights.availableLocations)
        # for each in CabinNights.assignments:
        #     print(each, CabinNights.assignments[each])
            
        # self.chooseCabinRandom(requestsTable)
                
    
    def locationListInitializer(self, locationsTable):
        # Go through locations table and create a list of each location and how many cabins can be placed there
        # For example, for "Lower Fields, 4", "Lower Fields" would be appended to availableLocations list 4 times
        # No return value
        
        for index, row in locationsTable.iterrows():
            location = row["Location"]
            num = row["Amount"]
            for i in range(num):
                CabinNights.availableLocations.append(location)
        
        # print(CabinNights.availableLocations)
        
        return
    
    def dictionaryUpdater(self, cabin, assignment, location):
        # Update assignments dictionary with cabin(s) as the key and (assignment,location) as the value
        # Includes a check to see if the cabin(s) already has a value in the dictionary prior to update
        # Before update, the value should be None
        # Returns a boolean: False is cabin has already been assigned, True if assignment was put into dictionary
        
        if CabinNights.assignments[cabin] != None:
            return False
        CabinNights.assignments[cabin] = assignment + " (" + location + ")" 
        return True

    def chooseCabinRandom(self, requestsTable):
        # Randomly selects a cabin from the requests that will be assigned next
        # Returns a cabin number and removes the cabin (or the duplex for double cabin nights) from the cabins list
        
        if len(CabinNights.cabinsThatRequested) > 0:
            choice = random.choice(CabinNights.cabinsThatRequested)
        else:
            self.DONEWITHREQUESTED = True
            choice = random.choice(CabinNights.totalCabins)
        camp = self.whichCamp(int(choice))
        if camp == 'M':
            assignment = self.campM
        elif camp == '1':
            assignment = self.camp1
        elif camp == '2':
            assignment = self.camp2
        elif camp == '3':
            assignment = self.camp3
        elif camp == '4':
            assignment = self.camp4
        if (assignment == 'Cabin Night') or ('Camp Night' in assignment):
            # print(CabinNights.totalCabins)
            # print("Choice", choice)
            # print("TotalCabins", CabinNights.totalCabins)
            CabinNights.totalCabins.remove(choice)
            if self.DONEWITHREQUESTED == False:
                CabinNights.cabinsThatRequested.remove(choice)
        elif assignment == 'Double Cabin Night':
            if (choice % 2 != 0):
                doublecabin = choice + 1
                CabinNights.totalCabins.remove(choice)
                CabinNights.totalCabins.remove(doublecabin)
                # if self.DONEWITHREQUESTED == False:
                    # CabinNights.cabinsThatRequested.remove(choice)
                    # if doublecabin in CabinNights.cabinsThatRequested:
                        # CabinNights.cabinsThatRequested.remove(doublecabin)
                choice = str(choice)+","+str(doublecabin)
            else:
                doublecabin = choice - 1
                CabinNights.totalCabins.remove(choice)
                CabinNights.totalCabins.remove(doublecabin)
                # if self.DONEWITHREQUESTED == False:
                    # CabinNights.cabinsThatRequested.remove(choice)
                    # if doublecabin in CabinNights.cabinsThatRequested:
                        # CabinNights.cabinsThatRequested.remove(doublecabin)
                choice = str(doublecabin)+","+str(choice)
        return str(choice)
        
    
    def lifeguardCheck(self, requestsTable, cabin):
        # Checks the requests table to see if there is a lifeguard in the cabin(s) that is on duty this night
        # Returns a boolean (True if lifeguard available for this night, False if not)
        cabin1 = cabin
        cabin2 = ""
        if len(cabin1) > 2:
            cabins = cabin.split(',')
            cabin2 = cabins[1]   
            cabin1 = cabins[0]
            # print("CABIN1", cabin1)
            # print("CABIN2", cabin2)
            if int(cabin2) in CabinNights.cabinsThatRequested and int(cabin1) not in CabinNights.cabinsThatRequested:
                temp = cabin1
                cabin1 = cabin2
                cabin2 = temp

        # print("CABIN1", cabin1)
        # print("CABIN2", cabin2)
        # print("CABINSTHATREQUESTED", CabinNights.cabinsThatRequested)
        # print(cabin2 in CabinNights.cabinsThatRequested)
        # print(cabin1 not in CabinNights.cabinsThatRequested)
        row = CabinNights.requests.loc[(CabinNights.requests["What cabin are you in?"] == int(cabin1))]
        # print("CABIN1", cabin1)
        # print("CABIN2", cabin2)
        # print(row)
        lifeguard = row.values[0,3]
        lifeguardStaff = row.values[0,4]
        # print("LIFEGUARD",lifeguard)
        # print("LIFEGUARDSTAFF",lifeguardStaff)
        # print(cabin1, lifeguardStaff, lifeguardStaff == CabinNights.staff)
        if (lifeguard == "Yes" and lifeguardStaff == CabinNights.staff) or lifeguardStaff == "Both":
            return True
        if cabin2 == "":
            return False
        if cabin2 not in CabinNights.cabinsThatRequested:
            return False
        row = CabinNights.requests.loc[(CabinNights.requests["What cabin are you in?"] == int(cabin2))]
        # print(row.size)
        lifeguard = row.values[0,3]
        lifeguardStaff = row.values[0,4]
        # print(cabin2, lifeguardStaff, lifeguardStaff == CabinNights.staff)
        if (lifeguard == "Yes" and lifeguardStaff == CabinNights.staff) or lifeguardStaff == "Both":
            return True
        return False
            
    def assignCabin(self, requestsTable, locationsTable):
        # Has a while loop until there are no cabins remaining in the requests
        # Calls chooseCabinRandom function to decide which cabin(s) is assigned next
        # After a cabin is assigned, dictionaryUpdater is called and its row is then nremoved from the table
        # No return value
        # i = 1
        while len(CabinNights.totalCabins) > 0:
            # print(i)
            # i += 1
            lastCabinNight = ""
            done = False
            success = False
            doubleCabinNight = False
            # if i > 2:
            #     if len(primChoice) > 2:
            #         print("CHOICE",self.assignments[int(choice)])
            #     else:
            #     print("PRIMCHOICE",primChoice, self.assignments[primChoice])
                
            primChoice = CabinNights.chooseCabinRandom(self,requestsTable)
            # print("PRIMCHOICECABIN", primChoice)
            # print("CABINSTHATREQUESTED", CabinNights.cabinsThatRequested)
            # print("TOTALCABINS", CabinNights.totalCabins)
            if self.DONEWITHREQUESTED == False:          
                lifeguardBool = CabinNights.lifeguardCheck(self, requestsTable, primChoice)
            else:
                lifeguardBool = False
            # print("LIFEGUARDBOOL", lifeguardBool)
            # print("DONEWITHREQUESTED", self.DONEWITHREQUESTED)
            if len(primChoice) > 2:
                doubleCabinNight = True
                temp = primChoice.split(',')
                # print("Cabins", temp[0],temp[1])
                # print("cabinsThatRequested", CabinNights.cabinsThatRequested)
                if int(temp[0]) in CabinNights.cabinsThatRequested and int(temp[1]) not in CabinNights.cabinsThatRequested:
                    choice = temp[0]
                    # print("sitch 1", temp[0], temp[1], choice)
                elif int(temp[1]) in CabinNights.cabinsThatRequested and int(temp[0]) not in CabinNights.cabinsThatRequested:
                    choice = temp[1]
                    # print("sitch 2", temp[0], temp[1], choice)
                else:
                    choice = random.choice([temp[0],temp[1]])
                    # print("sitch 3", temp[0], temp[1], choice)
                if self.DONEWITHREQUESTED == False:
                    if int(temp[0]) in CabinNights.cabinsThatRequested:
                        CabinNights.cabinsThatRequested.remove(int(temp[0]))
                    if int(temp[1]) in CabinNights.cabinsThatRequested:
                        CabinNights.cabinsThatRequested.remove(int(temp[1]))
                    row = CabinNights.requests.loc[(CabinNights.requests["What cabin are you in?"] == int(choice))]
                    prefs = row.iloc[0]["Select your top 5 preferences for cabin nights"]
                    lastCabinNight = row.iloc[0]["What was your last cabin night? Type None if not applicable"]
                    prefs = prefs.split(', ')
                else:
                    prefs = list(set(CabinNights.potentialLocations.keys()))
                camp = self.whichCamp(int(choice))
                if camp == 'M':
                    assignment = self.campM
                elif camp == '1':
                    assignment = self.camp1
                elif camp == '2':
                    assignment = self.camp2
                elif camp == '3':
                    assignment = self.camp3
                else:
                    assignment = self.camp4
            else:
                if self.DONEWITHREQUESTED == False:
                    row = CabinNights.requests.loc[(CabinNights.requests["What cabin are you in?"] == int(primChoice))]
                    prefs = row.iloc[0]["Select your top 5 preferences for cabin nights"]
                    lastCabinNight = row.iloc[0]["What was your last cabin night? Type None if not applicable"]
                    prefs = prefs.split(', ')
                else:
                    prefs = random.sample(list(CabinNights.potentialLocations.keys()), len(list(CabinNights.potentialLocations.keys())))
                camp = self.whichCamp(int(primChoice))
                if camp == 'M':
                    assignment = self.campM
                elif camp == '1':
                    assignment = self.camp1
                elif camp == '2':
                    assignment = self.camp2
                elif camp == '3':
                    assignment = self.camp3
                else:
                    assignment = self.camp4
            
            # print("CAMP", camp)
            # print("ASSIGNMENT", assignment)
            # print(primChoice)
            # print(self.DONEWITHREQUESTED)
            # print(prefs)
            
            if "Camp Night" in assignment:
                continue
            
            for each in prefs:
                if (each == "Sharkstooth Pile" or each == "Field Games"):
                    if len(primChoice) > 2:
                        if int(primChoice.split(',')[0]) > 28:
                            continue
                    else:
                        if int(primChoice) > 28:
                            continue
                if (each == "Drip Drip Drop"):
                        if len(primChoice) > 2:
                            if int(primChoice.split(',')[0]) > 36:
                                continue
                        else:
                            if int(primChoice) > 28:
                                continue
                if each == lastCabinNight:
                    continue
                potentials = CabinNights.potentialLocations[each]
                for loc in potentials:
                    if done == True:
                        break
                    if loc in CabinNights.availableLocations:
                        if each in CabinNights.needsLifeguard and lifeguardBool == False:
                            continue
                        if (each == "Spikeball" and "Spikeball" not in CabinNights.spikeballOrBucketball):
                            continue
                        elif (each == "Bucketball" and "Bucketball" not in CabinNights.spikeballOrBucketball):
                            continue
                        success = CabinNights.dictionaryUpdater(self, primChoice, each, loc)
                        done = True
                        # print("SUCCESSCHECK", success)
                        if success == True:
                            CabinNights.availableLocations.remove(loc)
                            if each == "Spikeball" or each == "Bucketball":
                                # print("EACH", each)
                                # print("SOB", CabinNights.spikeballOrBucketball)
                                if doubleCabinNight == True:
                                    CabinNights.spikeballOrBucketball = list(filter(lambda a: a != each, CabinNights.spikeballOrBucketball))
                                else:
                                    CabinNights.spikeballOrBucketball.remove(each)
                                # print("SOB2", CabinNights.spikeballOrBucketball)
                # print("DONE", done, primChoice, each, loc) 
                if done == True:
                    break  
            if done == False:
                prefs = random.sample(list(CabinNights.potentialLocations.keys()), len(list(CabinNights.potentialLocations.keys())))
                for each in prefs:
                    # print(each, primChoice, int(primChoice) > 28)
                    if (each == "Sharkstooth Pile" or each == "Field Games") and int(primChoice) > 28:
                        continue
                    if (each == "Drip Drip Drop") and int(primChoice) > 36:
                        continue
                    if each == lastCabinNight:
                        continue
                    potentials = CabinNights.potentialLocations[each]
                    for loc in potentials:
                        if done == True:
                            break
                        if loc in CabinNights.availableLocations:
                            if each in CabinNights.needsLifeguard and lifeguardBool == False:
                                continue
                            if (each == "Spikeball" and "Spikeball" not in CabinNights.spikeballOrBucketball):
                                continue
                            elif (each == "Bucketball" and "Bucketball" not in CabinNights.spikeballOrBucketball):
                                continue
                            # print("SUCCESS", success)
                            # print("DONE-MID", done)
                            # print("EACH", each)
                            success = CabinNights.dictionaryUpdater(self, primChoice, each, loc)
                            done = True
                            if success == True:
                                CabinNights.availableLocations.remove(loc)
                                if each == "Spikeball" or each == "Bucketball":
                                    # print("EACH", each)
                                    # print("SOB", CabinNights.spikeballOrBucketball)
                                    if doubleCabinNight == True:
                                        CabinNights.spikeballOrBucketball = list(filter(lambda a: a != each, CabinNights.spikeballOrBucketball))
                                    else:
                                        CabinNights.spikeballOrBucketball.remove(each)
                                 # print("SOB2", CabinNights.spikeballOrBucketball)
                    # print("DONE2", done, success, primChoice, each, loc)
                    if done == True:
                        # print("BREAK")
                        break
            # print("#############", len(CabinNights.totalCabins))
        # print("HERE")
        return
    
    # TODO fix assignments for cabins with camp nights
    
    def outputDictionary(self):
        # Sorts the dictionary keys in numerical order and then returns the assignments in an easily digestible format
        # Could potentially write this information out to a file, not sure at the time of writing (7/1/21)
        # Returns formatted information, with each assignment on its own line
        retString = ""
        # keys = sorted(CabinNights.assignments.keys())
        # print(keys)
        for each in CabinNights.assignments:
            # print(each, CabinNights.assignments[each])
            retString += each + " - " + CabinNights.assignments[each] + "\n"
        print(retString.strip())
        return retString
    
    def writeToFile(self, assignmentsFinal):
        # If writing out assignments to a file, this function will take the output of outputDictionary and write it to a file
        # If not writing to a file, this function will not be used
        pass

def main():
    # requests = sys.argv[1]      # Takes command line arguments that represent cabin night requests, available locations and
    # locations = sys.argv[2]     # activities for cabin nights, and what the assignments are for that night (cabin night,             # To be uncommented when completed
    # schedule = sys.argv[3]      # double cabin night, etc.). The third argument also includes which staff is on that night
    # possibleLocations = sys.argv[4]
    
    requests = "TESTCabinNightRequests.csv"
    locations = "CabinNightLocations.csv"
    schedule = "CabinNightAssignments.csv"
    possibleLocations = "PossibleAssignmentLocations.csv"
    
    CN = CabinNights()
    CN.readCSV(requests, locations, schedule, possibleLocations)  # Calls the readCSV function to convert the csv files into pandas tables
    CN.locationListInitializer(CN.locations) 
    CN.dictionaryInitializer(CN.requests, CN.schedule)
    CN.assignCabin(CN.requests, CN.locations)
    CN.outputDictionary()
    
        
    # boolean = CN.lifeguardCheck(CN.requests, '2')       # lifeguardCheck test
    # print(boolean)
    
    # CN.dictionaryInitializer(CN.requests, CN.schedule)  # dictionaryInitializer test
    
    
    
    # camp1 = CN.whichCamp(23)
    # campM = CN.whichCamp(27)
    # camp2 = CN.whichCamp(33)                          # whichCamp test
    # camp3 = CN.whichCamp(43)
    # camp4 = CN.whichCamp(63)
    # campNone = CN.whichCamp(53)
    # print(camp1, camp2, camp3, campM, camp4, campNone)

if __name__ == '__main__':
    main()
    