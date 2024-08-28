"""You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results so far Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    using your expert knowledge considering all the phyical examination,lab reports and image 
    Only select from this set of diseases for analysis: {diseases}
    output should be formated as a list where each element is a dictionary.each element will have following fields
    1.disease-name:name of the disease based on above set
    2.reason:reason based on past history,physical examination,lab reports and image reports
    3.next-step:possible next examination needed to furthur confirm the disease
    If you have any doubts regarding differential diagnosis clearly mention them in order
    """
    
    
system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top 3 possible disease using above analysis and differential diagnosis
    output should be formated as a list where each element is a dictionary.each element will have following fields
    1.disease-name:name of the disease based on above set
    2.reason:Detailed reason based on past history,physical examination,lab reports and image reports
    """
    
system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis.I need you to not miss any examination reports and think step by step what each
    examination report suggest.Make sure you only stick to above set of diseases
    output should be formated in the following format
    **Medical Examination Analysis**
    ***Physical Examination***
    ***Laboratory Examination:***
    ***Imaging Examination***
    
    **Differential Diagnosis**
    1.disease1:Detailed reasons based on the case history
    2.disease2:Detailed reasons based on the case history
    3.disease3:Detailed reasons based on the case history
    4.disease4:Detailed reasons based on the case history
    
    **Final Diagnosis""
    ***Name of the most possible disease***
    ****possible reasons****
    Detailed reasons based on past medical history,physical examination,laboratory examinations and image examinations.
    Each reasoning should be precise and small.you can list any number of reason you are confident about
    """
    
system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis.I need you to not miss any examination reports and think step by step what each
    examination report suggest.Make sure you only stick to above set of diseases
    output should be formated in the following format
    **Medical Examination Analysis**
    ***Physical Examination***
    ***Laboratory Examination:***
    ***Imaging Examination***
    
    **Differential Diagnosis Based on above set of diseases**
    1.disease1:Detailed reasons based on the case history
    2.disease2:Detailed reasons based on the case history
    3.disease3:Detailed reasons based on the case history
    4.disease4:Detailed reasons based on the case history
    
    **Final Diagnosis""
    ***Name of the most possible disease***
    ****possible reasons****
    Detailed reasons based on past medical history,physical examination,laboratory examinations and image examinations.
    Each reasonings should be bullet form and they should be precise and small.you can list any number of reasons you are confident about
    """
    
    
system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis.I need you to not miss any examination reports and think step by step what each
    examination report suggest.Make sure you only stick to above set of diseases
    output should be formated in the following format
    **Medical Examination Analysis**
    ***Physical Examination***
    ***Laboratory Examination:***
    ***Imaging Examination***
    
    **Differential Diagnosis Based on above set of diseases**
    1.disease1:Detailed reasons based on the case history
    2.disease2:Detailed reasons based on the case history
    3.disease3:Detailed reasons based on the case history
    4.disease4:Detailed reasons based on the case history
    
    
    **Final Diagnosis""
    ***Name of the most possible disease***
    ****possible reasons****
    Detailed reasons based on past medical history,physical examination,laboratory examinations and image examinations.
    Each reasonings should be bullet form and they should be precise and small.you can list any number of reasons you are confident about.Only
    focus on the current most possible Disease dont talk about other diseases in the above list
    """
    
    
    
