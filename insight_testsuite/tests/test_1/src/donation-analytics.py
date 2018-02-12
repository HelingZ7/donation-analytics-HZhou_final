def load_one_record(itcont_onerecord):
# load one record, check the content and assign the values of five fields of interest.
# itcont_onerecord contains one record only.
    itcont_onerecord=itcont_onerecord[0].split('|') 
    valid_record_flag=1
    CMTE_ID=itcont_onerecord[0]
    Name=itcont_onerecord[7]
    ZipCode=itcont_onerecord[10]
    Transaction_DT=itcont_onerecord[13]
    Trandaction_AMT=itcont_onerecord[14]
    Other_ID=itcont_onerecord[15]
    if not Name or not ZipCode or not Transaction_DT or not Trandaction_AMT or Other_ID or len(CMTE_ID)!=9 or len(ZipCode)<5:
        valid_record_flag=0
    else:
        ZipCode=ZipCode[0:5]
        Transaction_DT=Transaction_DT[4:8] # only year is used
        Trandaction_AMT=float(Trandaction_AMT)
    itcont_onerecord_selected=[CMTE_ID,Name,ZipCode,Transaction_DT,Trandaction_AMT]
    return valid_record_flag,itcont_onerecord_selected

class Record_Table:
    def __init__(self,CMTE_ID,ZipCode,Transaction_DT,Trandaction_AMT):
        self.CMTE_ID=CMTE_ID
        self.ZipCode=ZipCode
        self.Transaction_DT=Transaction_DT
        self.Trandaction_AMT=Trandaction_AMT
    def add_to_Table(self,itcont_selected_onerecord):
        self.CMTE_ID.append(itcont_selected_onerecord[0])
        self.ZipCode.append(itcont_selected_onerecord[2])
        self.Transaction_DT.append(itcont_selected_onerecord[3])
        self.Trandaction_AMT.append(itcont_selected_onerecord[4])

def indices_one_field(lst, element):
    # return indices all the records with the same field value as the last record
    result = []
    offset = -1
    while True:
        try:
            offset = lst.index(element, offset+1)
        except ValueError:
            return result
        result.append(offset)
  
def indices_all_fields(Record_Table):
# return indices all the records with the same CMTE_ID, zipcode and year of the last record
    indices_CMTE_ID=indices_one_field(Record_Table.CMTE_ID,Record_Table.CMTE_ID[-1])
    indices_zipcode=indices_one_field(Record_Table.ZipCode,Record_Table.ZipCode[-1])
    indices_year=indices_one_field(Record_Table.Transaction_DT,Record_Table.Transaction_DT[-1])
    indices=list(set(indices_CMTE_ID).intersection(indices_zipcode).intersection(indices_year))
    return indices

###### main function######
import numpy as np
import os
cwd = os.getcwd()
# Load input
f_prctile=open(cwd[:-3]+'input/percentile.txt', 'r')
input_percentile=f_prctile.read()
f_prctile.close()
with open(cwd[:-3]+'input/itcont.txt', 'r') as f_itcont:
    input_itcont = f_itcont.readlines()

# initialize lookuptable (LUT) for ZipCode and Name
ZipCode_LUT=[]
Name_LUT=[]
Record_ID_LUT=[]
itcont_selected=[]
RepeatDonor_Record_Table=Record_Table([],[],[],[])
# checking each record and identify repeat donors
i=0
for line in input_itcont:
    itcont_onerecord = line.split('\n')
    (valid_record_flag,itcont_onerecord_selected)=load_one_record(itcont_onerecord)
    #itcont_onerecord_selected=[CMTE_ID,Name,ZipCode,Transaction_DT,Trandaction_AMT]
    if valid_record_flag: #proceed if the record is valid
        itcont_selected.append(itcont_onerecord_selected)
        if not itcont_onerecord_selected[2] in ZipCode_LUT: # the first time this zipcode appears. add ZipCode and Name to LUT. update Record_ID_LUT.
            ZipCode_LUT.append(itcont_onerecord_selected[2])
            Name_LUT.append([itcont_onerecord_selected[1]])
            Record_ID_LUT.append([[i]])
        else: #ZipCode exists
            ZipCode_idx = ZipCode_LUT.index(itcont_onerecord_selected[2]) 
            if not itcont_onerecord_selected[1] in Name_LUT[ZipCode_idx]: # % the first time this name appears (in existing zipcode) Add Name to LUT. update Record_ID_LUT.
                Name_LUT[ZipCode_idx].append(itcont_onerecord_selected[1])
                Record_ID_LUT[ZipCode_idx].append([i])
            else: # Repeat Donor; update Record_ID_LUT. identify record with match CMTE_ID, year and zipcode
                Name_idx = Name_LUT[ZipCode_idx].index(itcont_onerecord_selected[1])
                Record_ID_LUT[ZipCode_idx][Name_idx].append(i)
                if len(Record_ID_LUT[ZipCode_idx][Name_idx])==2: #first time identified repeat donor. add previous record to repeat donor record
                    RepeatDonor_Record_Table.add_to_Table(itcont_selected[Record_ID_LUT[ZipCode_idx][Name_idx][0]])
                RepeatDonor_Record_Table.add_to_Table(itcont_selected[i]) #add current record
                record_idx = indices_all_fields(RepeatDonor_Record_Table)
                contributions_record_idx=list(RepeatDonor_Record_Table.Trandaction_AMT[c] for c in record_idx)
                prctile_contribution=str(round(np.percentile(contributions_record_idx,input_percentile,interpolation='nearest')))
                total_contribution=str(sum(contributions_record_idx))
                num_of_contribution=str(len(record_idx))
                output=[RepeatDonor_Record_Table.CMTE_ID[-1],'|',RepeatDonor_Record_Table.ZipCode[-1],'|',RepeatDonor_Record_Table.Transaction_DT[-1],
                        '|',prctile_contribution,'|',total_contribution,'|',num_of_contribution,'\n']
                f_output=open(cwd[:-3]+'output/repeat_donor.txt', 'a') 
                f_output.writelines(output)
                f_output.close()          
        i=i+1 
    
    
    




