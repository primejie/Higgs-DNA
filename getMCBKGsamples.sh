
outputfile="BKGsamples.json"
preamblefile="/tmp/fmonti/preamble.json"
postamblefile="/tmp/fmonti/postamble.json"
cat <<EOF > ${preamblefile}
        "bf" : 1.0,
        "files" : {
EOF

cat <<EOF > ${postamblefile}
        },
        "systematics" : {
            "weights" : {
                "dummy_ttH_theory_sf" : {
                    "type" : "event",
                    "method" : "from_branch",
                    "branches" : { "central" : "genWeight", "up" : "genWeight", "down" : "genWeight" },
                    "modify_central_weight" : false
                }
            }
        }
    },
EOF

echo '{' > $outputfile

declare -A crosssections=( \
    ['DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa']='84.4' \
    ['GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8']='872.1' \
    ['GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8']='862.4' \
#    ['GJets_DR-0p4_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_v2']='' \
#    ['GJets_DR-0p4_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_v2']='' \
#    ['GJets_DR-0p4_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_v2']='' \
#    ['GJets_DR-0p4_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8']='' \
    ['QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8']='24810.0' \
    ['QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8']='22110.0' \
    ['QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8']='118100.0' \
    ['QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8']='113400.0' \
    ['TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8']='831.76' \
    ['TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8']='511.3' \
    ['TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8']='3.055' \
    ['TGJets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8']='2.967' \
    ['TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8']='4.078' \
    ['TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8']='3.819' \
    ['TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8']='0.01687' \
    ['TTGG_0Jets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8']='0.01731' )

echo "the following cross sections will be used"
for sound in "${!crosssections[@]}"; do echo "$sound - ${crosssections[$sound]}"; done



for sample in \
    DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa \
    GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8 \
    QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8 \
    QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCP5_13TeV_Pythia8 \
    TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8 \
    TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8 \
    TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8 \
    TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8; do
    #    GJets_DR-0p4_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8_v2 \
    #    GJets_DR-0p4_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8_v2 \
    #    GJets_DR-0p4_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_v2 \
    #    GJets_DR-0p4_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8 \

    version2016="RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1"
    version2017="RunIIFall17NanoAODv7-PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1"
    version2018="RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1"

    echo doing $sample
    echo >> $outputfile
    samplename=${sample}
    samplelabel=${sample}
    samplelabel=${samplelabel/"_TuneCP5_13TeV_Pythia8"/""}
    samplelabel=${samplelabel/"_TuneCUETP8M1_13TeV_Pythia8"/""}
    echo '    "'$samplelabel'" : {'                    >> $outputfile
    echo '        "xs" : '${crosssections[$sample]}',' >> $outputfile
    cat ${preamblefile}                                >> $outputfile

    echo '            "2016" : ['         >> $outputfile
    samplename2016=$samplename

    if [ $sample = "TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8" ]; then
	version2016="RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1"
	version2017="RunIIFall17NanoAODv7-PU2017_12Apr2018_Nano02Apr2020_new_pmx_102X_mc2017_realistic_v8-v1"
	version2018="RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext2-v1"
	samplename2016=${samplename/"TuneCP5"/"TuneCP5_PSweights"}
    elif [ $sample = "TGJets_TuneCP5_13TeV_amcatnlo_madspin_pythia8" ]; then
	version2016="RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8_ext1-v1"
	samplename2016=${samplename/"TuneCP5"/"TuneCUETP8M1"}
    else
	samplename2016=${samplename/"TuneCP5"/"TuneCUETP8M1"}
    fi	

    dasgoclient -query="file dataset=/${samplename2016}/${version2016}/NANOAODSIM" >>  $outputfile
    echo '            ],'                >> $outputfile

    echo '            "2017" : ['         >> $outputfile
    dasgoclient -query="file dataset=/${samplename}/${version2017}/NANOAODSIM" >>  $outputfile
    echo '            ],'                >> $outputfile

    echo '            "2018" : ['         >> $outputfile
    dasgoclient -query="file dataset=/${samplename}/${version2018}/NANOAODSIM" >>  $outputfile
    echo '            ]'                 >> $outputfile

    cat ${postamblefile}                  >> $outputfile

done 

echo '}' >> $outputfile

sed -i 's&.root&.root",&g' $outputfile
sed -i -z 's&.root",\n            ]&.root"\n            ]&g' $outputfile
sed -i 's&/store/&                "root://cms-xrd-global.cern.ch///store/&g' $outputfile