for department in departments:
    print("department is",department)
    departmentdf=filterDepartment(df,department)
    print(len(departmentdf))
    caseNumbers = [i for i in range(1, len(departmentdf), 10)]
    # caseNumbers=[1]#,11,21]#31,41,51,61]
    print(caseNumbers)
    differential_diseases = departmentdf["differential_diagnosis"].apply(extract_disease_names_from_row).sum()
    refined_differential_diseases=[]
    for disease in differential_diseases:
        if len(disease) <20:
            refined_differential_diseases.append(disease)
    uniqueDiseases=departmentdf["principal_diagnosis"].unique().tolist()
    uniquePrimary=uniqueDiseases[:]
    uniqueDiseases.extend(refined_differential_diseases)
    uniqueDiseases=list(set(uniqueDiseases))
    
    
    
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis
    output should be formated as a dictionary where each element is a dictionary.each element will have following fields
    {"Final Diagnosis":Name of the most possible disease within above set of diseases
    "preasons":{
    "medical-history":list of precise reasons you are confident about based on given medical history
    "Physical-Examination":list of precise reasons you are confident about based on Physical examination
    "Laboratory-Examination":list of precise reasons you are confident about based on Laboratory examination
    "Image-Examination":list of precise reasons you are confident about based on Image examination
    }
    Each reasonings should be precise and small.you can list any number of reasons you are confident about.Only
    """
    
    
    
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top  most likely disease of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis
    
    output should be formated in the following format
    **Most Possible Disease Name from above list**
    ****Possible Reasons:****
    - **Medical History**: List of precise reasons based on the medical history.
    - **Physical Examination**: List of precise reasons based on the physical examination.
    - **Laboratory Examination**: List of precise reasons based on the laboratory examination.
    - **Imaging Examination**: List of precise reasons based on the imaging examination.
    Each reasonings should be precise and small.you can list any number of reasons you are confident about.Only
    focus on the current most possible Disease dont talk about other diseases in the above list
    """
    
    
    
    
    system_template = """You are a experienced doctor from {department} and you have provided below diagnosis with reasons
    for following clinical case of a patient containing the past medical history,physical examination,laboratory examination and Imaging examination
    where you had to select the best possible disease out of {diseases}
    Can you recheck step by step by comparing your diagnosis against patient clinical case 
    1.whether it aligns with physical examination,laboratory examination and Imaging examination of the patient?
    2.Check whether each reasoning is true for the predicted disease
    3.any above possible diseases {diseases} is more possible than currently detected disesase.If so change your diagnosis to new disease
    
    clinical History: {medical_history}
    
    your diagnosis: {diagnosis}
        
    Once you have rechecked your  diagnosis output should be formated in the following format
    ##Final Diagnosis##:Name of the most possible disease within above set of diseases
    **Possible Reasons:**
    - ****Medical History****: List of new precise reasons based on the medical history.
    - ****Physical Examination****: List of new precise reasons based on the physical examination.
    - ****Laboratory Examination****: List of new precise reasons based on the laboratory examination.
    - ****Imaging Examination****: List of new precise reasons based on the imaging examination.
    Each reasonings should be precise and small.you can list any number of reasons you are confident about.Only
    focus on the current most possible Disease dont talk about other diseases in the above list
    """
    
    
    
    # Create the system message
    # system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    # ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top  most likely disease of the patient using differential diagnosis using given below diseases 
    # the possible set of diseases are {diseases}
    # Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    # Once it is done select the top possible disease using above analysis and differential diagnosis
    
    # output should be formated in the following format
    # ##Final Diagnosis##:Name of the most possible disease within above set of diseases
    # **Possible Reasons:**
    # - ****Medical History****: List of precise reasons based on the medical history.
    # - ****Physical Examination****: List of precise reasons based on the physical examination.
    # - ****Laboratory Examination****: List of precise reasons based on the laboratory examination.
    # - ****Imaging Examination****: List of precise reasons based on the imaging examination.
    # Each reasonings should be precise and small.you can list any number of reasons you are confident about.Only
    # focus on the current most possible Disease dont talk about other diseases in the above list
    # """
    # system_template = """You are a experienced doctor from {department} and you will be provided with a medical case of a patient containing the past medical history
    # ,physical examination,laboratory examination and imaging examination results.Your task is to identify the top  most likely disease of the patient using differential diagnosis using given below diseases 
    # the possible set of diseases are {diseases}
    # Solve the medical case by thinking step by step 
    # 1.Summarize the medical case
    # 2.Understand How each physical examination,laboratory examination and Imaging examination help detecting above set of disases
    # 3.Furthur tests that need to be done to furthur confirm the diagnosis
    # 4.Select the best possible disease
    # 5.Format the final answer in the below format
    # - final_diagnosis: Name of the most possible disease within the above set of diseases.
    # - reasons:list  associated reasons for the final diagnosis. Each reason should be precise and brief and based on true facts.
    # - furthur tests: list of accurate furthur tests that need to be done to confirm the disases
    # Once done with analysis,select the top possible disease using above analysis
    
    # """