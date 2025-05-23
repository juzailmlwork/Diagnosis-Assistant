import json
import pandas as pd
import os
def run_individual_model_analysis(models,types,folder):
    for model in models:
        temp_dict = {}
        for type in types:
            with open(f"{folder}/analysis/{type}.json", "r") as file:
                data = json.load(file)
            
            extracted_values = {outer_key: len(inner_dict[model]["true"]) for outer_key, inner_dict in data.items()}
            temp_dict[type] = extracted_values
        
        # Create DataFrame
        df = pd.DataFrame.from_dict(temp_dict)
        
        # Add a row with the sum of all columns
        df.loc['Total'] = df.sum()
        df.index.name = 'department'
        
        # Save to CSV
        output_folder= f"{folder}/analysis"
        os.makedirs(output_folder, exist_ok=True)
        df.to_csv(f"{output_folder}/{model}_performance.csv")

def get_statistics(type,departments,folder):
    with open(f"{folder}/analysis/{type}.json", "r") as file:
        chart = json.load(file) 
    total_cases=0
    department_wise_statistics={}
    for department in departments:
        department_wise_statistics[department]={}
        with open(f"{folder}/{type}/{department}_{type}.json", "r") as file:
            data = json.load(file)
        all_ids=data.keys()
        total_cases+=len(all_ids)
        department_results=chart[department]
        models=list(department_results.keys())
        none_detected=[]
        all_detected=[]
        atleast_one_detected=[]
        for id  in all_ids:
            count=0
            for model in models:
                if id in department_results[model]["true"]:
                    count+=1
            if count==0:
                none_detected.append(id)
            elif count==len(models):
                all_detected.append(id)
            else:
                atleast_one_detected.append(id)
        department_wise_statistics[department]["all_detected"]=all_detected
        department_wise_statistics[department]["none_detected"]=none_detected
        department_wise_statistics[department]["atleast_one_detected"]=atleast_one_detected

    df = pd.DataFrame.from_dict(department_wise_statistics, orient='index')
    df.index.name = 'department'
    df['len_all_detected'] = df['all_detected'].apply(len)
    df['len_none_detected'] = df['none_detected'].apply(len)
    df['len_atleast_one_detected'] = df['atleast_one_detected'].apply(len)
    df.loc['Total'] = df.sum()
    # df.to_csv(f'results/analysis/department_wise_statistics_{type}.csv')
    
    filtered_df = df[['len_all_detected', 'len_none_detected','len_atleast_one_detected']]
    output_folder= f"{folder}/analysis"
    os.makedirs(output_folder, exist_ok=True)
    filtered_df.to_csv(f'{output_folder}/department_wise_statistics_{type}.csv')
    return filtered_df