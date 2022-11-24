import awkward
import vector
import numpy as np
vector.register_awkward()

import logging
logger = logging.getLogger(__name__)

from higgs_dna.taggers.tagger import Tagger, NOMINAL_TAG
from higgs_dna.selections import object_selections, lepton_selections, jet_selections, tau_selections, fatjet_selections, gen_selections,tools
from higgs_dna.utils import awkward_utils, misc_utils
from get2body import get2BodyMass

DUMMY_VALUE = -999.
DEFAULT_OPTIONS = {
    "electrons" : {
        "pt" : 15.0,
        "eta" : 2.5,
        "dxy" : 0.045,
        "dz" : 0.2,
        "id" : "WP90",
        "dr_photons" : 0.2,
        "veto_transition" : True,
    },
    "muons" : {
        "pt" : 15.0,
        "eta" : 2.4,
        "dxy" : 0.045,
        "dz" : 0.2,
        "id" : None,
        "pfRelIso03_all" : 0.3,
        "dr_photons" : 0.2
    },
    "taus" : {
        "pt" : 18.0,
        "eta" : 2.3,
        "dz" : 0.2,
        "deep_tau_vs_ele" : 1,
        "deep_tau_vs_mu" : 0,
        "deep_tau_vs_jet" : 7,
        "dr_photons" : 0.2,
        "dr_electrons" : 0.2,
        "dr_muons" : 0.2
    },
    "jets" : {
        "pt" : 25.0,
        "eta" : 2.4,
        "looseID" : True,
        "dr_photons" : 0.4,
        "dr_electrons" : 0.4,
        "dr_muons" : 0.4,
        "dr_taus" : 0.4,
        "dr_iso_tracks" : 0.4
    },
    "fatjets" : {
        "pt" : 250.,
        "eta" : 2.4,
        "dr_photons" : 0.4,
        "dr_electrons" : 0.4,
        "dr_muons" : 0.4,
        "dr_taus" : 0.4,
    }, 

    "photon_mvaID" : -0.9,
    "nocuts": False,
    "genHiggsAnalysis": True
}

