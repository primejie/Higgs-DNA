import json
import os
from higgs_dna.utils.logger_utils import setup_logger
from higgs_dna.analysis import run_analysis

logger = setup_logger('DEBUG')
config_file = '/eos/user/z/zhjie/ResonantAnalysis/Production_27APR2022_data/2016/Data_2016/job_97/Data_2016_config_job97.json'
if not os.path.exists(config_file):
    config_file = os.path.split(config_file)[-1]
with open(config_file, 'r') as f_in:
    config = json.load(f_in)

run_analysis(config)
