#echo "0-signal   1-singleH  2-bkg"
# WhichSamples=${1}
# if [ ${WhichSamples} -eq 0 ]
#     then 
#         echo "running signal"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_signal.json --years 2017 --unretire_jobs --output_dir /eos/user/z/zhjie/Forchu/allsignal/2017 --batch_system condor 
# fi

# if [ ${WhichSamples} -eq 18 ]
#     then 
#         echo "running signal"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_signal.json --years 2018 --unretire_jobs --output_dir /eos/user/z/zhjie/Forchu/allsignal/2018 --batch_system condor 
# fi
# if [ ${WhichSamples} -eq 161 ]
#     then 
#         echo "running signal"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_signal.json --years 2016preVFP --unretire_jobs --output_dir /eos/user/z/zhjie/Forchu/allsignal/2016pre --batch_system condor 
# fi
# if [ ${WhichSamples} -eq 162 ]
#     then 
#         echo "running signal"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_signal.json --years 2016postVFP --unretire_jobs --output_dir /eos/user/z/zhjie/Forchu/allsignal/2016post --batch_system condor 
# fi
# if [ ${WhichSamples} -eq 1 ]
#     then 
#         echo "running singleH"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_singleH.json --unretire_jobs --output_dir /eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_singleH --batch_system condor
# fi

# if [ ${WhichSamples} -eq 2 ]
#     then 
#         echo "running bkg"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_MCBKG.json --unretire_jobs --years 2017 --output_dir /eos/user/z/zhjie/Forchu/2017_tight/bkg  --batch_system condor
# fi
# if [ ${WhichSamples} -eq 3 ]
#     then 
#         echo "running bkg"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_MCBKG.json --unretire_jobs --years 2016preVFP --output_dir /eos/user/z/zhjie/Forchu/BKG/2016preVFP  --batch_system condor
# fi
# if [ ${WhichSamples} -eq 4 ]
#     then 
#         echo "running bkg"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_MCBKG.json --unretire_jobs --years 2018 --output_dir /eos/user/z/zhjie/Forchu/BKG/2018  --batch_system condor
# fi

# if [ ${WhichSamples} -eq 20161 ]
#     then 
#         echo "running 2016 data"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json  --years 2016preVFP --output_dir /eos/user/z/zhjie/Forchu/data/2016preVFP --batch_system condor
# fi
# if [ ${WhichSamples} -eq 20162 ]
#     then 
#         echo "running 2016 data"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json  --years 2016postVFP --output_dir /eos/user/z/zhjie/Forchu/data/2016postVFP --batch_system condor
# fi

# if [ ${WhichSamples} -eq 2017 ]
#     then 
#         echo "running 2017 data"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json --unretire_jobs --years 2017 --output_dir /eos/user/z/zhjie/Forchu/2017_tight/lowpt --batch_system condor --short
# fi

# if [ ${WhichSamples} -eq 2018 ]
#     then 
#         echo "running 2018 data"
#         python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data.json --unretire_jobs  --years 2018 --output_dir /eos/user/z/zhjie/Forchu/data/2018_fpo_2 --batch_system condor
# fi
python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_data_withsyst.json --unretire_jobs --years 2017 --output_dir /eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/zhangjie/Data_2017  --batch_system condor
python scripts/run_analysis.py --config metadata/tutorial/signal_withsys.json --unretire_jobs  --output_dir /eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/zhangjie/signal  --batch_system condor
python scripts/run_analysis.py --config metadata/tutorial/signal_withsys_2018.json --unretire_jobs  --output_dir /eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/zhangjie/signal_2018  --batch_system condor
python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_singleH.json --unretire_jobs  --output_dir /eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/zhangjie/ttH  --batch_system condor
python scripts/run_analysis.py --config metadata/tutorial/hhggxx_analysis_singleH_2018.json --unretire_jobs  --output_dir /eos/cms/store/group/dpg_ecal/alca_ecalcalib/ecalelf/ntuples/zhangjie/ttH_2018  --batch_system condor