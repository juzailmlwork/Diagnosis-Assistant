import pandas as pd
pd.set_option('display.max_colwidth', 5000)
import json
from dotenv import load_dotenv
from src.gpt import doctor_prompt_disease_restricted_gpt
from src.utils import convert_string_to_list,convert_clinical_case_summary,filterDepartment,getDepartmentStatistics,convert_cases_to_json,PDF,select_case_components
from src.ollama import doctor_prompt_disease_restricted_ollama,doctor_prompt_disease_restricted_ollama_self_refinement,doctor_prompt_disease_restricted_ollama_combined
load_dotenv()
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



required_fields=[ "Patient basic information",
                 "Chief complaint",
                 "Medical history",
                 "Physical examination",
                 "Laboratory examination",
                 "Imageological examination",
                 "Auxillary examination",
                 "Pathological examination"
    
]
departments=["respiratory medicine department",
             "nephrology department",
             "pediatrics department",
             "gynecology department",
             "endocrinology department",   
             "neurology department",
             "cardiac surgical department",                          
             "gastrointestinal surgical department" ]
# departments=["nephrology department",
#              "pediatrics department"]
laboratory="abnormal"
image="impression"
report_type=f"{laboratory}_{image}"
for department in departments:
    print("department is",department)
    departmentdf=filterDepartment(df,department)
    caseNumbers = [i for i in range(1, len(departmentdf), 5)]
    # caseNumbers=[1]#,11,21]#31,41,51,61]
    # caseNumbers=[1]
    print(caseNumbers)
    row=departmentdf
    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    getDepartmentStatistics(departmentdf)
    for caseNumber in caseNumbers:
        case_id,principal_diagnosis,differential_diagnosis,clinical_case_dict,filtered_clinical_case_dict=select_case_components(departmentdf,caseNumber,required_fields,laboratory,image)
         # ("gpt-4", doctor_prompt_disease_restricted_gpt(filtered_clinical_case_dict, "gpt-4", uniquePrimary, department)),
        diagnoses = [("gpt-4", doctor_prompt_disease_restricted_gpt(filtered_clinical_case_dict, "gpt-4", differential_diagnosis, department)),
                     ("llama3.1", doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, "llama3.1", differential_diagnosis, department)),
                     ("phi3:14b", doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, "phi3:14b", differential_diagnosis, department)),
                     ("mistral-nemo", doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, "mistral-nemo", differential_diagnosis, department))
                     ]
        # diagnoses = [(model_name, doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, model_name, differential_diagnosis, department)) for model_name in models]
        pdf.add_case(case_id, principal_diagnosis, differential_diagnosis, clinical_case_dict, diagnoses)
        print("done for caseid",case_id)
    # # Output the PDF to a file
    pdf_file_path = f"./medical-reports/{department}_{report_type}_combined_new.pdf"
    pdf.output(pdf_file_path)

    print(f"PDF report generated: {pdf_file_path}")
    


# laboratory="result"
# image="findings"
# report_type=f"{laboratory}_{image}"
# for department in departments:
#     print("department is",department)
#     departmentdf=filterDepartment(df,department)
#     caseNumbers = [i for i in range(1, len(departmentdf), 10)]
#     # caseNumbers=[1]#,11,21]#31,41,51,61]
#     # caseNumbers=[1]
#     print(caseNumbers)
#     row=departmentdf
#     pdf = PDF()
#     pdf.set_left_margin(10)
#     pdf.set_right_margin(10)
#     getDepartmentStatistics(departmentdf)
#     for caseNumber in caseNumbers:
#         case_id,principal_diagnosis,differential_diagnosis,clinical_case_dict,filtered_clinical_case_dict=select_case_components(departmentdf,caseNumber,required_fields,laboratory,image)
#          # ("gpt-4", doctor_prompt_disease_restricted_gpt(filtered_clinical_case_dict, "gpt-4", uniquePrimary, department)),
#         diagnoses = [("gpt-4", doctor_prompt_disease_restricted_gpt(filtered_clinical_case_dict, "gpt-4", differential_diagnosis, department)),
#                      ("llama3.1", doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, "llama3.1", differential_diagnosis, department)),
#                      ("phi3:14b", doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, "phi3:14b", differential_diagnosis, department)),
#                      ("mistral-nemo", doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, "mistral-nemo", differential_diagnosis, department))
#                      ]
#         # diagnoses = [(model_name, doctor_prompt_disease_restricted_ollama(filtered_clinical_case_dict, model_name, differential_diagnosis, department)) for model_name in models]
#         pdf.add_case(case_id, principal_diagnosis, differential_diagnosis, clinical_case_dict, diagnoses)
#         print("done for caseid",case_id)
#     # # Output the PDF to a file
#     pdf_file_path = f"./medical-reports/{department}_{report_type}_combined.pdf"
#     pdf.output(pdf_file_path)

#     print(f"PDF report generated: {pdf_file_path}")
    
    
    
