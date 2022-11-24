dir=$1
work=$PWD
for job in `ls $dir/job_* -d` 
do
echo ${job#*/}
jobname=${job#*/}
jobnumber=${jobname#*_}
if [ ! -f "$dir/$jobname/output_${jobname}_nominal.parquet" ]; then
# echo "No such file, need resubmit"
if [ ! -f "$dir/$jobname/${dir}_config_job${jobnumber}bak.json" ]; then
# echo "copy the original file as bak"
cp $dir/$jobname/${dir}_config_job${jobnumber}.json  $dir/$jobname/${dir}_config_job${jobnumber}bak.json
fi
cp $dir/$jobname/${dir}_config_job${jobnumber}bak.json  $dir/$jobname/${dir}_config_job${jobnumber}.json
# echo "Now finding the input root file"
xrdrootfile=`grep root $dir/$jobname/${dir}_config_job${jobnumber}.json`
rootfile=${xrdrootfile%*\"}
rootfile=${rootfile#*\"}
# echo ${rootfile}
# echo "Now trying to xrdcp the file to eos"
rootname=${rootfile##*/}
# echo $rootname
mkdir /eos/cms/store/group/phys_higgs/resonant_HH/RunII/tmp/$1/ -p 
if [  -f "/eos/cms/store/group/phys_higgs/resonant_HH/RunII/tmp/$1/${rootname}" ]; then
# rm /eos/cms/store/group/phys_higgs/resonant_HH/RunII/tmp/$1/${rootname}
echo "The file exists"
else
echo "xrdcp $rootfile /eos/cms/store/group/phys_higgs/resonant_HH/RunII/tmp/$1/"
xrdcp -f $rootfile /eos/cms/store/group/phys_higgs/resonant_HH/RunII/tmp/$1/
fi


sed -i "s#$rootfile#/eos/cms/store/group/phys_higgs/resonant_HH/RunII/tmp/$1/${rootname}#g" $dir/$jobname/${dir}_config_job${jobnumber}.json 
# cp sub_template.sub /afs/cern.ch/user/c/chuw/chuw/ResonantAnalysis/HiggsDNA/sub_template_run_${1}_${jobnumber}.sub
# sed -i "s#MYSAMPLE#$1#g"  /afs/cern.ch/user/c/chuw/chuw/ResonantAnalysis/HiggsDNA/sub_template_run_${1}_${jobnumber}.sub
# sed -i "s#MYJOBNAME#$jobname#g"  /afs/cern.ch/user/c/chuw/chuw/ResonantAnalysis/HiggsDNA/sub_template_run_${1}_${jobnumber}.sub
# sed -i "s#MYJOBNUMBER#job$jobnumber#g"  /afs/cern.ch/user/c/chuw/chuw/ResonantAnalysis/HiggsDNA/sub_template_run_${1}_${jobnumber}.sub
# cd /afs/cern.ch/user/c/chuw/chuw/ResonantAnalysis/HiggsDNA/ 
# condor_submit  /afs/cern.ch/user/c/chuw/chuw/ResonantAnalysis/HiggsDNA/sub_template_run_${1}_${jobnumber}.sub
# cd ${work}
fi
done