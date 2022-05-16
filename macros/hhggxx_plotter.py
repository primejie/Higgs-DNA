#!/bin/env python

import awkward
import matplotlib.pyplot as plt
import numpy as np

inputdir = {}
inputdir["no_cuts"] =   "/afs/cern.ch/user/f/fmonti/work/HiggsDNA/HiggsDNA/smallproduction_5APR2022_noselections_extraphotonvariables/"
inputdir["photon_cuts_only"] =   "/afs/cern.ch/user/f/fmonti/work/HiggsDNA/HiggsDNA/smallproduction_26APR2022_noselections_extraphotonvariables/"
inputdir["selected"] = "/afs/cern.ch/user/f/fmonti/work/HiggsDNA/HiggsDNA/smallproduction_14MAR2022/"
samples = {
    1000:"GluGluToBulkGravitonToHHTo2B2G_M1000_2017/merged_nominal.parquet",
    1250:"GluGluToBulkGravitonToHHTo2B2G_M1250_2017/merged_nominal.parquet",
#    1500:"GluGluToBulkGravitonToHHTo2B2G_M1500_2017/merged_nominal.parquet",
    1750:"GluGluToBulkGravitonToHHTo2B2G_M1750_2017/merged_nominal.parquet",
    2000:"GluGluToBulkGravitonToHHTo2B2G_M2000_2017/merged_nominal.parquet",
    2500:"GluGluToBulkGravitonToHHTo2B2G_M2500_2017/merged_nominal.parquet",
    3000:"GluGluToBulkGravitonToHHTo2B2G_M3000_2017/merged_nominal.parquet"
}

#load input files and compute yields
events = {}
yields = {}
for MX,sample in samples.items():
    print("Loading sample",sample)
    events[MX] = {}
    yields[MX] = {}
    for ftype in ["no_cuts","photon_cuts_only","selected"]:
        print("    Type",ftype)
        events[MX][ftype] = awkward.from_parquet(inputdir[ftype]+"/"+sample)
        yields[MX][ftype] = awkward.sum(events[MX][ftype].weight_central)
        print("    Yield:",yields[MX][ftype],", N=",len(events[MX][ftype]))
        if ftype=="no_cuts":
            selection = (events[MX][ftype].photon_1_eta!=-999) & (events[MX][ftype].photon_2_eta!=-999)
            yields[MX]["at_least_two_photons"] = awkward.sum(events[MX][ftype].weight_central[selection])
            print("    Type at_least_two_photons")
            print("    Yield:",yields[MX]["at_least_two_photons"])
        if ftype=="photon_cuts_only":
            selection = events[MX][ftype].hhggxx_photonIDcut
            yields[MX]["photon_and_ID_cuts"] = awkward.sum(events[MX][ftype].weight_central[selection])
            print("    Type photon_and_ID_cuts")
            print("    Yield:",yields[MX]["photon_and_ID_cuts"],", N=",len(events[MX][ftype].weight_central[selection]))

#plot photon selection efficiency vs MX
MXs = events.keys()
atleasttwophoton_eff = [ yields[MX]["at_least_two_photons"]/yields[MX]["no_cuts"] for MX in MXs ]
photon_eff = [ yields[MX]["photon_cuts_only"]/yields[MX]["no_cuts"] for MX in MXs ]
photonID_eff = [ yields[MX]["photon_and_ID_cuts"]/yields[MX]["no_cuts"] for MX in MXs ]
fatjet_eff = [ yields[MX]["selected"]/yields[MX]["no_cuts"] for MX in MXs ]
plt.plot(events.keys(), atleasttwophoton_eff, marker='.', linestyle='-', label='>=2 reco photons')
plt.plot(events.keys(), photon_eff, marker='.', linestyle='-', label='diphoton selections')
plt.plot(events.keys(), photonID_eff, marker='.', linestyle='-', label='photon ID > -0.7')
plt.plot(events.keys(), fatjet_eff, marker='.', linestyle='-', label='At least 1 fat jet')
plt.legend()
#plt.show()
plt.savefig('plots/efficiencies.png')
plt.clf()

