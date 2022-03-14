import awkward
import vector

vector.register_awkward()

import logging
logger = logging.getLogger(__name__)

from higgs_dna.taggers.tagger import Tagger, NOMINAL_TAG
from higgs_dna.selections import object_selections, lepton_selections, jet_selections, tau_selections, fatjet_selections, gen_selections
from higgs_dna.utils import awkward_utils, misc_utils

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

    "photon_mvaID" : -0.7
}

class HHggbbTagger(Tagger):

    def __init__(self, name = "hhggbb_tagger", options = {}, is_data = None, year = None):
        super(HHggbbTagger, self).__init__(name, options, is_data, year)

        if not options:
            self.options = DEFAULT_OPTIONS 
        else:
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

        n_bjets = awkward.num(bjets)
        awkward_utils.add_field(events, "n_bjets", n_bjets)

        n_fatjets = awkward.num(fatjets)
        awkward_utils.add_field(events, "n_fatjets", n_fatjets)

        # gen selections for the signal sample
        if not self.is_data:
            gen_hbb = gen_selections.select_x_to_yz(events.GenPart, 25, 5, 5)
            gen_hgg = gen_selections.select_x_to_yz(events.GenPart, 25, 22, 22)
            gen_hzz = gen_selections.select_x_to_yz(events.GenPart, 25, 23, 23)
            gen_hww = gen_selections.select_x_to_yz(events.GenPart, 25, 24, 24)
            gen_htt = gen_selections.select_x_to_yz(events.GenPart, 25, 15, 15)

            #two distincts decays per event
            if awkward.any( (awkward.num(gen_hbb)>1) | (awkward.num(gen_htt)>1) | \
                            (awkward.num(gen_hgg)>1) | (awkward.num(gen_hzz)>1) | (awkward.num(gen_hww)>1) ):
                raise RuntimeError("can handle only two distincts H decays per event")
                
            #at most one decay to something else than gg
            if awkward.any( (awkward.num(gen_hbb)>0) & (awkward.num(gen_hzz)>0) & \
                            (awkward.num(gen_hww)>0) & (awkward.num(gen_htt)>0) ):
                raise RuntimeError("can handle at most one decay to something else than gg")

            #hbbevts = (awkward.num(gen_hbb)==1)
            #hggevts = (awkward.num(gen_hgg)==1)
            #hzzevts = (awkward.num(gen_hzz)==1)
            #hwwevts = (awkward.num(gen_hww)==1)

            #gen_otherh_parent = awkward.zeros_like(n_jets)
            #gen_otherh_parent = awkward.fill_none(gen_otherh_parent, 0)
            #gen_otherh_parent = awkward.where(hbbevts, gen_hbb, gen_otherh_parent)
            #gen_otherh_parent = awkward.where(httevts, gen_htt, gen_otherh_parent)
            #gen_otherh_parent = awkward.where(hwwevts, gen_hww, gen_otherh_parent)
            #gen_otherh_parent = awkward.where(hzzevts, gen_hzz, gen_otherh_parent)

            print(gen_hbb)
            print(type(gen_hbb))
            print(awkward.num(gen_hbb))
            print(gen_htt)
            print(type(gen_htt))
            print(awkward.num(gen_htt))
            print(gen_hbb.GenParent)
            print(type(gen_hbb.GenParent))
            gen_otherh = awkward.concatenate([gen_hbb,gen_htt,gen_hww,gen_hzz], axis=1)
            print(gen_otherh)
            print(type(gen_otherh))
            print(awkward.num(gen_otherh))
            print(len(gen_otherh))
            hxxevts = (awkward.num(gen_otherh)==1)
            hggevts = (awkward.num(gen_hgg)==1)

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

            print("combination1",combination1)
            print("events.LeadPhoton.deltaR(gen_hgg.LeadGenChild)",events.LeadPhoton.deltaR(gen_hgg.LeadGenChild))

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
            #print("type(deltaRLeadPhotonfromGen)",type(deltaRLeadPhotonfromGen))
            #print("deltaRLeadPhotonfromGen",deltaRLeadPhotonfromGen)
            #print("awkward.num(deltaRLeadPhotonfromGen, axis=1)",awkward.num(deltaRLeadPhotonfromGen, axis=1))
            #print("awkward.sum(awkward.num(deltaRLeadPhotonfromGen))",awkward.sum(awkward.num(deltaRLeadPhotonfromGen)))
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

        #print(events.fields)            
        self.register_cuts(
            names = ["photon ID MVA", "ptOvermgg_cut", "category_cut", "all cuts"],
            results = [pho_id, ptOvermgg_cut, category_cut, presel_cut]
        )

        return presel_cut, events 

