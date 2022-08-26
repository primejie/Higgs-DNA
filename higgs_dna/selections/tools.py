import awkward
# from ROOT import TLorentzVector
import logging

import vector
from higgs_dna.utils import awkward_utils, misc_utils
vector.register_awkward()

import numpy
import numba
logger = logging.getLogger(__name__)
import math
from higgs_dna.selections import object_selections
from higgs_dna.utils import misc_utils
def Boost(bx,by,bz,obj1):
    # if awkward.count(objects1) == 0:
    #    return objects1.pt < 0.  
    # if not isinstance(objects1, vector.Vector4D):
        # objects1 = awkward.Array(objects1, with_name = "Momentum4D")
    # obj1 = awkward.unflatten(objects1, counts = 1, axis = -1) # shape [n_events, n_obj, 1]
    b2=bx*bx + by*by + bz*bz
    gamma = 1.0 / numpy.sqrt(1.0 - b2)
    bp = bx*(obj1.px) + by*(obj1.py) + bz*(obj1.pz)
    if any(b2) > 0 : 
        gamma2=(gamma - 1.0)/b2
    else:
        gamma2=0.0
    boosted_px1=obj1.px+gamma2*bp*bx+ gamma*bx*obj1.e
    boosted_py1=obj1.py+gamma2*bp*by+ gamma*by*obj1.e
    boosted_pz1=obj1.pz+gamma2*bp*bz+ gamma*bz*obj1.e
    return boosted_px1,boosted_py1,boosted_pz1
def getCosTheta_old(objects1,objects2):
    if awkward.count(objects1) == 0 or awkward.count(objects2) == 0:
        return objects1.pt < 0. 

    if not isinstance(objects1, vector.Vector4D):
        objects1 = awkward.Array(objects1, with_name = "Momentum4D")
    if not isinstance(objects2, vector.Vector4D):
        objects2 = awkward.Array(objects2, with_name = "Momentum4D")

    obj1 = awkward.unflatten(objects1, counts = 1, axis = -1) # shape [n_events, n_obj, 1]
    obj2 = awkward.unflatten(objects2, counts = 1, axis = 0) # shape [n_events, 1, n_obj]
    obj=obj1+obj2
    E=obj.e
    bx=-(obj.px)/E
    by=-(obj.py)/E
    bz=-(obj.pz)/E
    boosted_px1,boosted_py1,boosted_pz1=Boost(bx,by,bz,obj1)
    # b2 = bx*bx + by*by + bz*bz
    # gamma = 1.0 / numpy.sqrt(1.0 - b2)
    # bp = bx*(obj1.px) + by*(obj1.py) + bz*(obj1.pz)
    # if any(b2) > 0 : 
    #     gamma2=(gamma - 1.0)/b2
    # else:
    #     gamma2=0.0
    p=numpy.sqrt(boosted_px1*boosted_px1+boosted_py1*boosted_py1+boosted_pz1*boosted_pz1)
    return awkward.flatten(abs(boosted_pz1/p))

def getCosTheta(objects1,objects2):
    if awkward.count(objects1) == 0 or awkward.count(objects2) == 0:
        return objects1.pt < 0. 

    if not isinstance(objects1, vector.Vector4D):
        objects1 = awkward.Array(objects1, with_name = "Momentum4D")
    if not isinstance(objects2, vector.Vector4D):
        objects2 = awkward.Array(objects2, with_name = "Momentum4D")

    obj1 = awkward.unflatten(objects1, counts = 1, axis = -1) # shape [n_events, n_obj, 1]
    obj2 = awkward.unflatten(objects2, counts = 1, axis = 0) # shape [n_events, 1, n_obj]
    obj=obj1+obj2
    E=obj.e
    bx=-(obj.px)/E
    by=-(obj.py)/E
    bz=-(obj.pz)/E
    boost_vec=vector.obj(px=bx,py=by,pz=bz)
    obj1=obj1.boost(boost_vec)
    # b2 = bx*bx + by*by + bz*bz
    # gamma = 1.0 / numpy.sqrt(1.0 - b2)
    # bp = bx*(obj1.px) + by*(obj1.py) + bz*(obj1.pz)
    # if any(b2) > 0 : 
    #     gamma2=(gamma - 1.0)/b2
    # else:
    #     gamma2=0.0
    p=numpy.sqrt(obj1.px*obj1.px+obj1.py*obj1.py+obj1.pz*obj1.pz)
    return awkward.flatten(abs(obj1.pz/p))

def getCosThetaStar_CS_old(ebeam,objects1,objects2):#Obj1 Diphoton, Obj2 Jet
    if awkward.count(objects1) == 0 or awkward.count(objects2) == 0:
        return objects1.pt < 0. 

    if not isinstance(objects1, vector.Vector4D):
        objects1 = awkward.Array(objects1, with_name = "Momentum4D")
    if not isinstance(objects2, vector.Vector4D):
        objects2 = awkward.Array(objects2, with_name = "Momentum4D")
    obj1 = awkward.unflatten(objects1, counts = 1) # shape [n_events, n_obj, 1]
    obj2 = awkward.unflatten(objects2, counts = 1) # shape [n_events, 1, n_obj]
    obj=obj1+obj2 #obj could be HH condidate    
    E=obj.e
    bx=-(obj.px)/E
    by=-(obj.py)/E
    bz=-(obj.pz)/E
    boost_vec=vector.obj(px=bx,py=by,pz=bz)
    beam1=vector.obj(px=0, py=0, pz=ebeam, E=ebeam)
    beam2=vector.obj(px=0, py=0, pz=-ebeam, E=ebeam)
    beam1=beam1.boost(boost_vec)
    beam2=beam2.boost(boost_vec)
    beam1_3vec=vector.obj(px=beam1.px,py=beam1.py,pz=beam1.pz)
    beam2_3vec=vector.obj(px=beam2.px,py=beam2.py,pz=beam2.pz)
    CSaxis=beam1_3vec.unit()-beam2_3vec.unit()
    obj1=obj1.boost(boost_vec)
    obj1_3vec=vector.obj(px=obj1.px,py=obj1.py,pz=obj1.pz)
    cos=obj1_3vec.unit().dot(CSaxis)/1*numpy.sqrt(CSaxis.px*CSaxis.px+CSaxis.py*CSaxis.py+CSaxis.pz*CSaxis.pz)
    return awkward.flatten(fabs(cos))