'''
#for event in events[3000]["selected"]:
#    print(" lead gen phi = ",event.LeadPhoton_phi, 
#          " lead reco phi = ",event.GenHggLeadPhoton_phi,
#          " diff = ",event.LeadPhoton_phi-event.GenHggLeadPhoton_phi)
#    print(" lead gen eta = ",event.LeadPhoton_eta, 
#          " lead reco eta = ",event.GenHggLeadPhoton_eta,
#          " diff = ",event.LeadPhoton_eta-event.GenHggLeadPhoton_eta)
#    print(" sublead gen phi = ",event.SubleadPhoton_phi, 
#          " sublead reco phi = ",event.GenHggSubleadPhoton_phi,
#          " diff = ",event.SubleadPhoton_phi-event.GenHggSubleadPhoton_phi)
#    print(" sublead gen eta = ",event.SubleadPhoton_eta, 
#          " sublead reco eta = ",event.GenHggSubleadPhoton_eta,
#          " diff = ",event.SubleadPhoton_eta-event.GenHggSubleadPhoton_eta)
#    print()

#plot deltaR reco-gen of lead and sublead photons
for MX in MXs:
    plt.hist(x=events[MX]["selected"].deltaRLeadPhotonfromGen, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,0.01,0.0002),
             alpha=0.4,
             label='lead photon')
    plt.hist(x=events[MX]["selected"].deltaRSubleadPhotonfromGen, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,0.01,0.0002),
             alpha=0.4,
             label='sublead photon')
    plt.legend()
    plt.savefig('plots/deltaRgenrecophoton_M%i.png'%MX)
    plt.clf()

#plot deltaR between lead and sublead photons at gen and at reco level
for MX in MXs:
    plt.hist(x=events[MX]["selected"].Diphoton_dR, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,2.,0.05),
             alpha=0.4,
             label='reco')
    plt.hist(x=events[MX]["selected"].GenHggHiggs_dR, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,2.,0.05),
             alpha=0.4,
             label='gen')
    plt.legend()
    plt.savefig('plots/deltaRleadsublead_genandrecophoton_M%i.png'%MX)
    plt.clf()

#plot deltaR between lead and sublead photons at gen level, for all events vs only preselected events
for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].GenHggHiggs_dR, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,2.,0.05),
             alpha=0.4,
             label='before photon selections')
    plt.hist(x=events[MX]["photon_cuts_only"].GenHggHiggs_dR, 
             weights=events[MX]["photon_cuts_only"].weight_central, 
             bins=np.arange(0.,2.,0.05),
             alpha=0.4,
             label='after photon selections')
    plt.legend()
    plt.savefig('plots/deltaRgenleadsublead_beforevsafterselections_M%i.png'%MX)
    plt.clf()

#plot deltaR between Hbb candidate and fatjet
for MX in MXs:
    plt.hist(x=events[MX]["selected"].deltaRFatHbbJetGenOtherHiggs, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,2.,0.05),
             alpha=0.4)
    plt.savefig('plots/deltaRFatHbbJetGenOtherHiggs_M%i.png'%MX)
    plt.clf()

#plot distribution of particle net scores
for MX in MXs:
    plt.hist(x=events[MX]["selected"].fathbbjet_deepTagMD_HbbvsQCD, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,1.,0.02),
             alpha=0.4,
             label="deepTagMD_HbbvsQCD")
    plt.hist(x=events[MX]["selected"].fathbbjet_deepTagMD_H4qvsQCD, 
             weights=events[MX]["selected"].weight_central, 
             bins=np.arange(0.,1.,0.02),
             alpha=0.4,
             label="deepTagMD_H4qvsQCD")
    plt.legend()
    plt.savefig('plots/fathbbjet_particlenetscores_M%i.png'%MX)
    plt.clf()

    selection = (events[MX]["selected"].n_fatjets>0)
    plt.scatter(x=events[MX]["selected"].fathbbjet_deepTagMD_HbbvsQCD[selection],
                y=events[MX]["selected"].fathbbjet_deepTagMD_H4qvsQCD[selection])
    plt.xlabel('deepTagMD_HbbvsQCD')
    plt.ylabel('deepTagMD_H4qvsQCD')
    plt.savefig('plots/fathbbjet_particlenetscores_scatter_M%i.png'%MX)
    plt.clf()

####################################################    
#plot R9 of lead and sublead photons
for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].LeadPhoton_r9, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,1.,0.02),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.axvline(x=0.8)
plt.legend()
plt.xlabel('lead photon R9')
plt.savefig('plots/leadphotonR9.png')
plt.clf()

for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].SubleadPhoton_r9, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,1.,0.02),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.axvline(x=0.8)
plt.legend()
plt.xlabel('sublead photon R9')
plt.savefig('plots/subleadphotonR9.png')
plt.clf()

####################################################    
#plot variables used for isolation for lead photon
for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].LeadPhoton_pfRelIso03_chg * events[MX]["no_cuts"].LeadPhoton_pt, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,100.,1.),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.axvline(x=20.0)
plt.legend()
plt.xlabel('lead photon pfRelIso03_chg*pt')
plt.savefig('plots/leadphoton_isoXpt.png')
plt.clf()

for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].LeadPhoton_pfRelIso03_chg, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,2.,0.02),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.axvline(x=0.3)
plt.legend()
plt.xlabel('lead photon pfRelIso03_chg')
plt.savefig('plots/leadphoton_iso.png')
plt.clf()

####################################################    
#plot variables used for isolation for sublead photon
for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].SubleadPhoton_pfRelIso03_chg * events[MX]["no_cuts"].SubleadPhoton_pt, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,100.,1.),
             alpha=0.4,
             label='MX=%.0f'%MX)

plt.yscale("log")
plt.axvline(x=20.0)
plt.legend()
plt.xlabel('sublead photon pfRelIso03_chg*pt')
plt.savefig('plots/subleadphoton_isoXpt.png')
plt.clf()

for MX in MXs:
    plt.hist(x=events[MX]["no_cuts"].SubleadPhoton_pfRelIso03_chg, 
             weights=events[MX]["no_cuts"].weight_central, 
             bins=np.arange(0.,2.,0.02),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.axvline(x=0.3)
plt.legend()
plt.xlabel('sublead photon pfRelIso03_chg')
plt.savefig('plots/subleadphoton_iso.png')
plt.clf()

#################################################
# plot fraction of photons which are photons_eb_high_r9
frac_leadph_eb_high_r9 = {}
frac_subleadph_eb_high_r9 = {}
frac_leadph_eb_low_r9 = {}
frac_subleadph_eb_low_r9 = {}
frac_leadph_eb_low_r9_selected = {}
frac_subleadph_eb_low_r9_selected = {}
frac_leadph_ee_high_r9 = {}
frac_subleadph_ee_high_r9 = {}
for MX in MXs:
    leadph_eb_high_r9 = events[MX]["no_cuts"].LeadPhoton_isScEtaEB & (events[MX]["no_cuts"].LeadPhoton_r9 > 0.85)
    subleadph_eb_high_r9 = events[MX]["no_cuts"].SubleadPhoton_isScEtaEB & \
                           (events[MX]["no_cuts"].SubleadPhoton_r9 > 0.85)
    leadph_ee_high_r9 = events[MX]["no_cuts"].LeadPhoton_isScEtaEE & \
                        (events[MX]["no_cuts"].LeadPhoton_r9 > 0.9)
    subleadph_ee_high_r9 = events[MX]["no_cuts"].SubleadPhoton_isScEtaEE & \
                           (events[MX]["no_cuts"].SubleadPhoton_r9 > 0.9)

    leadph_eb_low_r9 = events[MX]["no_cuts"].LeadPhoton_isScEtaEB & \
                       (events[MX]["no_cuts"].LeadPhoton_r9 > 0.5) & \
                       (events[MX]["no_cuts"].LeadPhoton_r9 < 0.85)
    subleadph_eb_low_r9 = events[MX]["no_cuts"].SubleadPhoton_isScEtaEB & \
                          (events[MX]["no_cuts"].SubleadPhoton_r9 > 0.5) & \
                          (events[MX]["no_cuts"].SubleadPhoton_r9 < 0.85)
    leadph_eb_low_r9_selected = leadph_eb_low_r9 & (
        (events[MX]["no_cuts"].LeadPhoton_pfRelIso03_all * events[MX]["no_cuts"].LeadPhoton_pt * 0.16544) < 4.0)
    subleadph_eb_low_r9_selected = subleadph_eb_low_r9 & (
        (events[MX]["no_cuts"].SubleadPhoton_pfRelIso03_all * events[MX]["no_cuts"].SubleadPhoton_pt * 0.16544) < 4.0)


    frac_leadph_eb_high_r9[MX] = awkward.sum(events[MX]["no_cuts"].weight_central[leadph_eb_high_r9])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_eb_high_r9[MX] = awkward.sum(events[MX]["no_cuts"].weight_central[subleadph_eb_high_r9])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_leadph_ee_high_r9[MX] = awkward.sum(events[MX]["no_cuts"].weight_central[leadph_ee_high_r9])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_ee_high_r9[MX] = awkward.sum(events[MX]["no_cuts"].weight_central[subleadph_ee_high_r9])/awkward.sum(events[MX]["no_cuts"].weight_central)

    frac_leadph_eb_low_r9[MX] = awkward.sum(events[MX]["no_cuts"].weight_central[leadph_eb_low_r9])/ \
                                awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_eb_low_r9[MX] = awkward.sum(events[MX]["no_cuts"].weight_central[subleadph_eb_low_r9])/ \
                                   awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_leadph_eb_low_r9_selected[MX] =awkward.sum( 
        events[MX]["no_cuts"].weight_central[leadph_eb_low_r9_selected])/ \
        awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_eb_low_r9_selected[MX] = awkward.sum(
        events[MX]["no_cuts"].weight_central[subleadph_eb_low_r9_selected])/ \
        awkward.sum(events[MX]["no_cuts"].weight_central)

    print("MX=",MX)
    print("   frac_leadph_eb_high_r9=",frac_leadph_eb_high_r9[MX])
    print("   frac_leadph_ee_high_r9=",frac_leadph_ee_high_r9[MX])
    print("   frac_leadph_eb_low_r9=",frac_leadph_eb_low_r9[MX])
    print("   frac_leadph_eb_low_r9_selected=",frac_leadph_eb_low_r9_selected[MX])
    print('')
    print("   frac_subleadph_eb_high_r9=",frac_subleadph_eb_high_r9[MX])
    print("   frac_subleadph_ee_high_r9=",frac_subleadph_ee_high_r9[MX])
    print("   frac_subleadph_eb_low_r9=",frac_subleadph_eb_low_r9[MX])
    print("   frac_subleadph_eb_low_r9_selected=",frac_subleadph_eb_low_r9_selected[MX])

plt.plot(frac_leadph_eb_high_r9.keys(), frac_leadph_eb_high_r9.values(), marker='.', linestyle='-', label='lead ph eb_high_r9')
plt.plot(frac_subleadph_eb_high_r9.keys(), frac_subleadph_eb_high_r9.values(), marker='.', linestyle='-', label='sublead ph eb_high_r9')
plt.plot(frac_leadph_eb_low_r9.keys(), frac_leadph_eb_low_r9.values(), marker='.', linestyle='-', label='lead ph eb_low_r9')
plt.plot(frac_subleadph_eb_low_r9.keys(), frac_subleadph_eb_low_r9.values(), marker='.', linestyle='-', label='sublead ph eb_low_r9')
plt.plot(frac_leadph_eb_low_r9_selected.keys(), frac_leadph_eb_low_r9_selected.values(), marker='.', linestyle='-', label='lead ph eb_low_r9_selected')
plt.plot(frac_subleadph_eb_low_r9_selected.keys(), frac_subleadph_eb_low_r9_selected.values(), marker='.', linestyle='-', label='sublead ph eb_low_r9_selected')
plt.plot(frac_leadph_ee_high_r9.keys(), frac_leadph_ee_high_r9.values(), marker='.', linestyle='-', label='lead ph ee_high_r9')
plt.plot(frac_subleadph_ee_high_r9.keys(), frac_subleadph_ee_high_r9.values(), marker='.', linestyle='-', label='sublead ph ee_high_r9')
plt.legend()
plt.xlabel('MX (GeV)')
plt.ylabel('fraction of photons')
plt.savefig('plots/frac_photons_eb_high_r9')
plt.clf()
    
#plot photonID for preselected photons
for MX in MXs:
    plt.hist(x=events[MX]["photon_cuts_only"].LeadPhoton_mvaID, 
             weights=events[MX]["photon_cuts_only"].weight_central, 
             bins=np.arange(-1.,1,0.02),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.axvline(x=-0.7)
plt.legend()
plt.xlabel('lead photon ID')
plt.savefig('plots/leadphotonID.png')
plt.clf()

for MX in MXs:
    plt.hist(x=events[MX]["photon_cuts_only"].SubleadPhoton_mvaID, 
             weights=events[MX]["photon_cuts_only"].weight_central, 
             bins=np.arange(-1.,1,0.02),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.axvline(x=-0.7)
plt.legend()
plt.xlabel('sublead photon ID')
plt.savefig('plots/subleadphotonID.png')
plt.clf()

#plot isolation for preselected photons
for MX in MXs:
    selection = (events[MX]["no_cuts"].photon_1_all_cuts==1) & (events[MX]["no_cuts"].photon_2_all_cuts==1)
    plt.hist(x=events[MX]["no_cuts"].photon_1_pfRelIso03_all[selection]*events[MX]["no_cuts"].photon_1_pt[selection], 
             weights=events[MX]["no_cuts"].weight_central[selection], 
             bins=np.arange(0.,1200.,10),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.legend()
plt.xlabel('lead ph pfRelIso03_all*pt')
plt.savefig('plots/leadphoton_pfRelIso03_all.png')
plt.clf()

for MX in MXs:
    selection = (events[MX]["no_cuts"].photon_1_all_cuts==1) & (events[MX]["no_cuts"].photon_2_all_cuts==1)
    plt.hist(x=events[MX]["no_cuts"].photon_2_pfRelIso03_all[selection]*events[MX]["no_cuts"].photon_2_pt[selection], 
             weights=events[MX]["no_cuts"].weight_central[selection], 
             bins=np.arange(0.,1200.,10),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.legend()
plt.xlabel('sublead ph pfRelIso03_all*pt')
plt.savefig('plots/subleadphoton_pfRelIso03_all.png')
plt.clf()


#plot photon ID vs diphoton pt for preselected photons
plt.hist2d(awkward.flatten([events[MX]["photon_cuts_only"].Diphoton_pt for MX in MXs]),
           awkward.flatten([events[MX]["photon_cuts_only"].LeadPhoton_mvaID for MX in MXs]), 
           weights=awkward.flatten([events[MX]["photon_cuts_only"].weight_central for MX in MXs]), 
           bins=[np.arange(0.,1501.,50), np.arange(-1.,1.01,0.2)])

plt.xlabel('diphoton pt')
plt.ylabel('lead photon ID')
plt.savefig('plots/leadphotonIDvspt.png')
plt.clf()

plt.hist2d(awkward.flatten([events[MX]["photon_cuts_only"].Diphoton_pt for MX in MXs]),
           awkward.flatten([events[MX]["photon_cuts_only"].SubleadPhoton_mvaID for MX in MXs]), 
           weights=awkward.flatten([events[MX]["photon_cuts_only"].weight_central for MX in MXs]), 
           bins=[np.arange(0.,1501.,50), np.arange(-1.,1.01,0.2)])

plt.xlabel('diphoton pt')
plt.ylabel('sublead photon ID')
plt.savefig('plots/subleadphotonIDvspt.png')
plt.clf()
'''

