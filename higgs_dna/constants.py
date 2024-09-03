CENTRAL_WEIGHT = "weight_central" # name of the central weight branch
NOMINAL_TAG = "nominal" # name of the nominal events (relevant when we have multiple sets of events corresponding to systematics with independent collections)

# FIXME: need to add 2016 pre/post VFP split for UL
LUMI = {
    "2016" : 35.9,
    "2016preVFP" : 19.48, # 2016 APV
    "2016postVFP" : 16.76, # 2016
    "2017" : 41.5,
    "2018" : 59.8
}

# nanoAOD branches to always include
BRANCHES = {
    "data" : {
        "2016" : [
            "HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90",
        ],
        "2016postVFP" : [
            "HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90",
        ],
        "2016preVFP" : [
            "HLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90",
        ],
        "2017" : [
            "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90",
        ],
        "2018" : [
            "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90",
        ],
        "any" : []
    },
    "mc" : {
        "2016" : [],
        "2016preVFP" : [],
        "2016postVFP" : [],
        "2017" : [],
        "2018" : [],
        "any" : []
    }
}
