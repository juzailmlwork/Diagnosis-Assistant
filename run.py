import pandas as pd
pd.set_option('display.max_colwidth', 5000)
from dotenv import load_dotenv
import os
from src.utils import (
    load_preprocess_data,
    run_prediction,
    extract_disease_names)

from prompts import single_shot_disease_only_prompt,open_ended__top4_prompt,with_reasons_prompt


filePath="dataset/clinicallab/data_en.json"
df=load_preprocess_data(filePath)



# Apply the function to filter and transform the 'differential-diagnosis' field
df['differential_diagnosis'] = df['differential_diagnosis'].apply(extract_disease_names)

# Filter rows where the number of elements in 'differential-diagnosis' is greater than 1
filtered_df = df[df['differential_diagnosis'].apply(lambda x: len(x) > 1)]
filtered_df['differential_diagnosis'] = filtered_df['differential_diagnosis'] + filtered_df['principal_diagnosis'].apply(lambda x: [x] if x else [])
df=filtered_df
departments=["nephrology department",
             "gynecology department",
            "endocrinology department", 
            "neurology department",
             "pediatrics department",
             "cardiac surgical department",                          
             "gastrointestinal surgical department",
             "respiratory medicine department",
             "gastroenterology department",
             "urinary surgical department",
             "hepatobiliary and pancreas surgical department",
             "hematology department"
            ]
models = ["gpt-4o","llama3.1","gemma2"]#,"mistral-nemo","phi3:14b"]#]

type="single_shot"
prompt=single_shot_disease_only_prompt
run_prediction(df,prompt,departments,models=models,type=type,skip=3)

type="with_reasons"
prompt=with_reasons_prompt
run_prediction(df,prompt,departments,models=models,type=type,skip=3)

# type="open_ended"
# prompt=open_ended__top4_prompt# 
# run_prediction(df,prompt,departments,models=models,type=type,skip=5)