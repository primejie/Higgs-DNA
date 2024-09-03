import json
import sys
import os
import multiprocessing
import re
with open('metadata/samples/Data_UL.json','r') as f:
    # data_lines=f.readlines()
    data=json.load(f)
with open('metadata/samples/Data_UL.json','r') as f:
    data_lines=f.readlines()
data18=data["Data"]["files"]["2018"]
# print(data_lines)
for i in data18:
    # print(i)
    if 'zhjie' not in i:
        # print(i)
        rootfile=i.split('/')[-1]
        for j,dataline in enumerate(data_lines):
            # print("5")
            if i in dataline:
                # print(dataline)
               
                # print(j)
                # print(dataline)
                start=dataline.index("root:")
                end=dataline.index(".root")
                result=dataline[start:end+5]
                print(result)
                data_lines[j]=re.sub(result,'/eos/cms/store/group/phys_higgs/cmshgg/zhjie/'+rootfile,dataline)
                # data_lines[j]=f"{dataline[:dataline.index('root:')]}{data_lines[j]}"
                # data_lines[j]=dataline.replace(dataline,'/eos/cms/store/group/phys_higgs/cmshgg/zhjie/'+rootfile)
        # os.system( 'xrdcp ' + i + ' ' + '/eos/cms/store/group/phys_higgs/cmshgg/zhjie/' )
with open("/afs/cern.ch/user/z/zhjie/HiggsDNA/metadata/samples/Data_UL.json",'w') as f:
    f.writelines(data_lines)