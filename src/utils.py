import re
import os

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
    preliminary_diagnosis=df["preliminary_diagnosis"].value_counts()
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
    
    
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Medical Case Report', 0, 1, 'C')

    def chapter_title(self, case_id):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f'Case ID: {case_id}', 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, model_name, diagnosis):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, f'Diagnosis from {model_name}: {diagnosis}'.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(10)

    def add_case(self, case_id, principalDiagnosis, differentialDiagnosis, medicalHistory, diagnoses):
        self.add_page()
        self.chapter_title(case_id)

        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, f'Principal Diagnosis: {principalDiagnosis}'.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(5)
        self.multi_cell(0, 10, f'Differential Diagnosis: {differentialDiagnosis}'.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(5)
        self.multi_cell(0, 10, f'Medical History: {medicalHistory}'.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(10)

        # Add a page for each diagnosis
        for model_name, diagnosis in diagnoses:
            self.add_page()
            self.chapter_body(model_name, diagnosis)