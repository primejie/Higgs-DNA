import awkward
import time
import numpy
import numba
import vector

vector.register_awkward()

import logging
logger = logging.getLogger(__name__)

from higgs_dna.taggers.tagger import Tagger, NOMINAL_TAG 
from higgs_dna.utils import awkward_utils, misc_utils
from higgs_dna.selections import gen_selections,tools

DEFAULT_OPTIONS = {
    "photons" : {
        "nocuts" : False,
        "use_central_nano" : True,
        "pt" : 25.0,
        "eta" : [
            [0.0, 1.4442],
            [1.566, 2.5]
        ],
        "e_veto" : 0.5,
        "hoe" : 0.08,
        "r9" : 0.8,
        "charged_iso" : 20.0,
        "charged_rel_iso" : 0.3,
        "hlt" : {
            "eta_rho_corr" : 1.5,
            "low_eta_rho_corr" : 0.16544,
            "high_eta_rho_corr" : 0.13212,
            "eb_high_r9" : {
                "r9" : 0.85
            },
            "eb_low_r9" : {
                "r9" : 0.5,
                "pho_iso" : 4.0,
                "track_sum_pt" : 6.0,
                "sigma_ieie" : 0.015
            },
            "ee_high_r9" : {
                "r9" : 0.9
            },
            "ee_low_r9" : {
                "r9" : 0.8,
                "pho_iso" : 4.0,
                "track_sum_pt" : 6.0,
                "sigma_ieie" : 0.035
            }
        }
    },
    "diphotons" : {
        "lead_pt" : 35.0,
        "sublead_pt" : 25.0,
        "lead_pt_mgg" : 0.33,
        "sublead_pt_mgg" : 0.25,
        "mass" : [100., 180.],
        "select_highest_pt_sum" : True,
        "nocuts" : False
    },
    "trigger" : {
        "2016" : ["HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"],
        "2016preVFP":["HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"],
        "2016postVFP":["HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"],
        "2017" : ["HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"],
        "2018" : ["HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"]
    },
    "gen_info" : {
        "calculate" : True,
        "max_dr" : 0.2,
        "max_pt_diff" : 15.
    }
}


# Diphoton preselection below synced with flashgg, see details in:
#   - https://indico.cern.ch/event/1071721/contributions/4551056/attachments/2320292/3950844/HiggsDNA_DiphotonPreselectionAndSystematics_30Sep2021.pdf

