import pandas as pd
pd.set_option('display.max_colwidth', 5000)
import json
from dotenv import load_dotenv
from src.gpt import doctor_prompt_gpt_semi_ended
from src.utils import convert_string_to_list,convert_clinical_case_summary,filterDepartment,getDepartmentStatistics,select_case_components
from src.ollama import doctor_prompt_ollama_semi_ended
import os
print(os.getenv("OPENAI_API_KEY"))
filePath="dataset/clinicallab/data_en.json"
with open(filePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
print("\nnumber of total cases are",len(data))
print("\neach case have the following fields",list(data[0].keys()))

keys_to_include = ["id",'clinical_department', 'principal_diagnosis', 'preliminary_diagnosis',
                   'diagnostic_basis', 'differential_diagnosis', 
                   'treatment_plan', 'clinical_case_summary', 'imageological_examination', 
                   'laboratory_examination', 'pathological_examination', 'therapeutic_principle']
df = pd.DataFrame([{key: d[key] for key in keys_to_include} for d in data])

allDepartments=df['clinical_department'].value_counts()
print("number of departments available are",len(allDepartments))

print("\n all the departments available are")
print(allDepartments)

df['preliminary_diagnosis'] = df['preliminary_diagnosis'].apply(convert_string_to_list)
df['diagnostic_basis'] = df['diagnostic_basis'].apply(convert_string_to_list)
df['differential_diagnosis'] = df['differential_diagnosis'].apply(convert_string_to_list)
df['treatment_plan'] = df['treatment_plan'].apply(convert_string_to_list)
df["clinical_case_summary"] = df["clinical_case_summary"].apply(convert_clinical_case_summary)


uniqueDiseases1=['Lumbar Tuberculosis', 'systemic lupus erythematosus', 'Low T3 Syndrome', 'ankylosing spondylitis', "Graves' disease", 'Diabetes insipidus', 'Psoriatic Arthritis', 'Type 1 Diabetes', 'Type 1 diabetes', 'Hyperthyroidism', 'Scleredema', 'hypothyroidism', 'Hypoglycemia', 'Hypokalemia', 'Myositis', 'subacute thyroiditis', 'Simple Skin Allergy', 'Diabetes Insipidus', 'Simple Goiter', 'Psoriatic arthritis', 'rheumatoid arthritis', 'Rheumatic Fever', 'diabetes mellitus', 'Simple goiter', 'Colorectal cancer', 'gouty arthritis', 'Rheumatic fever', 'Osteoarthritis']
uniqueDiseases2=['Brain Hemorrhage', 'parkinson disease', 'Epilepsy', 'Cerebral Infarction', 'Diabetic Neuropathy', 'Cerebral hemorrhage', 'Lewy Body Dementia', 'Cervical vertigo', 'Tumorous Stroke', 'alzheimer disease', 'myelitis', 'Lyme Disease', 'Multiple sclerosis', 'Acute Myelitis', 'Tumoral Stroke', 'Optic neuritis', 'subarachnoid hemorrhage', 'Tumor Stroke', 'Cranial tumor', 'Vascular Dementia', 'Lyme disease', 'Syncope', 'Pseudoseizures', 'Periodic Paralysis', 'Primary Tremor', 'Diabetic neuropathy', 'facial neuritis', 'Polymyositis', 'transient ischemic attack']
uniqueDiseasesall=[uniqueDiseases1,uniqueDiseases2]

required_fields=[ "Patient basic information",
                 "Chief complaint",
                 "Medical history",
                 "Physical examination",
                 "Laboratory examination",
                 "Imageological examination",
                 "Auxillary examination",
                 "Pathological examination"
    
]
departments=["endocrinology department","neurology department"]
laboratory="result"
image="findings"
report_type=f"{laboratory}_{image}"
all_departments={}
for i  in range(len(departments)):
    department=departments[i]
    unique_diseases=uniqueDiseasesall[i]
    results={}
    print("department is",department)
    print("uniqueDiseases are",unique_diseases)
    departmentdf=filterDepartment(df,department)
    caseNumbers = [i for i in range(1, len(departmentdf), 3)]
    print(caseNumbers)
    row=departmentdf
    getDepartmentStatistics(departmentdf)
    for caseNumber in caseNumbers:
        case_details={}        
        case_id,principal_diagnosis,differential_diagnosis,clinical_case_dict,filtered_clinical_case_dict=select_case_components(departmentdf,caseNumber,required_fields,laboratory,image)
        print("case_id",case_id)
        print("principal diagnosis",principal_diagnosis)
        output0=doctor_prompt_gpt_semi_ended(filtered_clinical_case_dict,"gpt-4",unique_diseases,department)
        output1=doctor_prompt_ollama_semi_ended(filtered_clinical_case_dict,"llama3.1",unique_diseases,department)
        output2=doctor_prompt_ollama_semi_ended(filtered_clinical_case_dict,"gemma2",unique_diseases,department)
        # output3=doctor_prompt_ollama_semi_ended(filtered_clinical_case_dict,"phi3:14b",differential_diagnosis,department)
        
        case_details["gpt-4"]=output0
        case_details["llama3.1"]=output1
        case_details["gemma2"]=output2
        results[str(case_id)]=case_details
    with open(f"{department}_semi_ended.json", "w") as outfile: 
        json.dump(results, outfile)