#plot cut based photon selection efficiency vs MX
frac_leadph_MVAIDcut = {}
frac_leadph_cutlooseID = {}
frac_leadph_cutmediumID = {}
frac_leadph_cuttightID = {}
frac_subleadph_MVAIDcut = {}
frac_subleadph_cutlooseID = {}
frac_subleadph_cutmediumID = {}
frac_subleadph_cuttightID = {}
frac_dipho_MVAIDcut = {}
frac_dipho_cutlooseID = {}
frac_dipho_cutmediumID = {}
frac_dipho_cuttightID = {}


for MX in MXs:

    leadph_MVAIDcut = (events[MX]["photon_cuts_only"].LeadPhoton_mvaID>-0.7)
    leadph_cutlooseID = (events[MX]["photon_cuts_only"].LeadPhoton_cutBased>0)
    leadph_cutmediumID = (events[MX]["photon_cuts_only"].LeadPhoton_cutBased>1)
    leadph_cuttightID = (events[MX]["photon_cuts_only"].LeadPhoton_cutBased>2)

    subleadph_MVAIDcut = (events[MX]["photon_cuts_only"].SubleadPhoton_mvaID>-0.7)
    subleadph_cutlooseID = (events[MX]["photon_cuts_only"].SubleadPhoton_cutBased>0)
    subleadph_cutmediumID = (events[MX]["photon_cuts_only"].SubleadPhoton_cutBased>1)
    subleadph_cuttightID = (events[MX]["photon_cuts_only"].SubleadPhoton_cutBased>2)

    dipho_MVAIDcut = (leadph_MVAIDcut & subleadph_MVAIDcut)
    dipho_cutlooseID = (leadph_cutlooseID & subleadph_MVAIDcut)
    dipho_cutmediumID = (leadph_cutmediumID & subleadph_cutmediumID)
    dipho_cuttightID = (leadph_cuttightID & subleadph_cuttightID)

    frac_leadph_MVAIDcut[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[leadph_MVAIDcut])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_leadph_cutlooseID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[leadph_cutlooseID])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_leadph_cutmediumID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[leadph_cutmediumID])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_leadph_cuttightID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[leadph_cuttightID])/awkward.sum(events[MX]["no_cuts"].weight_central)

    frac_subleadph_MVAIDcut[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[subleadph_MVAIDcut])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_cutlooseID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[subleadph_cutlooseID])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_cutmediumID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[subleadph_cutmediumID])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_subleadph_cuttightID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[subleadph_cuttightID])/awkward.sum(events[MX]["no_cuts"].weight_central)

    frac_dipho_MVAIDcut[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[dipho_MVAIDcut])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_dipho_cutlooseID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[dipho_cutlooseID])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_dipho_cutmediumID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[dipho_cutmediumID])/awkward.sum(events[MX]["no_cuts"].weight_central)
    frac_dipho_cuttightID[MX] = awkward.sum(events[MX]["photon_cuts_only"].weight_central[dipho_cuttightID])/awkward.sum(events[MX]["no_cuts"].weight_central)

