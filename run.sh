#echo "0-signal   1-singleH  2-bkg"
WhichSamples=${1}
if [ ${WhichSamples} -eq 0 ]
    then 
        echo "running signal"
        python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_signal.json --unretire_jobs --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_signal --batch_system condor
fi

if [ ${WhichSamples} -eq 1 ]
    then 
        echo "running singleH"
        python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_singleH.json --unretire_jobs --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_singleH --batch_system condor
fi

if [ ${WhichSamples} -eq 2 ]
    then 
        echo "running bkg"
        python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_MCBKG.json --unretire_jobs --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_BKG --batch_system condor
fi

if [ ${WhichSamples} -eq 2016 ]
    then 
        echo "running 2016 data"
        python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json --unretire_jobs --years 2016 --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_data/2016 --batch_system condor
fi

if [ ${WhichSamples} -eq 2017 ]
    then 
        echo "running 2017 data"
        python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json --unretire_jobs --years 2017 --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_data/2017 --batch_system condor
fi

if [ ${WhichSamples} -eq 2018 ]
    then 
        echo "running 2018 data"
        python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json --unretire_jobs --years 2018 --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_data/2018 --batch_system condor
fi