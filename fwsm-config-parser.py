
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
            self.objTypename = 'object-group service'
        self.contents = []

    def append(self,input):
        self.contents.append(input)

    def __repr__(self):
        return "TypeID:: {}, TypeName :: {}, Name :: {} and contains:::".format(self.objType, self.objTypename, self.objName)

    def __str__(self):
        return "{}".format('"'.join(self.contents))


fileName = '/tmp/test.config'
csvfile = '/tmp/test.csv'
fileContents = []
objectRef = []
searchObjRef = []
searchObjList = []
lookupLevel = 0
lookupObjId = 0
objectCount = 0
outputlist = []
tmplookupObjId = 0
fwVersion = 'low'


### OPEN FILE TO READ LINES TO LIST
with open(fileName, 'r') as f:
   lines = f.readlines()
   f.close()


### FIND VERSION FROM CONFIG FILE
for line in lines:
    pattern = '(.*)Version(\s)(.*)[.].*(\<context>)'
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
    break


### ADD member 'name' OBJECTS to SEARCHLIST
if fwVersion == 'low':
    for line in lines:
        pattern = '^name(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            objectRef.append(ObjectData(1, string[2]))
            objectRef[lookupObjId - 1].append(string[1])
    tmplookupObjId = lookupObjId


### ADD member 'group-objects' OBJECTS to SEARCHLIST
for line in lines:
    pattern = '^(\040)(group\-object\s)(.*)$'
    match = re.search(pattern, line)
    if match:
        string = match.group() + '\n'
        string = string.split()
        while string[1] not in searchObjList:
            searchObjRef.append(ObjectData(0, string[1]))
            searchObjList.append(string[1])


### ADD member 'network-object object' OBJECTS to SEARCHLIST
for line in lines:
    pattern = '^(\040)(network\-object\sobject)(.*)$'
    match = re.search(pattern, line)
    if match:
        string = match.group() + '\n'
        string = string.split()
        while string[2] not in searchObjList:
            searchObjRef.append(ObjectData(0, string[2]))
            searchObjList.append(string[2])


#             LOOKUP THE LIST TWICE TO APPEND TO MEMBERS:
#               - MEMBERS OF MAIN MEMBERS
#               - MEMBERS FROM GROUP OBJECTS

for lookupLevel in range(0,2):
    lookupObjId = tmplookupObjId
    for line in lines:
        pattern = '^(object\-group\snetwork\s)(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            if lookupLevel == 0:
                objectRef.append(ObjectData(2, string[2]))
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[2]:
                        objectRef[lookupObjId-1].objType += 10
                        searchObjRef[i] = objectRef[lookupObjId-1]
                        break


        pattern = '^(object\snetwork\s)(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            if lookupLevel == 0:
                objectRef.append(ObjectData(3, string[2]))
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[2]:
                        objectRef[lookupObjId-1].objType += 10
                        searchObjRef[i] = objectRef[lookupObjId-1]
                        print(searchObjRef[i])
                        break

        pattern = '^(object\-group\sservice\s)(.*)$'
        match = re.search(pattern, line)
        if match:
            lookupObjId += 1
            string = match.group() + '\n'
            string = string.split()
            if lookupLevel == 0:
                objectRef.append(ObjectData(3, string[2]))
                if len(string) > 4:
                    objectRef.serviceType = string[4]
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[2]:
                        objectRef[lookupObjId-1].objType += 10
                        searchObjRef[i] = objectRef[lookupObjId-1]
                        break


        if lookupLevel == 0:
            pattern = '^(\040)(network\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                if string[1] == 'host':
                    ipa = str(string[2]+ '/' + '255.255.255.255')
                    objectRef[lookupObjId - 1].append(ipa)
                else:
                    if string[1] != 'object':
                        ipa = str(string[1]+ '/' + string[2])
                        objectRef[lookupObjId - 1].append(ipa)

            pattern = '^(\040)(subnet\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                ipa = str(string[1]+ '/' + string[2])
                objectRef[lookupObjId - 1].append(ipa)

            pattern = '^(\040)(host\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                ipa = str(string[1] + '/' + '255.255.255.255')
                objectRef[lookupObjId - 1].append(ipa)

            pattern = '^(\040)(port\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                po = '-'.join(string)
                objectRef[lookupObjId - 1].append(po)

            pattern = '^(\040)(service\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                po = '-'.join(string)
                objectRef[lookupObjId - 1].append(po)


        if lookupLevel > 0:
            pattern = '^(\040)(group\-object\s)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[1]:
                        objectRef[lookupObjId - 1].contents += searchObjRef[i].contents
                        searchObjRef[i] = objectRef[lookupObjId - 1]
                        break

            pattern = '^(\040)(network\-object\sobject)(.*)$'
            match = re.search(pattern, line)
            if match:
                string = match.group() + '\n'
                string = string.split()
                for i in range(0, len(searchObjRef)):
                    if searchObjRef[i].objName == string[2]:
                        print('objectRef',objectRef[lookupObjId - 1].contents)
                        print('searchRef',searchObjRef[i].contents)
                        objectRef[lookupObjId - 1].contents += searchObjRef[i].contents
                        searchObjRef[i] = objectRef[lookupObjId - 1]
                        break


# OUTPUT TO CSV FILE
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for i in range(0, len(objectRef)):
        objectRef[i].contents.sort()
        outputlist.append((objectRef[i].objName,objectRef[i]))
    writer.writerows(outputlist)
