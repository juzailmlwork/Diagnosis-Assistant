import re
import os
import pandas as pd
pd.set_option('display.max_colwidth', 5000)
import json
from src.ollama import doctor_prompt_ollama,evaluate_ollama
from src.gpt import doctor_prompt_gpt,evaluate_gpt

def extract_disease_names(diagnoses):
    disease_names = []
    for diagnosis in diagnoses:
        disease_name = diagnosis.split(':')[0]  # Split and get the disease name
        if len(disease_name) < 40:  # Check if the name is less than 40 characters
            disease_names.append(disease_name)
    return disease_names

def filterDepartment(df,department):
    allDepartments=df["clinical_department"].unique().tolist()
    if department in allDepartments:
        departmentdf=df[df["clinical_department"]==department]
    else:
        raise Exception
    return departmentdf

def getDepartmentStatistics(df):
    prinicipal_diagnosis=df["principal_diagnosis"].value_counts()
    print("number of principal diagnosis are",len(prinicipal_diagnosis))
    print(prinicipal_diagnosis)
    print("number of preliminary_diagnosis are",len(prinicipal_diagnosis))

def convert_string_to_list(s):
    pattern = r'\d+\.\s*'
    conditions = re.split(pattern, s)
    if len(conditions) == 1:
        return [s.strip()]
    
    # Remove any empty string that might result from the split
    return [condition.strip() for condition in conditions if condition.strip()]

def convert_clinical_case_summary(text):
    sections = [
        "Patient Basic Information",
        "Chief Complaint",
        "Medical History",
        "Physical Examination",
        "Auxiliary Examination",
        "Imaging Examination",
        "Laboratory Examination",
        "Pathological Examination"
    ]
    
    # Create a regex pattern to match each section
    pattern = r'(' + '|'.join(re.escape(section) for section in sections) + r'):\s*'
    
    # Split the text based on the pattern
    matches = re.split(pattern, text)
    
    # The first element is the text before the first match (Case Summary), so we skip it
    matches = matches[1:]
    
    # Create the dictionary by pairing section names with their content
    result = {}
    for i in range(0, len(matches), 2):
        section = matches[i].strip()
        content = matches[i+1].strip()
        result[section] = content
    
    return result

def convert_cases_to_json(df,folder_name):
    for index, row in df.iterrows():
        department_name = row['clinical_department']
        case_id = row['id']
        
        # Create the department-specific folder if it doesn't exist
        department_folder = os.path.join(folder_name, department_name)
        os.makedirs(department_folder, exist_ok=True)
        
        # Creating the filename
        filename = f"{department_name}-{case_id}.json"
        file_path = os.path.join(department_folder, filename)
        
        # Convert the row to a DataFrame to retain column names
        row_df = row.to_frame().T
        
        # Save the row as a JSON file with column names
        row_df.to_json(file_path, orient='records', lines=False, indent=4)
    print("done saving the json file")
    
def extract_lab_data(lab_data, field):
    """
    Extracts the specified field ('result' or 'abnormal') from the laboratory examination data.

    :param lab_data: A dictionary containing laboratory examination data.
    :param field: The field to extract ('result' or 'abnormal').
    :return: A dictionary containing the extracted field data.
    """
    extracted_data = {}
    
    # Iterate over each test in the laboratory examination data
    for test, data in lab_data.items():
        if field in data:
            extracted_data[test] = data[field]
    
    return extracted_data
                        
def select_case_components(departmentdf,rowNumber,required_fields,laboratory="result",image="findings"):
    row = departmentdf.iloc[rowNumber]
    case_id = row.id
    clinical_case = row.clinical_case_summary
    principal_diagnosis = row.principal_diagnosis
    differential_diagnosis = row.differential_diagnosis
    # differential_diagnosis = [entry.split(":")[0] for entry in differential_diagnosis if len(entry.split(":")[0]) < 40]
    # differential_diagnosis.append(principal_diagnosis)
    differential_diagnosis = [item.capitalize() for item in differential_diagnosis]
    differential_diagnosis.sort()
    try:
        laboratory_examination = extract_lab_data(row.laboratory_examination,laboratory)
    except:
        laboratory_examination = "Not available."
    try:
        imageological_examination = extract_lab_data(row.imageological_examination,image)
    except:
        imageological_examination="Not available."
    clinical_case_dict={
    "Patient basic information":clinical_case['Patient Basic Information'],
    "Chief complaint" : clinical_case['Chief Complaint'],
    "Medical history" : clinical_case['Medical History'],
    "Physical examination" : clinical_case['Physical Examination'],
    "Laboratory examination" : laboratory_examination,
    "Imageological examination" : imageological_examination,
    "Auxillary examination": clinical_case['Auxiliary Examination'],
    "Pathological examination" : row.pathological_examination
    }
    filtered_clinical_case_dict={}
    for key in required_fields:
        filtered_clinical_case_dict[key]=clinical_case_dict[key]
    return case_id,principal_diagnosis,differential_diagnosis,clinical_case_dict,filtered_clinical_case_dict


