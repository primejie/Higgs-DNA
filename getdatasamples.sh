
outputfile="SINGLEHsamples.json"
preamblefile="/tmp/fmonti/preamble.json"
postamblefile="/tmp/fmonti/postamble.json"
cat <<EOF > ${preamblefile}
        "bf" : 0.00227,
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
    ['GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8']='48.5800' \
    ['GluGluHToGG_M-125_13TeV_powheg_pythia8']='48.5800' \
    ['VBFHToGG_M-125_13TeV_powheg_pythia8']='3.7820' \
    ['VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8']='2.257' \
    ['ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8']='0.5071' \
    ['THQ_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5']='0.07425' \
    ['VBFHToGG_M125_13TeV_amcatnlo_pythia8']='3.7820')

echo
echo "the following cross sections will be used"
for xs in "${!crosssections[@]}"; do echo "$xs - ${crosssections[$xs]}"; done
echo

for sample in \
    GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8 \
    GluGluHToGG_M-125_13TeV_powheg_pythia8 \
    VBFHToGG_M-125_13TeV_powheg_pythia8 \
    VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8 \
    ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8 \
    THQ_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5 \
    VBFHToGG_M125_13TeV_amcatnlo_pythia8; do

    samplename2016=$sample
    samplename2017=$sample
    samplename2018=$sample
    samplelabel=${sample/"_TuneCP5"/""}

    version2016="RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1"
    version2017="RunIIFall17NanoAODv7-PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1"
    version2018="RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1"
    if [ $sample = "THQ_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCP5" ]; then
	samplename2016="THQ_ctcvcp_HToGG_M125_13TeV-madgraph-pythia8_TuneCUETP8M1_v2"
	samplename2018="THQ_ctcvcp_HToGG_M125_TuneCP5_13TeV-madgraph-pythia8"
    elif [ $sample = "GluGluHToGG_M-125_13TeV_powheg_pythia8" ]; then
	version2016="RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1"
    elif [ $sample = "VBFHToGG_M-125_13TeV_powheg_pythia8" ]; then
	version2016="RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1"
    elif [ $sample = "ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8" ]; then
	samplename2016="ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_v2"
    elif [ $sample = "GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8" ]; then
	version2016="RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8_ext2-v1"
	samplename2018="GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8"
    elif [ $sample = "VBFHToGG_M125_13TeV_amcatnlo_pythia8" ]; then
	version2016="RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8_ext2-v1"
    fi

    echo doing $sample

    echo >> $outputfile
    echo '    "'$samplelabel'" : {'                    >> $outputfile
    echo '        "xs" : '${crosssections[$sample]}',' >> $outputfile
    cat ${preamblefile}                                >> $outputfile

    echo '            "2016" : ['         >> $outputfile
    dasgoclient -query="file dataset=/${samplename2016}/${version2016}/NANOAODSIM" >>  $outputfile
    echo '            ],'                >> $outputfile

    echo '            "2017" : ['         >> $outputfile
    dasgoclient -query="file dataset=/${samplename2017}/${version2017}/NANOAODSIM" >>  $outputfile
    echo '            ],'                >> $outputfile

    echo '            "2018" : ['         >> $outputfile
    dasgoclient -query="file dataset=/${samplename2018}/${version2018}/NANOAODSIM" >>  $outputfile
    echo '            ]'                 >> $outputfile

    cat ${postamblefile}                  >> $outputfile

done 

echo '}' >> $outputfile

sed -i 's&.root&.root",&g' $outputfile
sed -i -z 's&.root",\n            ]&.root"\n            ]&g' $outputfile
sed -i 's&/store/&                "root://cms-xrd-global.cern.ch///store/&g' $outputfile
