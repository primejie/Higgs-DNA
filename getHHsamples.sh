
outputfile="samples2.json"
preamblefile="/tmp/fmonti/preamble.json"
postamblefile="/tmp/fmonti/postamble.json"
cat <<EOF > ${preamblefile}
        "xs" : 1.0,
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

for sample in GluGluToBulkGravitonToHHTo2G4Q GluGluToBulkGravitonToHHTo2G2l2nu GluGluToBulkGravitonToHHTo2G2Qlnu GluGluToBulkGravitonToHHTo2G2ZTo2G4Q GluGluToBulkGravitonToHHTo2B2G; do
#for sample in GluGluToBulkGravitonToHHTo2G2ZTo2G4Q GluGluToBulkGravitonToHHTo2B2G; do
    echo doing $sample
    echo >> $outputfile
    for mass in 1000 1250 1500 1750 2000 2500 3000; do
    #for mass in 1250 2000; do
	echo >> $outputfile 
	echo mass $mass 
 
	samplename=${sample}_M-${mass}
	samplelabel=${sample}_M${mass}
	echo '    "'$samplelabel'" : {'       >> $outputfile
	cat ${preamblefile}                   >> $outputfile

	echo '            "2016" : ['         >> $outputfile
	if [ $sample = "GluGluToBulkGravitonToHHTo2B2G" ]; then
            dasgoclient -query="file dataset=/${samplename}_narrow_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1/NANOAODSIM" >>  $outputfile
	else
	    dasgoclient -query="file dataset=/${samplename}_narrow_TuneCUETP8M1_PSWeights_13TeV-madgraph-pythia8/RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1/NANOAODSIM" >>  $outputfile
	fi
	echo '            ],'                >> $outputfile

	echo '            "2017" : ['         >> $outputfile
	if [ $sample = "GluGluToBulkGravitonToHHTo2B2G" ]; then
            dasgoclient -query="file dataset=/${samplename}_narrow_TuneCP5_13TeV-madgraph-pythia8_correctedcfg/RunIIFall17NanoAODv7-PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/NANOAODSIM" >>  $outputfile
	else
	    dasgoclient -query="file dataset=/${samplename}_narrow_TuneCP5_PSWeights_13TeV-madgraph-pythia8/RunIIFall17NanoAODv7-PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/NANOAODSIM" >>  $outputfile
	fi
	echo '            ],'                >> $outputfile

	echo '            "2018" : ['         >> $outputfile
	dasgoclient -query="file dataset=/${samplename}_narrow_TuneCP5_PSWeights_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM" >>  $outputfile
	echo '            ]'                 >> $outputfile

	cat ${postamblefile}                  >> $outputfile

    done
done 


echo '}' >> $outputfile