class HHggbbTagger(Tagger):

    def __init__(self, name = "hhggbb_tagger", options = {}, is_data = None, year = None):
        super(HHggbbTagger, self).__init__(name, options, is_data, year)

        if not options:
            print("not options")
            self.options = DEFAULT_OPTIONS 
        else:
            print("I got the following options")
            print(options)
            self.options = misc_utils.update_dict(
                    original = DEFAULT_OPTIONS,
                    new = options
            )
    
        

    def calculate_selection(self, events):
        # Electrons
        electron_cut = lepton_selections.select_electrons(
                electrons = events.Electron,
                options = self.options["electrons"],
                clean = {
                    "photons" : {
                        "objects" : events.Diphoton.Photon,
                        "min_dr" : self.options["electrons"]["dr_photons"]
                    }
                },
                name = "SelectedElectron",
                tagger = self
        )
        electrons = awkward_utils.add_field(
                events = events,
                name = "SelectedElectron",
                data = events.Electron[electron_cut]
        )

        # Muons
        muon_cut = lepton_selections.select_muons(
                muons = events.Muon,
                options = self.options["muons"],
                clean = {
                    "photons" : {
                        "objects" : events.Diphoton.Photon,
                        "min_dr" : self.options["muons"]["dr_photons"]
                    }
                },
                name = "SelectedMuon",
                tagger = self
        )
        muons = awkward_utils.add_field(
                events = events,
                name = "SelectedMuon",
                data = events.Muon[muon_cut]
        )

        # Fat jets
        fatjet_cut = fatjet_selections.select_fatjets(
                fatjets = events.FatJet,
                options = self.options["fatjets"],
                clean = {
                    "photons" : {
                        "objects" : events.Diphoton.Photon,
                        "min_dr" : self.options["jets"]["dr_photons"]
                    },
                    "electrons" : {
                        "objects" : events.SelectedElectron,
                        "min_dr" : self.options["jets"]["dr_electrons"]
                    },
                    "muons" : {
                        "objects" : events.SelectedMuon,
                        "min_dr" : self.options["jets"]["dr_muons"]
                    }
                },
                name = "SelectedFatJet",
                tagger = self
        )
        fatjets = awkward_utils.add_field(
                events = events,
                name = "SelectedFatJet",
                data = awkward.Array(events.FatJet[fatjet_cut], with_name = "Momentum4D")
        )   
        #pick the fat jet, if any, with the highest deepTagMD_HbbvsQCD score
        fathbbjets = awkward_utils.add_field(
                events = events,
                name = "SelectedFatHbbJet",
                data = awkward.pad_none(
                    events.SelectedFatJet[awkward.argsort(fatjets.deepTagMD_HbbvsQCD, axis = 1, ascending = False)],
                    1, clip=True)
        )   
        #pick the fat jet, if any, with the highest deepTagMD_H4qvsQCD score
        fath4qjets = awkward_utils.add_field(
                events = events,
                name = "SelectedFatH4qJet",
                data = awkward.pad_none(
                    events.SelectedFatJet[awkward.argsort(fatjets.deepTagMD_H4qvsQCD, axis = 1, ascending = False)],
                    1, clip=True)
        )   

        # Jets
        jet_cut = jet_selections.select_jets(
                jets = events.Jet,
                options = self.options["jets"],
                clean = {
                    "photons" : {
                        "objects" : events.Diphoton.Photon,
                        "min_dr" : self.options["jets"]["dr_photons"]
                    },
                    "electrons" : {
                        "objects" : events.SelectedElectron,
                        "min_dr" : self.options["jets"]["dr_electrons"]
                    },
                    "muons" : {
                        "objects" : events.SelectedMuon,
                        "min_dr" : self.options["jets"]["dr_muons"]
                    },

                },
                name = "SelectedJet",
                tagger = self
        )
        jets = awkward_utils.add_field(
                events = events,
                name = "SelectedJet",
                data = events.Jet[jet_cut]
        )
        #pick the two jets, with the highest btagDeepFlavB score
        bjets = awkward_utils.add_field(
                events = events,
                name = "SelectedbJet",
                data = awkward.pad_none(
                    events.SelectedJet[awkward.argsort(jets.btagDeepFlavB, axis = 1, ascending = False)],
                    2, clip=True)
        )   

        # Add object fields to events array
        for objects, name in zip([electrons, muons, jets, fatjets], ["electron", "muon", "jet", "fatjet"]):
            awkward_utils.add_object_fields(
                    events = events,
                    name = name,
                    objects = objects,
                    n_objects = 4,
                    dummy_value = DUMMY_VALUE
            )

        awkward_utils.add_object_fields(
            events = events,
            name = "bjet",
            objects = bjets,
            n_objects = 2,
            dummy_value = DUMMY_VALUE
        )

        awkward_utils.add_object_fields(
            events = events,
            name = "fathbbjet",
            objects = fathbbjets,
            n_objects = 1,
            dummy_value = DUMMY_VALUE
        )

        awkward_utils.add_object_fields(
            events = events,
            name = "fath4qjet",
            objects = fath4qjets,
            n_objects = 1,
            dummy_value = DUMMY_VALUE
        )


        n_electrons = awkward.num(electrons)
        awkward_utils.add_field(events, "n_electrons", n_electrons)
        
        n_muons = awkward.num(muons)
        awkward_utils.add_field(events, "n_muons", n_muons)
        
        n_leptons = n_electrons + n_muons
        awkward_utils.add_field(events, "n_leptons", n_leptons)
        
        n_jets = awkward.num(jets)
        awkward_utils.add_field(events, "n_jets", n_jets)
        print("jet",n_jets)
        print(len(n_jets))
        print(len(jets))
        n_bjets = awkward.num(bjets)
        awkward_utils.add_field(events, "n_bjets", n_bjets)

        n_fatjets = awkward.num(fatjets)
        awkward_utils.add_field(events, "n_fatjets", n_fatjets)
        print("nfatjet",n_fatjets)
        print(len(n_fatjets))
        print(len(fatjets))
        n_fat4qjets = awkward.num(fath4qjets)
        awkward_utils.add_field(events, "n_fath4qjets", n_fat4qjets)
        
        n_fathbbjets = awkward.num(fathbbjets)
        awkward_utils.add_field(events, "n_fathbbjets", n_fathbbjets)

        #dijet_mass = get2BodyMass(events,"bjet_1_pt","bjet_1_phi","bjet_1_eta","bjet_1_mass","bjet_2_pt","bjet_2_phi","bjet_2_eta","bjet_2_mass",type=False)
        
        print(bjets.pt)
        # resjet = events.SelectedJet[awkward.argsort(jets.pt, ascending=False, axis=1)]
        resjet = bjets[awkward.argsort(bjets.pt,ascending=False,axis=1)]
        resjet = awkward.Array(resjet, with_name = "Momentum4D")
        print("33333333",resjet.pt)
    #     # Get all combinations of two photons in each event
        dijet = awkward.combinations(resjet, 2, fields=["Leadjet", "Subleadjet"])
   
        dijet["Dijet"] = dijet.Leadjet + dijet.Subleadjet
        print("lead",dijet.Leadjet.pt)
        print("sub",dijet.Subleadjet.pt)
        print(dijet.Dijet.fields)
        print(dijet.Dijet.pt)
        di_events=dijet
        di_events["pt"] = dijet.Dijet.pt
        di_events["phi"] = dijet.Dijet.phi
        di_events["eta"] = dijet.Dijet.eta
        di_events["mass"] = dijet.Dijet.mass
        print(di_events.fields)
        awkward_utils.add_object_fields(
            events = events,
            name = "Dijet",
            objects = di_events,
            n_objects = 1,
            dummy_value = DUMMY_VALUE
        )
        awkward_utils.add_field(events = events,name = "resdijet",data = dijet.Dijet)
        #leadjet = awkward.pad_none(dijet.Leadjet[awkward.argsort(dijet.Leadjet.pt, axis = 1, ascending = False)],1,clip=True)
        #subleadjet = awkward.pad_none(dijet.Subleadjet[awkward.argsort(dijet.Subleadjet.pt, axis = 1, ascending = False)],1,clip=True)
        leadjet = dijet.Leadjet
        subleadjet = dijet.Subleadjet
        leadjet = awkward.flatten(leadjet,axis=1)
        subleadjet = awkward.flatten(subleadjet,axis=1)
        events["cosdijet"] = tools.getCosTheta(leadjet,subleadjet)
       

        mstar = get2BodyMass(events,events.Diphoton,"pt","phi","eta","mass","Dijet_pt","Dijet_phi","Dijet_eta","Dijet_mass")
        awkward_utils.add_field(events, "res_mStar", mstar)
        mstar2 = get2BodyMass(events,events.Diphoton,"pt","phi","eta","mass","fathbbjet_pt","fathbbjet_phi","fathbbjet_eta","fathbbjet_mass")
        awkward_utils.add_field(events, "boost_mStar", mstar2)
        
      
      
        print(self.options)
        if (not self.is_data) and self.options["genHiggsAnalysis"]:
            gen_hbb = gen_selections.select_x_to_yz(events.GenPart, 25, 5, 5)
            gen_Ybb = gen_selections.select_x_to_yz(events.GenPart, 35, 5, 5)
            gen_hgg = gen_selections.select_x_to_yz(events.GenPart, 25, 22, 22)
            gen_hzz = gen_selections.select_x_to_yz(events.GenPart, 25, 23, 23)
            gen_hww = gen_selections.select_x_to_yz(events.GenPart, 25, 24, 24)
            gen_htt = gen_selections.select_x_to_yz(events.GenPart, 25, 15, 15)

            #two distincts decays per event
            if awkward.any( (awkward.num(gen_hbb)>1) | (awkward.num(gen_htt)>1) | \
                            (awkward.num(gen_hgg)>1) | (awkward.num(gen_hzz)>1) | (awkward.num(gen_hww)>1)|(awkward.num(gen_Ybb)>1)):
                raise RuntimeError("can handle only two distincts H decays per event")
                #d
            #at most one decay to something else than gg
            if awkward.any( (awkward.num(gen_hbb)>0) & (awkward.num(gen_hzz)>0) & \
                            (awkward.num(gen_hww)>0) & (awkward.num(gen_htt)>0)&(awkward.num(gen_Ybb)>0)):
                raise RuntimeError("can handle at most one decay to something else than gg")