def select_case_components_based_on_id(df,case_id,required_fields,laboratory="result",image="findings"):
    
    row = df[df['id'] == case_id].iloc[0]
    clinical_case = row.clinical_case_summary
    principal_diagnosis = row.principal_diagnosis
    department=row.clinical_department
    differential_diagnosis = row.differential_diagnosis
    differential_diagnosis = [item.capitalize() for item in differential_diagnosis]
    differential_diagnosis.sort()
    try:
        laboratory_examination = extract_lab_data(row.laboratory_examination,laboratory)
    except:
        laboratory_examination = "Not available."
    try:
        imageological_examination = extract_lab_data(row.imageological_examination,image)
    except:
        imageological_examination="Not available."
    clinical_case_dict={
    "Patient basic information":clinical_case['Patient Basic Information'],
    "Chief complaint" : clinical_case['Chief Complaint'],
    "Medical history" : clinical_case['Medical History'],
    "Physical examination" : clinical_case['Physical Examination'],
    "Laboratory examination" : laboratory_examination,
    "Imageological examination" : imageological_examination,
    "Auxillary examination": clinical_case['Auxiliary Examination'],
    "Pathological examination" : row.pathological_examination
    }
    
    filtered_clinical_case_dict={}
    for key in required_fields:
        filtered_clinical_case_dict[key]=clinical_case_dict[key]
    
    return principal_diagnosis,differential_diagnosis,filtered_clinical_case_dict

    
