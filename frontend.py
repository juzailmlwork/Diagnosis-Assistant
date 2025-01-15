import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import json
import os
from datetime import datetime
from prompts import single_shot_disease_only_prompt, open_ended__top4_prompt, with_reasons_prompt
from src.gpt import doctor_prompt_gpt
from src.ollama import doctor_prompt_ollama

# Load environment variables
load_dotenv()

departments = [
    "nephrology department", "gynecology department", "endocrinology department", 
    "neurology department", "pediatrics department", "cardiac surgical department", 
    "gastrointestinal surgical department", "respiratory medicine department", 
    "gastroenterology department", "urinary surgical department", 
    "hepatobiliary and pancreas surgical department", "hematology department"
]

# Helper function to get user input for various fields
def get_input(field_name, placeholder):
    """Helper function to get input and return 'Not available' if left blank."""
    value = st.text_area(field_name, "", placeholder=placeholder).strip()
    return value if value else "Not available"

# Function to collect case information
def collect_clinical_case_info():
    """Collect the clinical case details from user input."""
    clinical_case_dict = {}

    # Prompt Type Selection
    st.header("Prompt Type")
    clinical_case_dict["Prompt type"] = st.selectbox(
        "Select the Prompt Type", ["single_shot", "two_shot", "three_shot"], index=0
    )

    # Models Selection
    st.header("Models")
    models = st.multiselect(
        "Select Models to Use", ["gpt-4o", "llama3.1", "gemma2"], default=[]
    )
    if not models:
        st.warning("Please select at least one model.")
    clinical_case_dict["Models"] = models

    # Department Selection
    st.header("Department")
    clinical_case_dict["Department"] = st.selectbox(
        "Select Department", departments, index=0
    )

    # Patient Basic Information
    st.header("Patient Basic Information")
    clinical_case_dict["Patient basic information"] = get_input(
        "Enter Patient Basic Information", "E.g., Elderly female, 88 years old."
    )

    # Chief Complaint
    st.header("Chief Complaint")
    clinical_case_dict["Chief complaint"] = get_input(
        "Enter Chief Complaint", "E.g., Fatigue for 1 week, fever, chills, and dysuria for 3 days."
    )

    # Medical History
    st.header("Medical History")
    clinical_case_dict["Medical history"] = get_input(
        "Enter Medical History", "E.g., Hypertension for 8 years, etc."
    )

    # Other Details (Physical Exam, Lab, Imaging, etc.)
    st.header("Physical Examination")
    clinical_case_dict["Physical examination"] = get_input(
        "Enter Physical Examination Findings", "E.g., No eyelid swelling, clear breath sounds, etc."
    )

    st.header("Laboratory Examination")
    clinical_case_dict["Laboratory examination"] = get_input(
        "Enter Laboratory Examination Details", "E.g., WBC, HGB, etc."
    )

    st.header("Imaging Examination")
    clinical_case_dict["Imaging examination"] = get_input(
        "Enter Imaging Examination Details", "E.g., CT scan results, X-ray findings, etc."
    )

    # Differential Diagnosis
    st.header("Differential Diagnosis")
    differential_diagnosis_input = st.text_area(
        "Enter Differential Diagnoses (comma-separated)",
        "E.g., Pneumonia, Urinary tract infection, Sepsis"
    ).strip()

    if differential_diagnosis_input:
        clinical_case_dict["Differential diagnosis"] = [diag.strip() for diag in differential_diagnosis_input.split(",") if diag.strip()]
    else:
        clinical_case_dict["Differential diagnosis"] = []

    return clinical_case_dict

# Save clinical case dictionary as JSON file with timestamp
def save_clinical_case(clinical_case_dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clinical_case_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(clinical_case_dict, f, indent=4)
    st.success(f"Clinical case saved as '{filename}'.")

# Main function
def main():
    st.title("Clinical Case Information Collector")
    st.write("Fill in the details below to create a comprehensive clinical case dictionary.")

    clinical_case_dict = collect_clinical_case_info()

    # Separate Buttons for Actions
    if st.button("Show Clinical Case Dictionary"):
        st.subheader("Collected Clinical Case Information")
        st.json(clinical_case_dict)

    if st.button("Save Clinical Case as JSON"):
        if clinical_case_dict:
            save_clinical_case(clinical_case_dict)

    if st.button("Run Prediction"):
        if clinical_case_dict["Models"]:
            prompt = single_shot_disease_only_prompt
            differential_diagnosis = clinical_case_dict["Differential diagnosis"]
            department = clinical_case_dict["Department"]
            models = clinical_case_dict["Models"]
            filtered_clinical_case_dict = {k: v for k, v in clinical_case_dict.items() if k not in ["Differential diagnosis", "Department", "Models", 'Prompt type']}
            # Replace the file loading part with actual case data for testing
            filtered_clinical_case_dict = json.load(open("clinical_case_example.json"))
            differential_diagnosis = ['Acute pyelonephritis', 'Urinary system stones', 'Urinary tract tumor', 'Urinary tuberculosis']
            department = "nephrology department"
            for model in models:
                if model == "gpt-4o":
                    output = doctor_prompt_gpt(prompt, filtered_clinical_case_dict, model, differential_diagnosis, department)
                else:
                    output = doctor_prompt_ollama(prompt, filtered_clinical_case_dict, model, differential_diagnosis, department)
                st.subheader(f"Output from {model}")
                st.write(output)

if __name__ == "__main__":
    main()
