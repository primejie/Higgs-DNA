dir=$1
work=$PWD
for job in `ls $dir/job_* -d` 
do
# echo ${job##*/}
jobname=${job##*/}
jobnumber=${jobname#*_}
if [ ! -f "$dir/$jobname/output_${jobname}_nominal.parquet" ]; then

if [ ! -f "$dir/$jobname/${dir}_config_job${jobnumber}bak.json" ]; then
# echo $jobnumber

# cp $dir/$jobname/${dir}_config_job${jobnumber}.json  $dir/$jobname/${dir}_config_job${jobnumber}bak.json
# fi
# cp $dir/$jobname/${dir}_config_job${jobnumber}bak.json  $dir/$jobname/${dir}_config_job${jobnumber}.json

# xrdrootfile=`grep root $dir/$jobname/${dir}_config_job${jobnumber}.json`
# rootfile=${xrdrootfile%*\"}
# rootfile=${rootfile#*\"}
# echo $rootfile
fi
fi
done
# rootname=${rootfile##*/}

# mkdir /eos/user/z/zhjie/dataroot/2016/$1/ -p 
# if [  -f "/eos/user/z/zhjie/dataroot/2016/$1/${rootname}" ]; then
# echo "The file exists"
# else
# echo "xrdcp $rootfile /eos/user/z/zhjie/dataroot/2016/$1/"
# xrdcp -f $rootfile /eos/user/z/zhjie/dataroot/2016/$1/
# fi


# sed -i "s#$rootfile#/eos/user/z/zhjie/dataroot/2016/$1/${rootname}#g" $dir/$jobname/${dir}_config_job${jobnumber}.json 
# fi
# done