class DiphotonTagger(Tagger):
    def __init__(self, name = "default_diphoton_tagger", options = {}, is_data = None, year = None):
        super(DiphotonTagger, self).__init__(name, options, is_data, year)

        if not options:
            self.options = DEFAULT_OPTIONS
        else:
            self.options = misc_utils.update_dict(
                    original = DEFAULT_OPTIONS,
                    new = options
            )

    def calculate_selection(self, events):
        """
        Select photons and create diphoton pairs.
        Add a record "Diphoton" to events array with relevant information about each diphoton pair.
        In principle, there can be more than one Diphoton pair per event.
        """
        #print("A awkward.sum(awkward.is_none(events))",awkward.sum(awkward.is_none(events)))

        photon_selection,photons = self.select_photons(
                photons = events.Photon,
                # rho = events.fixedGridRhoAll if not self.options["photons"]["use_central_nano"] else awkward.ones_like(events.Photon), # FIXME: to be deleted once fixedGridRhoAll is added to central nanoAOD
                rho = events.fixedGridRhoFastjetAll if not self.options["photons"]["use_central_nano"] else awkward.ones_like(events.Photon), # FIXME: to be deleted once fixedGridRhoAll is added to central nanoAOD
                # rho = events.fixedGridRhoFastjetAll,  # FIXME: to be deleted once fixedGridRhoAll is added to central nanoAOD
                options = self.options["photons"]
        )
        rho_debug=events.fixedGridRhoFastjetAll if not self.options["photons"]["use_central_nano"] else awkward.ones_like(events.Photon), # FIXME: to be deleted once fixedGridRhoAll is added to central nanoAOD
        if self.options["photons"]["nocuts"]:
            events["Photon"]=photons
        #print("B awkward.sum(awkward.is_none(events))",awkward.sum(awkward.is_none(events)))
        
        diphoton_selection, diphotons = self.produce_and_select_diphotons(
                events = events,
                photons = events.Photon[photon_selection],
                options = self.options["diphotons"]
        )

        #print("C awkward.sum(awkward.is_none(diphotons))",awkward.sum(awkward.is_none(diphotons)))

        if not self.is_data and self.options["gen_info"]["calculate"]:
            diphotons = self.calculate_gen_info(diphotons, self.options["gen_info"])

        #print("D awkward.sum(awkward.is_none(diphotons.GenHggHiggs_dR))",awkward.sum(awkward.is_none(diphotons.GenHggHiggs_dR)))
        #exit()
        return diphoton_selection, diphotons 


    def produce_and_select_diphotons(self, events, photons, options):
        """
        Perform diphoton preselection.
        For events with more than 2 photons, more than 1 diphoton candidate
        per event is possible.

        :param events: events array to calculate diphoton candidates from
        :type events: awkward.highlevel.Array
        :param photons: array of selected photons from events
        :type photons: awkward.highlevel.Array
        :param options: dictionary containing configurable options for the diphoton preselection
        :type options: dict
        :return: boolean array indicating which events pass the diphoton preselection
        :rtype: awkward.highlevel.Array
        """

        start = time.time()

        # Sort photons by pt
        photons = photons[awkward.argsort(photons.pt, ascending=False, axis=1)]

        # Register as `vector.Momentum4D` objects so we can do four-vector operations with them
        photons = awkward.Array(photons, with_name = "Momentum4D")
        # Get all combinations of two photons in each event
        diphotons = awkward.combinations(photons, 2, fields=["LeadPhoton", "SubleadPhoton"])
        diphotons["Diphoton"] = diphotons.LeadPhoton + diphotons.SubleadPhoton

        # Add sumPt and dR for convenience
        diphotons[("Diphoton", "sumPt")] = diphotons.LeadPhoton.pt + diphotons.SubleadPhoton.pt
        diphotons[("Diphoton", "dR")] = diphotons.LeadPhoton.deltaR(diphotons.SubleadPhoton)   
        #print("gggggggggggggg")   
        
        diphotons[("Diphoton", "sigmoM")] = 0.5 * numpy.sqrt(
                            (
                                diphotons["LeadPhoton"].energyErr
                                / (
                                    diphotons["LeadPhoton"].pt
                                    * numpy.cosh(diphotons["LeadPhoton"].eta)
                                )
                            )
                            ** 2
                            + (
                                diphotons["SubleadPhoton"].energyErr
                                / (
                                    diphotons["SubleadPhoton"].pt
                                    * numpy.cosh(diphotons["SubleadPhoton"].eta)
                                )
                            )
                            ** 2
                        )
        
        

        # Add lead/sublead photons to additionally be accessible together as diphotons.Diphoton.Photon
        # This is in principle a bit redundant, but makes many systematics and selections much more convenient to implement.
        # lead/sublead photons have shape [n_events, n_diphotons_per_event], but to merge them we need to give them shape [n_events, n_diphotons_per_event, 1]
        lead_photons = awkward.unflatten(
                diphotons.LeadPhoton,
                counts = 1, # new dimension has length 1
                axis = -1 # add new dimension to innermost axis
        )

        sublead_photons = awkward.unflatten(
                diphotons.SubleadPhoton,
                counts = 1,
                axis = -1
        )

        awkward_utils.add_field(
                events = diphotons,
                name = ("Diphoton", "Photon"),
                data = awkward.concatenate(
                    [lead_photons, sublead_photons],
                    axis = 2 # keep constant along first two dimensions ([n_events, n_diphotons]), and merge along remaining dimensions
                )
        )
       # print(diphotons.Diphoton.fields)
        #print(diphotons.Diphoton.mass)
        lead_pt_cut = diphotons.LeadPhoton.pt >= options["lead_pt"]
        lead_pt_mgg_cut = (diphotons.LeadPhoton.pt / diphotons.Diphoton.mass) >= options["lead_pt_mgg"]
        sublead_pt_mgg_cut = (diphotons.SubleadPhoton.pt / diphotons.Diphoton.mass) >= options["sublead_pt_mgg"]
        mass_cut = (diphotons.Diphoton.mass >= options["mass"][0]) & (diphotons.Diphoton.mass <= options["mass"][1])
        all_cuts = lead_pt_cut & lead_pt_mgg_cut & sublead_pt_mgg_cut & mass_cut

        if options["nocuts"]:
            for objects, name in zip(
                    [lead_pt_cut, lead_pt_mgg_cut, sublead_pt_mgg_cut, mass_cut, all_cuts],
                    ["lead_pt_cut", "lead_pt_mgg_cut", "sublead_pt_mgg_cut", "mass_cut", "all_cuts"]):
                diphotons[("Diphoton", name)] = objects

        else:
            self.register_cuts(
                names = ["lead pt cut", "lead pt mgg cut", "sublead pt mgg cut", "mass cut", "all cuts"],
                results = [lead_pt_cut, lead_pt_mgg_cut, sublead_pt_mgg_cut, mass_cut, all_cuts],
                cut_type = "diphoton"
            )
            diphotons = diphotons[all_cuts]

        # Sort by sumPt
        diphotons = diphotons[awkward.argsort(diphotons.Diphoton.sumPt, ascending=False, axis=1)]
        # Select highest pt sum diphoton
        if options["select_highest_pt_sum"]:
            logger.debug("[DiphotonTagger : produce_and_select_diphotons] %s, selecting the highest pt_sum diphoton pair from each event." % (self.name))

            n_diphotons_total = awkward.sum(awkward.num(diphotons))
            diphotons = awkward.singletons(awkward.firsts(diphotons)) # ak.firsts takes the first diphoton in each event (highest sumpt) and ak.singletons makes it variable length again
            n_diphotons_selected = awkward.sum(awkward.num(diphotons)) 

            logger.debug("[DiphotonTagger : produce_and_select_diphotons] %s, syst variation : %s. Number of total diphoton candidates: %d, number of diphoton candidates after selecting candidate with highest pt sum in each event: %d (%.2f percent of diphoton events removed)." % (self.name, self.current_syst, n_diphotons_total, n_diphotons_selected, 100. * (float(n_diphotons_total - n_diphotons_selected) / float(n_diphotons_total))))

        # Otherwise, keep all diphotons
        else:
            logger.debug("[DiphotonTagger : produce_and_select_diphotons] %s, keeping all diphoton candidates in each event." % (self.name))
            avg_diphotons = awkward.mean(awkward.num(diphotons))
            logger.debug("[DiphotonTagger : produce_and_select_diphotons] %s, syst variation : %s, %.4f diphotons per event for events with at least 1 diphoton)." % (self.name, self.current_syst, avg_diphotons)) 


        # Reshape events to have shape [n_events, n_diphotons_per_event] and then flatten.
        # This is necessary so event-level variables are properly copied for each diphoton per event
        dipho_events = awkward.broadcast_arrays(events, diphotons.Diphoton.mass)[0]
        print("hola",dipho_events)

        # Add to events
        for field in ["Diphoton", "LeadPhoton", "SubleadPhoton"]:
            dipho_events[field] = diphotons[field] 
            dipho_events[(field, "pt")] = diphotons[field].pt
            dipho_events[(field, "eta")] = diphotons[field].eta
            dipho_events[(field, "phi")] = diphotons[field].phi
            dipho_events[(field, "mass")] = diphotons[field].mass

        dipho_presel_cut = awkward.num(dipho_events.Diphoton) >= 1
        if self.is_data and self.year is not None:
            trigger_cut = awkward.num(dipho_events.Diphoton) < 0 # dummy cut, all False
            for hlt in self.options["trigger"][self.year]: # logical OR of all triggers
                trigger_cut = (trigger_cut) | (dipho_events[hlt] == True)
        else:
            trigger_cut = awkward.num(dipho_events.Diphoton) >= 0 # dummy cut, all True

        presel_cut = dipho_presel_cut & trigger_cut

        if options["nocuts"]:

            if not options["select_highest_pt_sum"]:
                raise RuntimeError("nocuts option works only with select_highest_pt_sum enabled")
            
            for objects, name in zip(
                    [dipho_presel_cut, trigger_cut, presel_cut],
                    ["dipho_presel_cut", "trigger_cut", "presel_cut"]):
                dipho_events[("Diphoton",name)] = objects
            dipho_events = awkward.firsts(dipho_events)#keep Nones

            for field in ["Diphoton", "LeadPhoton", "SubleadPhoton"]:
                events[field] = dipho_events[field] 
                events[(field, "pt")] = dipho_events[(field, "pt")]
                events[(field, "eta")] = dipho_events[(field, "eta")]
                events[(field, "phi")] = dipho_events[(field, "phi")]
                events[(field, "mass")] = dipho_events[(field, "mass")]

            dipho_events = events
            awkward_utils.add_object_fields(
                events = dipho_events,
                name = "photon",
                objects = photons,
                n_objects = 4,
                dummy_value = -999,
            )
            #print("awkward.sum(awkward.is_none(events.weight_central))", awkward.sum(awkward.is_none(events.weight_central)) )
            #print("events.weight_central", events.weight_central )
            dipho_events["weight_central"] = events.weight_central
            #print("dipho_events.weight_central", dipho_events.weight_central )
            #print("awkward.sum(awkward.is_none(dipho_events.weight_central))",awkward.sum(awkward.is_none(dipho_events.weight_central)))
        else:
            self.register_cuts(
                names = ["At least 1 diphoton pair", "HLT Trigger", "all"],
                results = [dipho_presel_cut, trigger_cut, presel_cut]
            )
            dipho_events = dipho_events[presel_cut]
            dipho_events = awkward.flatten(dipho_events)#drop Nones

        elapsed_time = time.time() - start
        logger.debug("[DiphotonTagger] %s, syst variation : %s, total time to execute select_diphotons: %.6f s" % (self.name, self.current_syst, elapsed_time))

        dummy_cut = dipho_events.Diphoton.pt > 0
        dummy_cut = awkward.where(awkward.is_none(dummy_cut), awkward.is_none(dummy_cut), dummy_cut)



        return dummy_cut, dipho_events 

    def calculate_gen_info(self, diphotons, options):
        """
        Calculate gen info, adding the following fields to the events array:
            GenHggHiggs : [pt, eta, phi, mass, dR]
            GenHggLeadPhoton : [pt, eta, phi, mass, dR, pt_diff]
            GenHggSubleadPhoton : [pt, eta, phi, mass, dR, pt_diff]
            LeadPhoton : [gen_dR, gen_pt_diff]
            SubleadPhoton : [gen_dR, gen_pt_diff]

        Perform both matching of
            - closest gen photons from Higgs to reco lead/sublead photons from diphoton candidate
            - closest reco photons to gen photons from Higgs

        If no match is found for a given reco/gen photon, it will be given values of -999. 
        """
        gen_hgg = gen_selections.select_x_to_yz(diphotons.GenPart, 25, 22, 22)
        
        awkward_utils.add_object_fields(
                events = diphotons,
                name = "GenHggHiggs",
                objects = gen_hgg.GenParent,
                n_objects = 1
        )

        awkward_utils.add_object_fields(
                events = diphotons,
                name = "GenHggLeadPhoton",
                objects = gen_hgg.LeadGenChild,
                n_objects = 1
        )

        awkward_utils.add_object_fields(
                events = diphotons,
                name = "GenHggSubleadPhoton",
                objects = gen_hgg.SubleadGenChild,
                n_objects = 1
        )

        return diphotons 
        

    def select_photons(self, photons, rho, options):
        """
        Enforces all photon cuts that are commmon to both
        leading and subleading photons in the diphoton preselection.
        Cuts specific to a diphoton pair are not enforced here.

        :param photons: input collection of photons to use for calculating selected photons
        :type photons: awkward.highlevel.Array
        :param rho: energy density in each event, used for corrections to photon isolation cuts
        :type rho: awkward.highlevel.Array
        :param options: dictionary containing configurable options for the photon selection
        :type options: dict
        :return: boolean array indicating which photons pass the photon selection
        :rtype: awkward.highlevel.Array
        """
        # pt
        pt_cut = photons.pt > options["pt"]

        # eta
        #eta_cut = Tagger.get_range_cut(abs(photons.eta), options["eta"]) | (photons.isScEtaEB | photons.isScEtaEE)
        eta_cut = (photons.isScEtaEB | photons.isScEtaEE)

        # electron veto
        e_veto_cut = photons.electronVeto > options["e_veto"]

        use_central_nano = options["use_central_nano"] # indicates whether we are using central nanoAOD (with some branches that are necessary for full diphoton preselection missing) or custom nanoAOD (with these branches added)

        # r9/isolation cut
        r9_cut = photons.r9 > options["r9"]

        if not use_central_nano:
            charged_iso_cut = photons.chargedHadronIso < options["charged_iso"]
            charged_rel_iso_cut = (photons.chargedHadronIso / photons.pt) < options["charged_rel_iso"]

        else: # FIXME: to be deleted once Photon.chargedHadronIso is added to central nanoAOD
            charged_iso_cut = (photons.pfRelIso03_chg * photons.pt) < options["charged_iso"]
            charged_rel_iso_cut = photons.pfRelIso03_chg < options["charged_rel_iso"]

        r9_iso_cut = r9_cut | charged_iso_cut | charged_rel_iso_cut

        # hadronic over em energy cut
        hoe_cut = photons.hoe < options["hoe"]

        # hlt-mimicking cuts
        photons_eb_high_r9 = photons.isScEtaEB & (photons.r9 > options["hlt"]["eb_high_r9"]["r9"]) 
        photons_eb_low_r9 = photons.isScEtaEB & (photons.r9 > options["hlt"]["eb_low_r9"]["r9"]) & (photons.r9 < options["hlt"]["eb_high_r9"]["r9"])

        photons_ee_high_r9 = photons.isScEtaEE & (photons.r9 > options["hlt"]["ee_high_r9"]["r9"])
        photons_ee_low_r9 = photons.isScEtaEE & (photons.r9 > options["hlt"]["ee_low_r9"]["r9"]) & (photons.r9 < options["hlt"]["ee_high_r9"]["r9"])

        if not use_central_nano:
            eb_low_r9_track_pt_cut = photons.trkSumPtHollowConeDR03 < options["hlt"]["eb_low_r9"]["track_sum_pt"]
            ee_low_r9_track_pt_cut = photons.trkSumPtHollowConeDR03 < options["hlt"]["ee_low_r9"]["track_sum_pt"]

        else: # FIXME: to be deleted once Photon.trkSumPtHollowConeDR03 is added to central nanoAOD
            eb_low_r9_track_pt_cut = photons.pt > 0
            ee_low_r9_track_pt_cut = photons.pt > 0

        eb_low_r9_sigma_ieie_cut = photons.sieie < options["hlt"]["eb_low_r9"]["sigma_ieie"]
        ee_low_r9_sigma_ieie_cut = photons.sieie < options["hlt"]["ee_low_r9"]["sigma_ieie"]

        low_eta = abs(photons.eta) < options["hlt"]["eta_rho_corr"]

        if not use_central_nano:
            eb_low_r9_pho_iso_low_eta_cut = low_eta & (photons.photonIso - rho * options["hlt"]["low_eta_rho_corr"] < options["hlt"]["eb_low_r9"]["pho_iso"]) 
            eb_low_r9_pho_iso_high_eta_cut = ~low_eta & (photons.photonIso - rho * options["hlt"]["high_eta_rho_corr"] < options["hlt"]["eb_low_r9"]["pho_iso"]) 
        else: # FIXME: to be deleted once Photon.photonIso is added to central nanoAOD
            eb_low_r9_pho_iso_low_eta_cut = low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["low_eta_rho_corr"]) < options["hlt"]["eb_low_r9"]["pho_iso"])
            eb_low_r9_pho_iso_high_eta_cut = ~low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["high_eta_rho_corr"]) < options["hlt"]["eb_low_r9"]["pho_iso"])

        eb_low_r9_pho_iso_cut = eb_low_r9_pho_iso_low_eta_cut | eb_low_r9_pho_iso_high_eta_cut

        if not use_central_nano:
            ee_low_r9_pho_iso_low_eta_cut = low_eta & (photons.photonIso - rho * options["hlt"]["low_eta_rho_corr"] < options["hlt"]["ee_low_r9"]["pho_iso"]) 
            ee_low_r9_pho_iso_high_eta_cut = ~low_eta & (photons.photonIso - rho * options["hlt"]["high_eta_rho_corr"] < options["hlt"]["ee_low_r9"]["pho_iso"]) 
        else: # FIXME: to be deleted once Photon.photonIso is added to central nanoAOD
            ee_low_r9_pho_iso_low_eta_cut = low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["low_eta_rho_corr"]) < options["hlt"]["ee_low_r9"]["pho_iso"])
            ee_low_r9_pho_iso_high_eta_cut = ~low_eta & ((photons.pfRelIso03_all * photons.pt * options["hlt"]["high_eta_rho_corr"]) < options["hlt"]["ee_low_r9"]["pho_iso"])
    
        ee_low_r9_pho_iso_cut = ee_low_r9_pho_iso_low_eta_cut | ee_low_r9_pho_iso_high_eta_cut

        hlt_cut = photons.pt < 0 # initialize to all False
        hlt_cut = hlt_cut | photons_eb_high_r9
        hlt_cut = hlt_cut | (photons_eb_low_r9 & eb_low_r9_track_pt_cut & eb_low_r9_sigma_ieie_cut & eb_low_r9_pho_iso_cut)
        hlt_cut = hlt_cut | photons_ee_high_r9
        hlt_cut = hlt_cut | (photons_ee_low_r9 & ee_low_r9_track_pt_cut & ee_low_r9_sigma_ieie_cut & ee_low_r9_pho_iso_cut)

        all_cuts = pt_cut & eta_cut & e_veto_cut & r9_iso_cut & hoe_cut & hlt_cut

        if options["nocuts"]:
            for objects, name in zip(
                    [pt_cut, eta_cut, e_veto_cut, r9_iso_cut, hoe_cut, hlt_cut, all_cuts], 
                    ["pt_cut", "eta_cut", "e_veto_cut", "r9_iso_cut", "hoe_cut", "hlt_cut", "all_cuts"]): 
                photons[name] = objects
                #awkward_utils.add_field(events, name, objects)
            dummyflag = (photons.pt>=0)
            return dummyflag,photons

        else:
            self.register_cuts(
                names = ["pt", "eta", "e_veto", "r9", "hoe", "hlt", "all"],
                results = [pt_cut, eta_cut, e_veto_cut, r9_iso_cut, hoe_cut, hlt_cut, all_cuts],
                cut_type = "photon"
            )
            return all_cuts,photons

