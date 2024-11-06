import pandas as pd
pd.set_option('display.max_colwidth', 5000)
from dotenv import load_dotenv
from src.utils import (
    load_preprocess_data,
    run_prediction)
load_dotenv()
from prompts import single_shot_disease_only_prompt,open_ended__top4_prompt,with_reasons_prompt


filePath="dataset/clinicallab/data_en.json"
df=load_preprocess_data(filePath)


departments=["nephrology department",
             "gynecology department",
            "endocrinology department", 
            "neurology department",
             "pediatrics department",
             "cardiac surgical department",                          
             "gastrointestinal surgical department",
             "respiratory medicine department",
            ]
models = ["gpt-4","llama3.1","gemma2"]
# type="with_reasons"
# prompt=with_reasons_prompt
type="single_shot_without_sorted"
prompt=single_shot_disease_only_prompt
# type="open_ended"
# prompt=open_ended__top4_prompt# 
run_prediction(df,prompt,departments,models=models,type=type,skip=5)