#& 
            #,gen_Ybb gen_hbb,gen_htt,gen_hww,gen_hzz,
            gen_otherh = awkward.concatenate([gen_hbb,gen_htt,gen_hww,gen_hzz,gen_Ybb], axis=1)
            hxxevts = (awkward.num(gen_otherh)==1)
            hggevts = (awkward.num(gen_hgg)==1)

            awkward_utils.add_object_fields(events, 
                                            "Genhbb", 
                                            gen_hbb.GenParent, 
                                            n_objects = 1, 
                                            dummy_value = DUMMY_VALUE)

            awkward_utils.add_object_fields(events, 
                                            "GenYbb", 
                                            gen_Ybb.GenParent, 
                                            n_objects = 1, 
                                            dummy_value = DUMMY_VALUE)

            awkward_utils.add_object_fields(events, 
                                            "GenOtherHiggs", 
                                            gen_otherh.GenParent, 
                                            n_objects = 1, 
                                            dummy_value = DUMMY_VALUE)
            awkward_utils.add_object_fields(events, 
                                            "GenOtherHiggsLeadprod", 
                                            gen_otherh.LeadGenChild, 
                                            n_objects = 1,
                                            dummy_value = DUMMY_VALUE)
            awkward_utils.add_object_fields(events, 
                                            "GenOtherHiggsSubleadprod", 
                                            gen_otherh.SubleadGenChild, 
                                            n_objects = 1,
                                            dummy_value = DUMMY_VALUE)

            # find combination of the pair of gen & reco photons that minimizes the deltaR  
            combination1 = (events.LeadPhoton.deltaR(gen_hgg.LeadGenChild)+
                            events.SubleadPhoton.deltaR(gen_hgg.SubleadGenChild)) < (
                                events.LeadPhoton.deltaR(gen_hgg.SubleadGenChild)+
                                events.SubleadPhoton.deltaR(gen_hgg.LeadGenChild))

            deltaRLeadPhotonfromGen = awkward.where(combination1,
                                                    events.LeadPhoton.deltaR(gen_hgg.LeadGenChild),
                                                    events.LeadPhoton.deltaR(gen_hgg.SubleadGenChild))
            deltaRLeadPhotonfromGen = awkward.where(hggevts, 
                                                    deltaRLeadPhotonfromGen, 
                                                    awkward.ones_like(deltaRLeadPhotonfromGen)*DUMMY_VALUE)
            deltaRSubleadPhotonfromGen = awkward.where(combination1,
                                                    events.SubleadPhoton.deltaR(gen_hgg.SubleadGenChild),
                                                    events.SubleadPhoton.deltaR(gen_hgg.LeadGenChild))
            deltaRSubleadPhotonfromGen = awkward.where(hggevts, 
                                                       deltaRSubleadPhotonfromGen, 
                                                       awkward.ones_like(deltaRSubleadPhotonfromGen)*DUMMY_VALUE)
            
            
            deltaRLeadPhotonfromGen = awkward.flatten(deltaRLeadPhotonfromGen,axis=1)
            deltaRSubleadPhotonfromGen = awkward.flatten(deltaRSubleadPhotonfromGen,axis=1)
            
            awkward_utils.add_field(events, "deltaRLeadPhotonfromGen", deltaRLeadPhotonfromGen)
            awkward_utils.add_field(events, "deltaRSubleadPhotonfromGen", deltaRSubleadPhotonfromGen)

            deltaRFatHbbJetGenOtherHiggs = events.SelectedFatHbbJet.deltaR(gen_otherh.GenParent)
            deltaRFatHbbJetGenOtherHiggs = awkward.where(hxxevts & (n_fatjets>0), 
                                                      deltaRFatHbbJetGenOtherHiggs, 
                                                      awkward.ones_like(deltaRFatHbbJetGenOtherHiggs)*DUMMY_VALUE)

            deltaRFatHbbJetGenOtherHiggs = awkward.flatten(deltaRFatHbbJetGenOtherHiggs,axis=1)
            awkward_utils.add_field(events, "deltaRFatHbbJetGenOtherHiggs", deltaRFatHbbJetGenOtherHiggs)

            deltaRFatH4qJetGenOtherHiggs = events.SelectedFatH4qJet.deltaR(gen_otherh.GenParent)
            deltaRFatH4qJetGenOtherHiggs = awkward.where(hxxevts & (n_fatjets>0), 
                                                      deltaRFatH4qJetGenOtherHiggs, 
                                                      awkward.ones_like(deltaRFatH4qJetGenOtherHiggs)*DUMMY_VALUE)
            
           
            deltaRFatH4qJetGenOtherHiggs = awkward.flatten(deltaRFatH4qJetGenOtherHiggs,axis=1)
            
            awkward_utils.add_field(events, "deltaRFatH4qJetGenOtherHiggs", deltaRFatH4qJetGenOtherHiggs)

        events[("Diphoton", "DiphoCosThetaStar")]=tools.getCosTheta(events.LeadPhoton,events.SubleadPhoton)
        events[("Diphoton", "lead_pt_mgg")]=events.LeadPhoton.pt/events.Diphoton.mass
        events[("Diphoton", "sublead_pt_mgg")]=events.SubleadPhoton.pt/events.Diphoton.mass
        events[("Diphoton", "lead_vidNestedWPBitmap")]=events.LeadPhoton.vidNestedWPBitmap
        events[("Diphoton", "sublead_vidNestedWPBitmap")]=events.SubleadPhoton.vidNestedWPBitmap
        events[("Diphoton", "lead_pho_mvaID")]=events.LeadPhoton.mvaID
        events[("Diphoton", "sublead_pho_mvaID")]=events.SubleadPhoton.mvaID

        events[("Diphoton", "lead_pho_sigEoE")]=events.LeadPhoton.energyErr/events.LeadPhoton.E
        events[("Diphoton", "sublead_pho_sigEoE")]=events.SubleadPhoton.energyErr/events.SubleadPhoton.E
        # Photon ID and Pt/Mgg cuts
        pho_id = (events.LeadPhoton.mvaID > self.options["photon_mvaID"]) & (events.SubleadPhoton.mvaID > self.options["photon_mvaID"])
        ptOvermgg_cut = (events.LeadPhoton.pt/events.Diphoton.mass)>0.33
        ptOvermgg_cut = ptOvermgg_cut & ((events.SubleadPhoton.pt/events.Diphoton.mass)>0.25)

        # category
        # 1: boosted
        # 2: resolved
        category = awkward.zeros_like(n_jets)
        category = awkward.fill_none(category, 0)
        category = awkward.where(n_fatjets>0, awkward.ones_like(category)*1, category)
        category = awkward.where((n_fatjets==0) & (n_jets>1), awkward.ones_like(category)*2, category)
        awkward_utils.add_field(events, "category", category) 
        category_cut = category > 0

        presel_cut = pho_id & ptOvermgg_cut & category_cut
        
