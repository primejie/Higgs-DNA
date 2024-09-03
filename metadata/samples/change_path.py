import json

with open ("signal.json") as f:
    data = json.load(f)
for name in data.keys():
    try:
        rootname=data[name]["files"]["2016postVFP"]
        i=0
        for root in rootname:
            rename=root.split("/")[-1].split(".")[0]
            rename="/eos/cms/store/group/phys_higgs/cmshgg/zhjie/signal_out/2016postVFP/"+name+"/"+rename+"_Skim.root"

            data[name]["files"]["2016postVFP"][i]=rename
            i=i+1
    except KeyError:
        print("none")
with open('signal.json', 'w') as file:
    json.dump(data, file, indent=4)
