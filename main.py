'''
The purpose of the this code is to parse the daily Current Inventory Report XML
file posted to reginfo.gov. The code will download and save a version of the 
XML file and produce a fully parsed out csv file to the file locations 
identified in the code. 
'''


from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import datetime
import sys 
import os


'''
Enter the full file location for where the downloaded raw xml file should be 
saved in the linkFolder variable. From there the file will be printed in CSV 
form to that location. NOTE: Do not remove the 'r' in front of the quotations. 
Only change the text in between the quotes
'''

linkFolder = r'/Users/scottbchrist/Desktop/GitHub/rocis/rocis_data'

'''
Enter the full file location for where the file should be saved in the 
saveLink variable.
From there the file will be printed in CSV form to that location. 
NOTE: Do not remove the 'r' in front of the quotations. Only change
the text in between the quotes. 
'''
saveLink = r'/Users/scottbchrist/Desktop/GitHub/rocis/rocis_data'

'''
The code below will download the current inventory report from reginfo.gov and 
save the file at the desired path. Users will be notified when the download is 
complete. 
'''

r = requests.get(r'https://www.reginfo.gov/public/do/PRAXML?type=inventory',\
    stream = True)
print(r.json())

filePath = os.path.join(linkFolder, 'CurrentInventoryReport - %s.xml'\
     % datetime.date.today().strftime("%d%m%Y"))

with open(filePath, 'wb') as f:
    for chunk in r.iter_content(chunk_size=128):
        f.write(chunk)
    f.close()
    print('Currenty Inventory Download Complete.')

'''
The code below will open the saved XML and read it in to begin parsing. 
'''

with open(filePath, encoding='utf-8') as fd:
    doc = fd.read()

'''
The Beautiful Soup code below is used to parse the xml file and get to the 
correct level in the file to pull out the desired data. 
'''

soup = BeautifulSoup("data.xml", 'xml')

z = soup.find_all('InformationCollectionRequest')

'''
The lists below identify the fields the code will pull from each level of the 
downloaded XML file. 
NOTE: If you would like to add fields to the report, please do so at
the appropriate level in the lists below. 
'''

#Fields that need to be found on the collection request level. 
requestLevFields = [
    'OMBControlNumber',
    'ICRReferenceNumber',
    'AgencyCode',
    'Title',
    'ICRTypeCode',
    'PIIFlag',
    'PrivacyActStatementFlag',
    'EO13771Designation',
]

#Fields that need to be found on the collection level. 
incoFields = [
    'Title',
    'StandardFormIndicator',
    'ObligationCode'
]

#Fields that need to be found on the instrument level of a collection 
instlevFields = [
    'AvailableElectronically',
    'ElectronicCapability',
    'CanSubmittedElectronically',
    'FormName',
    'FormNumber'
    
]


'''
The function below is used to pull the contents out of a tag in the downloaded
XML file. Block.find produces a list of the contents and should only contain 
one item. If more than one item is present, there is an issue in the file, and 
the code stops and errors out printing the message "Error: More than 1 item in
field list".  

This function will be used to pull the contents from each of the fields entered 
in the field lists above. If the function cannot find the tag in the 
specificied xml block, the function returns a null.  
 
'''


def findTag(block, field):
    if block.find(field):
        if len(block.find(field).contents) > 1:
            print("Error: More than 1 item in field list") 
            sys.exit(1)
        else:
            holder = block.find(field).contents[0]
    else:
        holder = np.nan
    return holder 
       
'''
The code below goes through every collection request in the file, searches for 
and pulls the data from every information collection present in the collection 
request block, and finally searches for and pulls the data from each instrument 
present in each information collection block. If any of these levels are 
missing, nulls are entered in their corresponding fields.

All information requests listed in the XML are parsed into the final file.
If no information collection and/or instrument is listed, null values are
entered for the fields that would have been pulled from the missing levels. 

The final fullinst variable will be a list of lists that can be transformed 
into a pandas dataframe in a later step. 
'''

fullinst = []

for k,i in enumerate(z):
    
    requestLev = []
    instLev = []
    for j in requestLevFields:
        holdField = findTag(i, j)
        requestLev.append(holdField)
    
    if i.find('InformationCollection'):
        for inco in i.find_all('InformationCollection'):
            requestLev2 = [x for x in requestLev]
            for incoField in incoFields:
                holdTitle = findTag(inco, incoField)
                requestLev2.append(holdTitle)
            
            if inco.find('Instrument'):
                for inst in inco.find_all('Instrument'):

                    instLev = [x for x in requestLev2]

                    for m in instlevFields:
                        holdInstField = findTag(inst, m)
                        instLev.append(holdInstField)

                    fullinst.append(instLev)


            else:
                instLev = [x for x in requestLev2]
                for m in instlevFields:
                    instLev.append(np.nan)

                fullinst.append(instLev)
    else: 
        instLev = [x for x in requestLev]
        instLev.append("Information Collection Not Listed")
        for m in instlevFields:
            instLev.append(np.nan)
        fullinst.append(instLev)


'''
If any field names are added to or removed from the section field lists, they 
must be added to or removed from the list of column names for the printed out 
file. Field names are unique to the block level of the xml file but not to the 
XML as a whole. Therefore, adding more detailed column names may be needed. 
'''


columns = ['OMBControlNumber',
    'ICRReferenceNumber',
    'AgencyCode',
    'Collection Request Title',
    'ICRTypeCode',
    'PIIFlag',
    'PrivacyActStatementFlag',
    'EO13771Designation',
    'Collection Title',
    'CollectionStandardFormIndicator',
    'CollectionObligationCode',
    'AvailableElectronically',
    'ElectronicCapability',
    'CanSubmittedElectronically',
    'FormName',
    'FormNumber'   
          ]

#This will generate the dataframe to print to CSV. 

fullPrint = pd.DataFrame(fullinst,columns=columns) 


'''
The code below is used to print out some quick information about the
details of the file. It then prints how many unique collections, collection 
requests, and instruments are contained in the file.
'''

fullPrintQA = pd.DataFrame(fullinst,columns=columns) 
fullPrintQA['CollTitleICR'] = fullPrintQA['ICRReferenceNumber']\
    + fullPrintQA['Collection Title'] 
fullPrintQA['InstrumentFlag'] = np.where(\
    fullPrintQA['AvailableElectronically'].isnull() &\
    fullPrintQA['ElectronicCapability'].isnull() &\
    fullPrintQA['CanSubmittedElectronically'].isnull() &\
    fullPrintQA['FormName'].isnull() &\
    fullPrintQA['FormNumber'].isnull() , 0, 1)


#QA

tempCollTitle = len(set(fullPrintQA['CollTitleICR']))
tempICR = len(set(fullPrintQA['ICRReferenceNumber']))
tempinstrument = fullPrintQA['InstrumentFlag'].sum()

print('Collection Count: %d' % tempCollTitle)
print('Collection Reqest Count: %d' % tempICR)
print('Unique Instrument Count: %d' % tempinstrument)


'''
The code below uses the saveLink variable established at the beginning of the
code and saves the generated dataframe as a csv. 
'''

savePath = os.path.join(saveLink, 'CurrentInventoryReport - %s.csv'\
    % datetime.date.today().strftime("%d%m%Y"))

fullPrint.to_csv(savePath, index=False)