# ============================================
#       
        

        #events["deltaRsubleadjetphoton"] = deltaRsubleadjetphoton
        combination2 = (events.LeadPhoton.deltaR(leadjet)+
                            events.SubleadPhoton.deltaR(subleadjet)) < (
                                events.LeadPhoton.deltaR(subleadjet)+
                                events.SubleadPhoton.deltaR(leadjet))
        
        deltaRleadjetphoton=awkward.where(combination2,events.LeadPhoton.deltaR(leadjet),events.LeadPhoton.deltaR(subleadjet))
        
        deltaRleadjetphoton = awkward.where( (n_fatjets==0) & (n_jets>1), 
                                                     deltaRleadjetphoton,awkward.ones_like(deltaRleadjetphoton)*DUMMY_VALUE)
        #awkward_utils.add_field(events, "deltaRleadjetphoton", deltaRleadjetphoton)
        deltaRsubleadjetphoton = awkward.where(combination2,events.SubleadPhoton.deltaR(subleadjet),events.SubleadPhoton.deltaR(leadjet))
        deltaRsubleadjetphoton = awkward.where( (n_fatjets==0) & (n_jets>1), 
                                                      deltaRsubleadjetphoton, 
                                                      awkward.ones_like(deltaRsubleadjetphoton)*DUMMY_VALUE)
        minjetphoton = awkward.where(deltaRleadjetphoton<deltaRsubleadjetphoton,deltaRleadjetphoton,deltaRsubleadjetphoton)
        # awkward_utils.add_field(events, "mindrjetphoton",minjetphoton)
        fathbbjet = awkward.flatten(fathbbjets,axis=-1)
        combination3 = (events.LeadPhoton.deltaR(fathbbjet))<(events.LeadPhoton.deltaR(fathbbjet))
        deltaRfatjetphoton = awkward.where(combination3,events.LeadPhoton.deltaR(fathbbjet),events.LeadPhoton.deltaR(fathbbjet))
        deltaRfatjetphoton = awkward.where( (n_fatjets>0),deltaRfatjetphoton,awkward.ones_like(deltaRfatjetphoton)*DUMMY_VALUE)
        



        awkward_utils.add_field(
                events = events,
                name = "FatHighestPtJet",
                data = awkward.pad_none(
                    events.SelectedFatJet[awkward.argsort(events.SelectedFatJet.pt, axis = 1, ascending = False)],
                    1, clip=True)
        ) 
        print(events.FatHighestPtJet.pt)
      
        print(events.Diphoton.pt)
        
        FatHighestPtJet = awkward.flatten(events.FatHighestPtJet,axis = -1)
        print("resdijet",events.resdijet.pt)
        res_dijet = awkward.flatten(events.resdijet,axis = -1)
        print("flatten",res_dijet.pt)
        #print(events[""][events["category"]==1])
        print(len(events.Diphoton.pt))
        print(len(FatHighestPtJet.pt))
        print(FatHighestPtJet.pt)
        print(len(res_dijet.pt))
        print(len(FatHighestPtJet["pt"][events["category"]==1]))
        #dijet_events = events[events["category"]==2]
        cosTheta_CS = awkward.zeros_like(n_jets)
        cosTheta_CS = awkward.fill_none(cosTheta_CS, 0)
        cosTheta_CS = awkward.where(events.category==1, tools.getCosThetaStar_CS(events.Diphoton,FatHighestPtJet),cosTheta_CS)
        cosTheta_CS = awkward.where(events.category==2, tools.getCosThetaStar_CS(events.Diphoton,res_dijet), cosTheta_CS)
        mStar = awkward.zeros_like(mstar)
        mStar = awkward.fill_none(mStar,0)
        mStar = awkward.where(events.category==1, mstar2,mStar)
        mStar = awkward.where(events.category==2,mstar,mStar)
        mindr = awkward.zeros_like(deltaRfatjetphoton)
        mindr = awkward.fill_none(mindr,0)
        mindr = awkward.where(events.category==1,deltaRfatjetphoton,mindr)
        mindr = awkward.where(events.category==2,minjetphoton,mindr)
        awkward_utils.add_field(
                events = events,
                name = "cosThetaStar_CS",
                data = cosTheta_CS
        ) 
        awkward_utils.add_field(
                events = events,
                name = "mStar",
                data = mStar
        ) 
        awkward_utils.add_field(
                events = events,
                name = "mindr",
                data = mindr
        )
        # if(len(FatJet_events)>0): 
        #    # FatJet_events = FatJet_events[awkward.argsort(FatJet_events.SelectedFatJet.pt, axis = 1, ascending = False)]
           
        #     FirstFatJet = awkward.singletons(awkward.firsts(FatJet_events.FatHighestPtJet))
        #     First_Fat_Jet = awkward.flatten(
        #             FirstFatJet,
        #             axis = -1 
        #             )
        #     print("fatjet:",len(FatJet_events))
        #     awkward_utils.add_field(events = FatJet_events,name="FirstFatJet",data = First_Fat_Jet,overwrite=True)
        #     print("first",FatJet_events.FirstFatJet)
        #     cosTheta_CS=tools.getCosThetaStar_CS(FatJet_events.Diphoton,FatJet_events.FirstFatJet)
            
        # # cosTheta_CS=tools.getCosThetaStar_CS(FatJet_events.Diphoton,FatJet_events.SubleadFatJet)
        #     min_dr,max_dr=tools.getPhoJetDr(FatJet_events.FirstFatJet,FatJet_events.LeadPhoton,FatJet_events.SubleadPhoton)
        #     tools.FillWithDummy(events,min_dr,DUMMY_VALUE,"minPhoJetDr","category",1) #when category==1 fill the value with min_dr, otherwise, fill with Dummy
        #     tools.FillWithDummy(events,max_dr,DUMMY_VALUE,"maxPhoJetDr","category",1)
        #     tools.FillWithDummy(events,cosTheta_CS,DUMMY_VALUE,"cosThetaStar_CS","category",1)
        # elif(len(dijet_events>0)):
              
        #         #awkward_utils.add_field(events = dijet_events,name="Dijet",data = dijet_events.dijet_cos,overwrite=True)
        #         cosTheta_CS_dijet = tools.getCosThetaStar_CS(dijet_events.Diphoton,dijet_events.dijet_cos)
        #         tools.FillWithDummy(events,[],DUMMY_VALUE,"minPhoJetDr","category",1) #when category==1 fill the value with min_dr, otherwise, fill with Dummy
        #         tools.FillWithDummy(events,[],DUMMY_VALUE,"maxPhoJetDr","category",1)
        #         tools.FillWithDummy(events,cosTheta_CS_dijet,DUMMY_VALUE,"cosThetaStar_CS","category",1)
        # else:
        #         tools.FillWithDummy(events,[],DUMMY_VALUE,"minPhoJetDr","category",1) #when category==1 fill the value with min_dr, otherwise, fill with Dummy
        #         tools.FillWithDummy(events,[],DUMMY_VALUE,"maxPhoJetDr","category",1)
        #         tools.FillWithDummy(events,[],DUMMY_VALUE,"cosThetaStar_CS","category",1)
        # print("111   :",len(FatJet_events.FirstFatJet))
        # cosTheta_CS = awkward.zeros_like(n_jets)
        # cosTheta_CS = awkward.fill_none(cosTheta_CS, 0)
        # cosTheta_CS = awkward.where(n_fatjets>0, tools.getCosThetaStar_CS(FatJet_events.Diphoton,FatJet_events.FirstFatJet),cosTheta_CS)
        # cosTheta_CS = awkward.where((n_fatjets==0) & (n_jets>1), tools.getCosThetaStar_CS(dijet_events.Diphoton,dijet_events.resdijet), cosTheta_CS)

# ===========================================
        #print(events.fields)            
        if self.options["nocuts"]:
            for name,objects in zip(
                    ["hhggxx_photonIDcut", "hhggxx_ptOvermgg_cut", "hhggxx_category_cut", "hhggxx_allcuts"],
                    [pho_id, ptOvermgg_cut, category_cut, presel_cut]):
                awkward_utils.add_field(events, name, objects)
                presel_cut = (events.LeadPhoton.pt > 0)
        else:
            self.register_cuts(
                names = ["photon ID MVA", "ptOvermgg_cut", "category_cut", "all cuts"],
                results = [pho_id, ptOvermgg_cut, category_cut, presel_cut]
            )

        return presel_cut, events 