def getPhoJetDr(Jet,LeadPhoton,SubleadPhoton):

    if not isinstance(Jet, vector.Vector4D):
        Jet = awkward.Array(Jet, with_name = "Momentum4D")
    if not isinstance(LeadPhoton, vector.Vector4D):
        LeadPhoton = awkward.Array(LeadPhoton, with_name = "Momentum4D")
    if not isinstance(LeadPhoton, vector.Vector4D):
        SubleadPhoton = awkward.Array(SubleadPhoton, with_name = "Momentum4D")
    print(len(Jet))
    jet = awkward.unflatten(Jet, counts = 1) # shape [n_events, n_obj, 1]
    lead_photon = awkward.unflatten(LeadPhoton, counts = 1)  # shape [n_events, 1, n_obj]
    sublead_photon = awkward.unflatten(SubleadPhoton, counts = 1)  # shape [n_events, 1, n_obj]
    lead_pho_jet_dr=awkward.flatten(jet.deltaR(lead_photon))
    sublead_pho_jet_dr=awkward.flatten(jet.deltaR(sublead_photon))
    # print(lead_pho_jet_dr)
    # print(sublead_pho_jet_dr)
    dr_list=list(zip(lead_pho_jet_dr,sublead_pho_jet_dr))
    #     print(dr_list)
    min_dr=[]
    max_dr=[]
    for drs in dr_list:
#         print(min(drs))
        min_dr.append(min(drs))
        max_dr.append(max(drs))
#     print(min_dr)
    return min_dr,max_dr
    # return lead_pho_jet_dr,sublead_pho_jet_dr

def getCosThetaStar_CS(objects1,objects2):#Obj1 Diphoton, Obj2 Jet
    obj1 = vector.obj(px = 0., py = 0., pz = 0., E = 0.)
    obj2 = vector.obj(px = 0., py = 0., pz = 0., E = 0.)
    print(awkward.count(objects2))
    if awkward.count(objects1) == 0 or awkward.count(objects2) == 0:
        return objects1.pt < 0. 

    if not isinstance(objects1, vector.Vector4D):
        objects1 = awkward.Array(objects1, with_name = "Momentum4D")
    if not isinstance(objects2, vector.Vector4D):
        objects2 = awkward.Array(objects2, with_name = "Momentum4D")

    obj1 = awkward.unflatten(objects1, counts = 1) # shape [n_events, n_obj, 1]
#     obj1 = awkward.singletons(awkward.firsts(obj1))
    obj2 = awkward.unflatten(objects2, counts = 1)  # shape [n_events, 1, n_obj]
    # print(obj1)
    # print(obj2)
    # print(obj1.px)
    # print(obj1.py)
    # print(obj1.pz)
    # print(obj1.e)
    
    # print(obj2.px)
    # print(obj2.py)
    # print(obj2.pz)
    # print(obj2.e)
    obj=obj1+obj2 #obj could be HH condidate    
    E=obj.e
    bx=-(obj.px)/E
    by=-(obj.py)/E
    bz=-(obj.pz)/E
    # print(obj.px)
    # print(obj.py)
    # print(obj.pz)
    # print(obj.e)
    boost_vec=vector.obj(px=bx,py=by,pz=bz)
    # beam1=vector.obj(px=0, py=0, pz=ebeam, E=ebeam)
    # beam2=vector.obj(px=0, py=0, pz=-ebeam, E=ebeam)
    # beam1=beam1.boost(boost_vec)
    # beam2=beam2.boost(boost_vec)
    # beam1_3vec=vector.obj(px=beam1.px,py=beam1.py,pz=beam1.pz)
    # beam2_3vec=vector.obj(px=beam2.px,py=beam2.py,pz=beam2.pz)
    # CSaxis=beam1_3vec.unit()-beam2_3vec.unit()
    obj1=obj1.boost(boost_vec)
    # obj1_3vec=vector.obj(px=obj1.px,py=obj1.py,pz=obj1.pz)
    # cos=obj1_3vec.unit().dot(CSaxis)/1*numpy.sqrt(CSaxis.px*CSaxis.px+CSaxis.py*CSaxis.py+CSaxis.pz*CSaxis.pz)
    p=numpy.sqrt(obj1.px*obj1.px+obj1.py*obj1.py+obj1.pz*obj1.pz)
    return awkward.flatten(abs(obj1.pz/p))
def FillWithDummy(events,inputlist,Dummy,fieldname,cut_var,cut_val):
    j=0
    outlist=[]
#     print (inputlist)
    for i in range(0,len(events)):
        if (events[i][cut_var]!=cut_val):
            outlist.append(Dummy)
        else:
            outlist.append(inputlist[j])
            j=j+1
    print(len(outlist))
    awkward_utils.add_field(events, fieldname, awkward.Array(outlist))


