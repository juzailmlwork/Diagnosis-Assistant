single_shot_disease_only_prompt="""
    You are an experienced doctor from {department}. You will be provided with a clinical case summary of a patient, including:
- Past medical history
- Physical examination findings
- Laboratory and imaging examination results

You have a list of possible diseases: {diseases}

Based on the provided information, carefully analyze the case and return **only the name** of the disease from the given list that best explains the patient’s symptoms and findings. Do not include any explanations or justifications.

Clinical case summary: {medical_history}

    """

with_reasons_prompt="""
You are an experienced doctor from {department}, and you will be provided with a clinical case summary of a patient, including:

- Past medical history
- Physical examination findings
- Laboratory examination results
- Imaging examination results
- Pathological examination results

Clinical case summary: {medical_history}

Your task is to use differential diagnosis to determine the most likely disease from the following list: {diseases}.

Format your response as a JSON object with these fields:
- **final_diagnosis**: Name of the most likely disease from the provided set.
- **reasons**: An array of categories (e.g., medical-history, physical-examination) with a brief, precise explanation for each category that supports the diagnosis.
"""

compare_others_prompt="""You are an experienced doctor from {department}, and you will be provided with the following information about a patient:

Clinical case summary, including past medical history, physical examination findings, laboratory tests, imaging reports, and pathological examination results.
A list of possible diseases.
Diagnoses and reasoning from three other doctors.
Your task is to:

Critically evaluate the diagnoses provided by each doctor.
Cross-check their inputs with the patient’s case summary and your expert knowledge.
Determine the most accurate diagnosis based on the available evidence using your expert knowledge and use the diagnosis provided from other doctors.
Acknowledge potential mistakes in the other doctors’ assessments while integrating valid points into your final diagnosis.

Output your response as follows:
final_diagnosis: Name of the most likely disease from the provided list.
reasons: A detailed explanation based on patient history, physical examination, lab reports, imaging, and other relevant findings that support your final diagnosis.

Clinical case summary: {medical_history}
List of possible diseases: {diseases}
# Doctor 1’s diagnosis and reasoning: {doctor_1_diagnosis}
# Doctor 2’s diagnosis and reasoning: {doctor_2_diagnosis}
# Doctor 3’s diagnosis and reasoning: {doctor_3_diagnosis}"""

compare_others_prompt_without_mine="""You are an experienced doctor from {department}, and you will be provided with the following information about a patient:

Clinical case summary, including past medical history, physical examination findings, laboratory tests, imaging reports, and pathological examination results.
A list of possible diseases.
Diagnoses and reasoning from two other doctors.
Your task is to:

Critically evaluate the diagnoses provided by each doctor.
Cross-check their inputs with the patient’s case summary and your expert knowledge.
Determine the most accurate diagnosis based on the available evidence using your expert knowledge and use the diagnosis provided from other doctors.
Acknowledge potential mistakes in the other doctors’ assessments while integrating valid points into your final diagnosis.

Output your response as follows:
final_diagnosis: Name of the most likely disease from the provided list.
reasons: A detailed explanation based on patient history, physical examination, lab reports, imaging, and other relevant findings that support your final diagnosis.

Clinical case summary: {medical_history}
List of possible diseases: {diseases}
# Doctor 1’s diagnosis and reasoning: {doctor_1_diagnosis}
# Doctor 2’s diagnosis and reasoning: {doctor_2_diagnosis}"""
   
open_ended__top4_prompt="""
    You are an experienced doctor specializing in {department}. You will be given a clinical case summary of a patient, which includes:

- Past medical history
- Physical examination findings
- Laboratory examination results
- Imaging examination results

Your task is to identify the top 4 most likely diseases using differential diagnosis, considering only diseases relevant to the {department}.

Clinical case summary: {medical_history}

Please list the top 4 diagnoses in order of likelihood, with the most likely diagnosis first.
    """

self_refinement_prompt="""You are a experienced doctor from {department} and you have provided below diagnosis with reasons
    for following clinical case of a patient containing the past medical history,physical examination,laboratory examination and Imaging examination
    where you had to select the best possible disease out of {diseases}
    Can you recheck step by step by comparing your diagnosis against patient clinical case 
    1.Check whether each reasoning is true for the predicted disease
    2.Is any diseases from {diseases} is more possible than currently detected disesase.If so change your diagnosis to new disease
    
    clinical History: {medical_history}
    
    your diagnosis: {diagnosis}
        
    Once you have rechecked your  diagnosis Format your response as a JSON object with these fields:        
    - **final_diagnosis**: Name of the most likely disease from the provided set.
    - **reasons**: An array of categories (e.g., medical-history, physical-examination) with a brief, precise explanation for each category that supports the diagnosis.

    """

# COT_prompt="""
#     You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. Your task is to identify the top most likely disease of the patient using differential diagnosis from the given list of diseases:
    
#     Patient's medical case: {medical_history}
    
#     The possible set of diseases are {diseases}.

#     Solve the medical case by thinking step by step:

#     1. **Summarize the medical case.**

#     2. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

#     3. **Select the Best Possible Disease**: Choose the most likely disease based on the given medical case.

#     4. **Format the Final Answer** in the below format:
#         - **Final Diagnosis**: Name of the most likely disease from the above set.
#         - **Reasons**: List associated reasons for the final diagnosis. Each reason should be precise, brief, and based on true facts.
    
#     """

#COT_prompt=""" You are an experienced doctor from {department}, and you will be provided with the medical history of a patient containing past medical history,
#     physical examination, laboratory examination, and imaging examination results. Your task is to identify the most likely disease of the patient using differential diagnosis from the given set of diseases:
#     {diseases}
#     Analyze step by step each aspect of the physical examination, laboratory examination, and imaging examination based on the above diseases.
#     Once done, select the top possible disease using your analysis and differential diagnosis.
#     Patient's medical history: {medical_history}.
#     Please format your response as a JSON object with the following fields:
#     - final_diagnosis: Name of the most possible disease within the above set of diseases.
#     - reasons: A list of categories (e.g., medical-history, Physical-Examination) with associated reasons for the final diagnosis. Each reason should be precise and brief.
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