plt.plot(events.keys(), atleasttwophoton_eff, marker='.', linestyle='-', label='>=2 reco photons')
plt.plot(events.keys(), photon_eff, marker='.', linestyle='-', label='diphoton preselections')
plt.plot(events.keys(), photonID_eff, marker='.', linestyle='-', label='photon ID > -0.7')
plt.plot(frac_dipho_MVAIDcut.keys(), frac_dipho_MVAIDcut.values(), marker='.', linestyle='-', label='MVA ID selection')
plt.plot(frac_dipho_cutlooseID.keys(), frac_dipho_cutlooseID.values(), marker='.', linestyle='-', label='cut based loose')
plt.plot(frac_dipho_cutmediumID.keys(), frac_dipho_cutmediumID.values(), marker='.', linestyle='-', label='cut based medium')
plt.plot(frac_dipho_cuttightID.keys(), frac_dipho_cuttightID.values(), marker='.', linestyle='-', label='cut based tight')
plt.legend()
plt.xlabel('MX (GeV)')
plt.ylabel('efficiency')
plt.savefig('plots/cut_based efficiency')
plt.clf()

#plot shower shape variables for preselected photons
for MX in MXs:
    if not ("000" in MX): continue 
    plt.hist(x=events[MX]["photon_cuts_only"].LeadPhoton_hoe, 
             weights=events[MX]["photon_cuts_only"].weight_central,
             bins=np.arange(0.,0.1,0.002),
             alpha=0.4,
             label='MX=%.0f'%MX)
plt.yscale("log")
plt.legend()
plt.xlabel('lead ph H/E')
plt.savefig('plots/leadphoton_hoe.png')
plt.clf()

for MX in MXs:
    if not ("000" in MX): continue 
    plt.hist(x=events[MX]["photon_cuts_only"].LeadPhoton_sieie, 
             weights=events[MX]["photon_cuts_only"].weight_central,
             bins=np.arange(0.,0.1,0.002),
             alpha=0.4,
             label='MX=%.0f'%MX)

plt.yscale("log")
plt.legend()
plt.xlabel('lead ph sigma(ieta,ieta)')
plt.savefig('plots/leadphoton_sieie.png')
plt.clf()

