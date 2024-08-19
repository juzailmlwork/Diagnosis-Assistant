import concurrent.futures
def parallel_diagnosis(model_name, medical_history, diseases, department):
    return (model_name, doctor_prompt_disease_restricted_ollama(medical_history, model_name, diseases, department))

for department in departments:
    print("department is", department)
    departmentdf = filterDepartment(df, department)
    print(len(departmentdf))
    caseNumbers = [i for i in range(1, len(departmentdf), 10)]
    caseNumbers = [1]#, 11, 21]  # 31,41,51,61]
    print(caseNumbers)
    differential_diseases = departmentdf["differential_diagnosis"].apply(extract_disease_names_from_row).sum()
    refined_differential_diseases = []
    for disease in differential_diseases:
        if len(disease) < 20:
            refined_differential_diseases.append(disease)
    uniqueDiseases = departmentdf["principal_diagnosis"].unique().tolist()
    uniquePrimary = uniqueDiseases[:]
    uniqueDiseases.extend(refined_differential_diseases)
    uniqueDiseases = list(set(uniqueDiseases))

    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    getDepartmentStatistics(departmentdf)

    for caseNumber in caseNumbers:
        print(caseNumber)
        case_id, principal_diagnosis, differential_diagnosis, clinical_case_dict, filtered_clinical_case_dict = select_case_components(departmentdf, caseNumber, required_fields)
        row = departmentdf.iloc[caseNumber]

        # Models to run in parallel
        model_names = ["llama3.1", "mistral", "gemma2", "phi3:14b", "mistral-nemo"]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map the models to the parallel diagnosis function
            future_to_model = {executor.submit(parallel_diagnosis, model, filtered_clinical_case_dict, uniquePrimary, department): model for model in model_names}
            
            # Collect the results
            diagnoses = []
            for future in concurrent.futures.as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    result = future.result()
                    diagnoses.append(result)
                except Exception as exc:
                    print(f'{model_name} generated an exception: {exc}')
        
        print("done diagnosing")
        pdf.add_case(case_id, principal_diagnosis, differential_diagnosis, clinical_case_dict, diagnoses)

    # Output the PDF to a file
    pdf_file_path = f"./medical-reports/medical_case_report_{department}.pdf"
    pdf.output(pdf_file_path)

    print(f"PDF report generated: {pdf_file_path}")
    
    
    
    
    
    ###########################################################
    
    
    
    import concurrent.futures

def parallel_diagnosis(model_name, medical_history, diseases, department):
    return (model_name, doctor_prompt_disease_restricted_ollama(medical_history, model_name, diseases, department))

for department in departments:
    print("department is", department)
    departmentdf = filterDepartment(df, department)
    print(len(departmentdf))
    caseNumbers = [i for i in range(1, len(departmentdf), 10)]
    caseNumbers = [1]  # Example case numbers
    print(caseNumbers)
    differential_diseases = departmentdf["differential_diagnosis"].apply(extract_disease_names_from_row).sum()
    refined_differential_diseases = [disease for disease in differential_diseases if len(disease) < 20]
    uniqueDiseases = list(set(departmentdf["principal_diagnosis"].unique().tolist() + refined_differential_diseases))

    pdf = PDF()
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    getDepartmentStatistics(departmentdf)

    for caseNumber in caseNumbers:
        print(caseNumber)
        case_id, principal_diagnosis, differential_diagnosis, clinical_case_dict, filtered_clinical_case_dict = select_case_components(departmentdf, caseNumber, required_fields)
        row = departmentdf.iloc[caseNumber]

        model_names = ["llama3.1", "mistral", "gemma2", "phi3:14b", "mistral-nemo"]

        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_model = {executor.submit(parallel_diagnosis, model, filtered_clinical_case_dict, uniquePrimary, department): model for model in model_names}
            
            diagnoses = []
            for future in concurrent.futures.as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    result = future.result()
                    diagnoses.append(result)
                except Exception as exc:
                    print(f'{model_name} generated an exception: {exc}')
        
        print("done diagnosing")
        pdf.add_case(case_id, principal_diagnosis, differential_diagnosis, clinical_case_dict, diagnoses)

    pdf_file_path = f"./medical-reports/medical_case_report_{department}.pdf"
    pdf.output(pdf_file_path)

    print(f"PDF report generated: {pdf_file_path}")