# Below is an example of how the diphoton preselection could be performed with an explicit loop (C++ style) 
# that is compiled with numba for increased performance.

# NOTE: pre-compiled numba functions should be defined outside the class,
# as numba does not like when a class instance is passed to a function
@numba.njit
def produce_diphotons(photons, n_photons, lead_pt_cut, lead_pt_mgg_cut, sublead_pt_mgg_cut):
    n_events = len(photons)

    diphotons_offsets = numpy.zeros(n_events + 1, numpy.int64)
    diphotons_contents = []
    lead_photons_idx = []
    sublead_photons_idx = []

    # Loop through events and select diphoton pairs
    for i in range(n_events):
        n_diphotons_event = 0
        # Enumerate photon pairs
        if n_photons[i] >= 2: # only try if there are at least 2 photons
            sum_pt = 0
            for j in range(n_photons[i]):
                for k in range(j+1, n_photons[i]):
                    # Choose who is the leading photon
                    lead_idx = j if photons[i][j].pt > photons[i][k].pt else k
                    sublead_idx = k if photons[i][j].pt > photons[i][k].pt else j
                    lead_photon = photons[i][lead_idx]
                    sublead_photon = photons[i][sublead_idx]

                    # Lead photon must satisfy lead pt cut
                    if lead_photon.pt < lead_pt_cut:
                        continue

                    # Construct four vectors
                    lead_photon_vec = vector.obj(
                            pt = lead_photon.pt,
                            eta = lead_photon.eta,
                            phi = lead_photon.phi,
                            mass = lead_photon.mass
                    )
                    sublead_photon_vec = vector.obj(
                            pt = sublead_photon.pt,
                            eta = sublead_photon.eta,
                            phi = sublead_photon.phi,
                            mass = sublead_photon.mass
                    )
                    diphoton = vector.obj(px = 0., py = 0., pz = 0., E = 0.) # IMPORTANT NOTE: you need to initialize this to an empty vector first. Otherwise, you will get ZeroDivisionError exceptions for like 1 out of a million events (seemingly only with numba). 
                    diphoton = diphoton + lead_photon_vec + sublead_photon_vec

                    if (diphoton.mass < 40) | (diphoton.mass > 180):
                        continue

                    if lead_photon.pt / diphoton.mass < lead_pt_mgg_cut:
                        continue

                    if sublead_photon.pt / diphoton.mass < sublead_pt_mgg_cut:
                        continue

                    # This diphoton candidate passes
                    n_diphotons_event += 1

                    diphotons_contents.append([
                        diphoton.pt,
                        diphoton.eta,
                        diphoton.phi,
                        diphoton.mass
                    ])

                    lead_photons_idx.append(lead_idx)
                    sublead_photons_idx.append(sublead_idx)

        diphotons_offsets[i+1] = diphotons_offsets[i] + n_diphotons_event

    return diphotons_offsets, numpy.array(diphotons_contents), numpy.array(lead_photons_idx), numpy.array(sublead_photons_idx)