def load_preprocess_data(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        print("\nnumber of total cases are",len(data))
        print("\neach case have the following fields",list(data[0].keys()))

        keys_to_include = ["id",'clinical_department', 'principal_diagnosis', 'preliminary_diagnosis',
                        'diagnostic_basis', 'differential_diagnosis', 
                        'treatment_plan', 'clinical_case_summary', 'imageological_examination', 
                        'laboratory_examination', 'pathological_examination', 'therapeutic_principle']
        df = pd.DataFrame([{key: d[key] for key in keys_to_include} for d in data])

        allDepartmentsCount=df['clinical_department'].value_counts()
        print("\nnumber of departments available are",len(allDepartmentsCount))
        print("\n all the departments available are")
        print(allDepartmentsCount)

        df['preliminary_diagnosis'] = df['preliminary_diagnosis'].apply(convert_string_to_list)
        df['diagnostic_basis'] = df['diagnostic_basis'].apply(convert_string_to_list)
        df['differential_diagnosis'] = df['differential_diagnosis'].apply(convert_string_to_list)
        df['treatment_plan'] = df['treatment_plan'].apply(convert_string_to_list)
        df["clinical_case_summary"] = df["clinical_case_summary"].apply(convert_clinical_case_summary)
        
        return df
    
    
    
def extract_disease_names_from_row(differential_diagnosis_list):
    disease=[entry.split(":")[0].strip() for entry in differential_diagnosis_list]
    return disease

def extract_all_diseases_per_department(departmentdf,max_len_disease=40):
    differential_diseases = departmentdf["differential_diagnosis"].apply(extract_disease_names_from_row).sum()
    refined_differential_diseases=[]
    for disease in differential_diseases:
        if len(disease) <max_len_disease:
            refined_differential_diseases.append(disease)
    uniqueDiseases=departmentdf["principal_diagnosis"].unique().tolist()
    uniqueDiseases.extend(refined_differential_diseases)
    uniqueDiseases = [item.lower() for item in uniqueDiseases]
    uniqueDiseases = sorted(set(uniqueDiseases))

    print("number of unique diseases are",len(uniqueDiseases))
    print(len(uniqueDiseases))
    print(uniqueDiseases)
    return uniqueDiseases


def run_prediction(df,prompt,departments,models,folder,type="semi_ended",laboratory_examination="result",
                   image_examination="findings",skip=6):
    required_fields=[ "Patient basic information",
                 "Chief complaint",
                 "Medical history",
                 "Physical examination",
                 "Laboratory examination",
                 "Imageological examination",
                 "Auxillary examination",
                 "Pathological examination"
    
]
    report_type=f"{laboratory_examination}_{image_examination}"
    for i  in range(len(departments)):
        department=departments[i]
        results={}
        print("department is",department)
        departmentdf=filterDepartment(df,department)
        caseNumbers = [i for i in range(1, len(departmentdf), skip)]
        print(caseNumbers)
        getDepartmentStatistics(departmentdf)
        for caseNumber in caseNumbers:
            case_details={}        
            case_id,principal_diagnosis,differential_diagnosis,clinical_case_dict,filtered_clinical_case_dict=select_case_components(departmentdf,caseNumber,required_fields,laboratory_examination,image_examination)
            case_details["original"]={"main-diagnosis":principal_diagnosis,"differential_diagnosis":differential_diagnosis}
            case_details["predictions"]={}
            print("case_id",case_id)
            # print("principal diagnosis",principal_diagnosis)
            for model in models:
                if model=="gpt-4o":
                    output=doctor_prompt_gpt(prompt,filtered_clinical_case_dict,model,differential_diagnosis,department)
                else:
                    output=doctor_prompt_ollama(prompt,filtered_clinical_case_dict,model,differential_diagnosis,department)
                case_details["predictions"][model]=output
            results[str(case_id)]=case_details
        output_folder= f"{folder}/{type}"
        os.makedirs(output_folder, exist_ok=True)
        with open(f"{output_folder}/{department}_{type}.json", "w") as outfile: 
            json.dump(results, outfile)
import difflib

def calculate_word_similarity(word1, word2):
    # Use SequenceMatcher to calculate similarity
    return difflib.SequenceMatcher(None, word1, word2).ratio() * 100            
            
def evaluate_department_results(data,evaluating_model="ollama"):
    models=list(data[list(data.keys())[0]]["predictions"].keys())
    print(models)
    results = {model: {"true": [], "false": [], "count_true": 0, "count_false": 0,"results":[]} for model in models}

    # Iterate through each case in the data
    for caseNumber, case in data.items():
        ground_truth_disease = case["original"]["main-diagnosis"]  
        differential_diagnosis = case["original"]["differential_diagnosis"]       
        # # Evaluate predictions for each model
        # for model in results.keys():
        #     predicted = case["predictions"][model]
        #     # output = list(evaluate_gpt(ground_truth_disease, predicted))
        #     # output = list(evaluate_ollama(ground_truth_disease, predicted))
        #     output = list(evaluate_ollama(ground_truth_disease, predicted,diseases))
        #     result=str(output[1])
        #     results[model][result.lower()].append(caseNumber)
        #     results[model][f'count_{result.lower()}'] += 1
        #     results[model]["predicted"].append(str(output[0]).lower())
        #     results[model]["ground_truth"].append(ground_truth_disease.lower())
        # Evaluate predictions for each model
        for model in results.keys():
            predicted = case["predictions"][model]
            if evaluating_model=="ollama":
                output = list(evaluate_ollama(ground_truth_disease, predicted))[0]
            elif evaluating_model=="gpt":
                 output = list(evaluate_gpt(ground_truth_disease, predicted))[0]
            result=output.lower()
            # print("predicted disease is",result)
            # results[model][result.lower()].append(caseNumber)
            similarity_percentage = calculate_word_similarity(ground_truth_disease, result)
            if similarity_percentage >80:
                matching="true"
            else:
                matching="false"
            # print(ground_truth_disease,result,matching,similarity_percentage)
            results[model][matching].append(caseNumber) 
            results[model][f'count_{matching}'] += 1
            results[model]["results"].append({"case_id":caseNumber,"ground_truth":ground_truth_disease.lower(),"predicted":result,"differential-diagnosis":differential_diagnosis})
            # results[model]["ground_truth"].append(ground_truth_disease.lower())

    return results


import zipfile
import os
import shutil

def unzip_flatten_top_level(zip_path: str, extract_to: str = "./"):
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            if member.is_dir():
                continue

            path_parts = member.filename.split(os.sep)

            # Skip the top-level folder
            if len(path_parts) > 1:
                new_filename = os.path.join(*path_parts[1:])
            else:
                new_filename = path_parts[0]

            target_path = os.path.join(extract_to, new_filename)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                shutil.copyfileobj(source, target)

    print(f"Unzipped to: {extract_to}")


def zip_folder(folder_path: str, output_zip_path: str):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, start=folder_path)
                zipf.write(abs_path, arcname=rel_path)
    
    print(f"Zipped folder '{folder_path}' into: {output_zip_path}")