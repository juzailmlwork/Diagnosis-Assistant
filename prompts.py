single_shot_disease_only_prompt="""
    You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top  most likely disease of the patient 
    
    Patient's medical case: {medical_history}
    
    The possible set of diseases are {diseases}.
    
    Answer:Most possible disease
    """

prompt_template = """
    You are an experienced doctor, and you will be provided with the medical history of a patient containing past medical history,
    physical examination, laboratory examination, and imaging examination results. 
    Patient's medical history: {medical_history}.
    
    Your task is to identify the most likely disease of the patient using differential diagnosis from the these diseases: {diseases}.

    Please format your response as a JSON object with the following fields:
    - final_diagnosis: Name of the most possible disease within the above set of diseases.
    - reasons: A list of categories (e.g., medical-history, Physical-Examination) with associated reasons for the final diagnosis. Each reason should be precise and brief.
    """

    
open_ended__top4_prompt="""
    You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 4 most likely diseases of the patient using differential diagnosis
    from diseases occuring at {department}
    What are the top 4 most likely diagnoses? Be precise, listing one diagnosis per line, and try to cover many unique possibilities 
    The top 4 diagnoses are:
    """
COT_prompt="""
    You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. Your task is to identify the top most likely disease of the patient using differential diagnosis from the given list of diseases:
    
    Patient's medical case: {medical_history}
    
    The possible set of diseases are {diseases}.

    Solve the medical case by thinking step by step:

    1. **Summarize the medical case.**

    2. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

    3. **Select the Best Possible Disease**: Choose the most likely disease based on the given medical case.

    4. **Format the Final Answer** in the below format:
        - **Final Diagnosis**: Name of the most likely disease from the above set.
        - **Reasons**: List associated reasons for the final diagnosis. Each reason should be precise, brief, and based on true facts.
    
    """
    

    


self_refinement_prompt="""You are a experienced doctor from {department} and you have provided below diagnosis with reasons
    for following clinical case of a patient containing the past medical history,physical examination,laboratory examination and Imaging examination
    where you had to select the best possible disease out of {diseases}
    Can you recheck step by step by comparing your diagnosis against patient clinical case 
    1.Check whether each reasoning is true for the predicted disease
    2.Is any diseases from {diseases} is more possible than currently detected disesase.If so change your diagnosis to new disease
    
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



        
    
compare_others_prompt="""You are a experienced doctor from {department} and you will be provided with a medical history of a patient
    and 2 clinical diagnosis from 2 different doctors. Your task is to identify the best disease based on the input from 2 different doctors 
    Investrigate both the diagnosis based on your expert knowledge and come to the best possible conclusion.Also note that sometimes those doctors make 
    mistakes too.I want you to thoroughly investrigate the case and use their views too
    output should be dictionary with  following fields
    1.disease-name:name of the disease based on above set
    2.reason:reason based on past history,physical examination,lab reports and image reports  
    """
    
 # system_template = """You are a experienced doctor from {department} and you will be provided with a medical case of a patient containing the past medical history
    # ,physical examination,laboratory examination and imaging examination results.
    # Your task is to identify the top 2 most likely diseases of the patient using differential diagnosis from diseases occuring at {department}
    # First analyze the medical case by thinking step by step regarding each physical examination,laboratory examination and Imaging examination
    # 1.Detailed analysis of the medical case
    # 2.Identifying top 2 possible diseases from {department}
    # 3.Format the top 2 possible diseases with reasons
    # """   


# shorten_choice_prompt="""
#     You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. 
#     Your task is to identify the top  most likely diseases of the patient using differential diagnosis from the below given list of diseases:

#     Patient's medical case: {medical_history}
    
#     The possible set of diseases are {diseases}.

#     Solve the medical case by thinking step by step:

#     1. **Summarize the medical case.**

#     2. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

#     3. **Select the 2 Best Possible Diseases**: Choose the most 2 likely diseases based on the given medical case
    
#     4  **Select the best possible disease**: Choose the best possible disease from above 2 likely diseases after rechecking the case

#     5. **Format the Disease** in the below format:
#         = **Best possible Disease**:Name of the best possible disease
#             -**Reasons**:List associated reasons for the above selection.Each reason should be precise, brief, and based on true facts.
#     """ 
   
    
# intrinsic_knowledge="""
#     You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. Your task is to identify the top most likely disease of the patient using differential diagnosis from the given list of diseases:

#     Patient's medical case: {medical_history}
    
#     The possible set of diseases are {diseases}.

#     Solve the medical case by thinking step by step:

#     1. **Summarize the medical case.**

#     2. **Understand the Diseases**:For each disease in the above list 
#         -   Explain what each of the diseases in the given set is, 
#         -   Common symptoms
#         -   how they are differentiated from one another using tests and symptoms.

#     3. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

#     5. **Select the Best Possible Disease**: Choose the most likely disease based on the given medical case and understanding of diseases.

#     6. **Format the Final Answer** in the below format:
#         - **Final Diagnosis**: Name of the most likely disease from the above set.
#         - **Reasons**: List associated reasons for the final diagnosis. Each reason should be precise, brief, and based on true facts.
    
#     """


# ollama_combined_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient
#     and 2 clinical diagnosis from 2 different doctors. Your task is to identify the best disease based on the input from 2 different doctors 
#     Investrigate both the diagnosis based on your expert knowledge and come to the best possible conclusion.Also note that sometimes those doctors make 
#     mistakes too.I want you to thoroughly investrigate the case and use their views too
#     output should be dictionary with  following fields
#     1.disease-name:name of the disease based on above set
#     2.reason:reason based on past history,physical examination,lab reports and image reports
    
#     """