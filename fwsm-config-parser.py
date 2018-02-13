import re
import csv


class ObjectData:

    def __init__(self, objType, objName):
        self.objName = objName
        self.objType = objType
        self.serviceType = None
        if self.objType == 1:
            self.objTypename = 'name'
        if self.objType == 2:
            self.objTypename = 'object-group network'
        if self.objType == 3:
            self.objTypename = 'object network'
        if self.objType == 4:
            self.objTypename = 'object-group service'
        self.contents = []

    def addto(self,input):
        self.contents.append(input)

    def __repr__(self):
        return "TypeID:: {}, TypeName :: {}, Name :: {} and contains:::".format(self.objType, self.objTypename, self.objName)

    def __str__(self):
        return "{}".format('"'.join(self.contents))


fileName = 'C:\\Users\\t721\\Desktop\\workbook\\test.txt'
csvfile = 'C:\\Users\\t721\\Desktop\\workbook\\test.csv'
fileContents = []
objectRef = []
searchObjRef = []
searchObjList = []
lookupLevel = 0
lookupObjId = 0
objectCount = 0
outputlist = []
nameObjCount = 0
fwVersion = 'low'
runOnceSearchFill = 1


### OPEN FILE TO READ LINES TO LIST
with open(fileName, 'r') as f:
   lines = f.readlines()
   f.close()


### FIND VERSION FROM CONFIG FILE
for line in lines:
    pattern = '(.*)Version(\s)(.*)[.].*'
    match = re.search(pattern, line)
    if match:
        string = match.group() + '\n'
        string = string.split()
        string = string[2].split('.')
        if int(string[0]) > 4:
            fwVersion = 'high'
            print('Running for new config Version')
        else:
            fwVersion = 'low'
            print('Running for old config Version')


# ADD member 'name' OBJECTS to SEARCHLIST for old version config.
# *** IN OLDER CONFIGS, THE SUBNET MASK CAN BE FOUND FROM network-object OR ACL entries IF the name object is being used

if fwVersion == 'low':
    for line in lines:
        pattern = '^name(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            objectRef.append(ObjectData(1, string[2]))
            found = False
            for line0 in lines:
                pattern0 = str('^(\040)(network\-object\s)' + string[1] + '\s(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
                match0 = re.search(pattern0, line0)
                if match0:
                    found = True
                    string0 = match0.group() + '\n'
                    string0 = string0.split()
                    if str(string0[1]) == str(string[1]):
                        ipa = str(string0[1] + '/' + string0[2])
                        objectRef[lookupObjId - 1].addto(ipa)
                        break
            if found is False:
                for line0 in lines:
                    pattern1 = str('^access\-list(.*)(' + string[1] + ')\s(?:[0-9]{1,3}\.){3}[0-9]{1,3}\\b')
                    match1 = re.search(pattern1, line0)
                    if match1:
                        found = True
                        string1 = match1.group() + '\n'
                        string1 = string1.split()
                        if string1[-3] == 'host':
                            ipa = str(string[1] + '/255.255.255.255')
                            objectRef[lookupObjId - 1].addto(ipa)
                            break
                        else:
                            ipa = str(string[1] + '/' + string1[-1])
                            objectRef[lookupObjId - 1].addto(ipa)
                            break
            if found is False:
                ipa = str(string[1] + '/255.255.255.255')
                objectRef[lookupObjId - 1].addto(ipa)
        nameObjCount = lookupObjId


### ADD member 'group-objects' OBJECTS to SEARCHLIST
for line in lines:
    pattern = '^(\040)(group\-object\s)(.*)$'
    match = re.search(pattern, line)
    if match:
        string = match.group() + '\n'
        string = string.split()
        if string[1] not in searchObjList:
            searchObjList.append(string[1])


### ADD member 'network-object object' OBJECTS to SEARCHLIST
for line in lines:
    pattern = '^(\040)(network\-object\sobject)(.*)$'
    match = re.search(pattern, line)
    if match:
        string = match.group() + '\n'
        string = string.split()
        if string[2] not in searchObjList:
            searchObjList.append(string[2])


#             LOOKUP THE LIST TWICE TO APPEND TO MEMBERS:
#               - MEMBERS OF MAIN MEMBERS
#               - MEMBERS FROM GROUP OBJECTS

for lookupLevel in range(0,2):
    lookupObjId = nameObjCount
    for line in lines:
        pattern = '^(object\-group\snetwork\s)(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            if lookupLevel == 0:
                objectRef.append(ObjectData(2, string[2]))

        pattern = '^(object\snetwork\s)(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            if lookupLevel == 0:
                objectRef.append(ObjectData(3, string[2]))

        pattern = '^(object\-group\sservice\s)(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            if lookupLevel == 0:
                objectRef.append(ObjectData(4, string[2]))
                if len(string) > 4:
                    objectRef.serviceType = string[4]

        if lookupLevel == 0:
            pattern = '^(\040)(network\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                if string[1] == 'host':
                    ipa = str(string[2]+ '/' + '255.255.255.255')
                    objectRef[lookupObjId - 1].addto(ipa)
                else:
                    if string[1] != 'object':
                        ipa = str(string[1]+ '/' + string[2])
                        objectRef[lookupObjId - 1].addto(ipa)

            pattern = '^(\040)(subnet\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                ipa = str(string[1]+ '/' + string[2])
                objectRef[lookupObjId - 1].addto(ipa)

            pattern = '^(\040)(host\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                ipa = str(string[1] + '/' + '255.255.255.255')
                objectRef[lookupObjId - 1].addto(ipa)

            pattern = '^(\040)(port\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                po = '-'.join(string)
                objectRef[lookupObjId - 1].addto(po)

            pattern = '^(\040)(service\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                po = '-'.join(string)
                objectRef[lookupObjId - 1].addto(po)

        if lookupLevel > 0:
            if runOnceSearchFill > 0:
                for i in range(0, len(objectRef)):
                    for j in range(0, len(searchObjList)):
                        if searchObjList[j] == objectRef[i].objName:
                            searchObjRef.append(ObjectData(objectRef[i].objType, objectRef[i].objName))
                            searchObjRef[-1].contents = objectRef[i].contents
                runOnceSearchFill = 0

            pattern = '^(\040)(group\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[1]:
                        objectRef[lookupObjId - 1].contents += searchObjRef[i].contents
                        break

            pattern = '^(\040)(network\-object\sobject)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[2]:
                        objectRef[lookupObjId - 1].contents += searchObjRef[i].contents
                        break


# OUTPUT TO CSV FILE
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for i in range(0, len(objectRef)):
        listset = set(objectRef[i].contents)
        objectRef[i].contents = list(listset)
        objectRef[i].contents.sort()
        outputlist.append((objectRef[i].objName,objectRef[i]))
    writer.writerows(outputlist)
