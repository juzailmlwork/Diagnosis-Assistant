from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_ollama.llms import OllamaLLM
import json

def doctor_prompt_ollama_semi_ended(medical_history, modelname, diseases, department):
    model = OllamaLLM(model=modelname,temperature=0.1,num_predict=1500,num_ctx=12000)#4096)
    print("started model ",modelname)

    # system_template = """
    # You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. 
    # Your task is to identify the top 2 most likely diseases of the patient using differential diagnosis from the below given list of diseases:

    # Patient's medical case: {medical_history}
    
    # The possible set of diseases are {diseases}.These diseases belongs to {department}

    # Solve the medical case by thinking step by step:

    # 1. **Summarize the medical case.**

    # 2. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

    # 3. **Select the 4 Best Possible Diseases**: Choose the most 4 likely diseases based on the given medical case
    
    # 4  **Select the 2 best possible diseases**: Choose the most 2 likely diseases from 4 likely diseases after rechecking the case

    # 5. **Format the Diseases** in the below format:
    #     = **Disease1**:Name of the first most possible disease
    #         -**Reasons**:List associated reasons for the disease1 Each reason should be precise, brief, and based on true facts.
    #     = **Disease2**:Name of the second most possible disease
    #         -**Reasons**:List associated reasons for the disease2 Each reason should be precise, brief, and based on true facts.
    
    # """
    system_template = """
    You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. 
    Your task is to identify the top 2 most likely diseases of the patient using differential diagnosis from the below given list of diseases:

    Patient's medical case: {medical_history}
    
    The possible set of diseases are {diseases}.These diseases belongs to {department}

    Solve the medical case by thinking step by step:

    1. **Summarize the medical case.**

    2. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

    3. **Select the 2 Best Possible Diseases**: Choose the most 2 likely diseases based on the given medical case
    
    4  **Select the best possible disease**: Choose the best possible disease from above 2 likely diseases after rechecking the case

    5. **Format the Disease** in the below format:
        = **Best possible Disease**:Name of the best possible disease
            -**Reasons**:List associated reasons for the above selection.Each reason should be precise, brief, and based on true facts.
    """  
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])
    chain = chat_prompt | model

    results=chain.invoke({"department": department,"diseases": diseases,"medical_history":json.dumps(medical_history)})
    print("done for model",modelname)
    return results

def doctor_prompt_ollama(medical_history, modelname, diseases, department):
    model = OllamaLLM(model=modelname,temperature=0.1,num_predict=1500,num_ctx=12000)#4096)
    print("started model ",modelname)

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
    system_template = """
    You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. Your task is to identify the top most likely disease of the patient using differential diagnosis from the given list of diseases:

    The possible set of diseases are {diseases}.

    Solve the medical case by thinking step by step:

    1. **Summarize the medical case.**

    2. **Understand the Diseases**:For each disease in the above list 
        -   Explain what each of the diseases in the given set is, 
        -   Common symptoms
        -   how they are differentiated from one another using tests and symptoms.

    3. **Medical case Analysis**: Understand how each physical examination, laboratory examination, and imaging examination help in detecting the diseases mentioned above.

    5. **Select the Best Possible Disease**: Choose the most likely disease based on the given medical case and understanding of diseases.

    6. **Format the Final Answer** in the below format:
        - **Final Diagnosis**: Name of the most likely disease from the above set.
        - **Reasons**: List associated reasons for the final diagnosis. Each reason should be precise, brief, and based on true facts.
    
    """
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    # Create the human message
    human_template = "Patient's medical history: {medical_history}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Create the chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = chat_prompt | model

    results=chain.invoke({"department": department,"diseases": diseases,"medical_history":json.dumps(medical_history)})
    print("done for model",modelname)
    return results

def doctor_prompt_ollama_openended(medical_history, modelname, diseases, department):
    model = OllamaLLM(model=modelname,temperature=0.1,num_predict=1200,num_ctx=12000)#4096)
    print("started model ",modelname)

    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 4 most likely diseases of the patient using differential diagnosis
    from diseases occuring at {department}
    What are the top 4 most likely diagnoses? Be precise, listing one diagnosis per line, and try to cover many unique possibilities 
    The top 4 diagnoses are:
    """
    
    # system_template = """You are a experienced doctor from {department} and you will be provided with a medical case of a patient containing the past medical history
    # ,physical examination,laboratory examination and imaging examination results.
    # Your task is to identify the top 2 most likely diseases of the patient using differential diagnosis from diseases occuring at {department}
    # First analyze the medical case by thinking step by step regarding each physical examination,laboratory examination and Imaging examination
    # 1.Detailed analysis of the medical case
    # 2.Identifying top 2 possible diseases from {department}
    # 3.Format the top 2 possible diseases with reasons
    # """
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    # Create the human message
    human_template = "Patient's medical history: {medical_history}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Create the chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = chat_prompt | model

    results=chain.invoke({"department": department,"medical_history":json.dumps(medical_history)})
    print("done for model",modelname)
    return results


def doctor_prompt_ollama_self_refinement(medical_history, modelname, diseases, department,diagnosis):
    model = OllamaLLM(model=modelname,temperature=0.1,num_predict=1500,num_ctx=12000)#4096)
    print("started model ",modelname)

    # Create the system message
    system_template = """You are a experienced doctor from {department} and you have provided below diagnosis with reasons
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
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])
    chain = chat_prompt | model

    results=chain.invoke({"department": department,"diseases": diseases,"medical_history":json.dumps(medical_history),"diagnosis":diagnosis})
    print("done for model",modelname)
    return results


def doctor_prompt_ollama_combined(medical_history, model, diagnosis1, diagnosis2,department):
    model = OllamaLLM(model=model)


    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient
    and 2 clinical diagnosis from 2 different doctors. Your task is to identify the best disease based on the input from 2 different doctors 
    Investrigate both the diagnosis based on your expert knowledge and come to the best possible conclusion.Also note that sometimes those doctors make 
    mistakes too.I want you to thoroughly investrigate the case and use their views too
    output should be dictionary with  following fields
    1.disease-name:name of the disease based on above set
    2.reason:reason based on past history,physical examination,lab reports and image reports
    3.next-step:possible next examination needed to furthur confirm the disease
    
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    # Create the human message
    human_template = """
    medical case: {medical_history}
    diagnosis1: {diagnosis1}
    diagnosis2: {diagnosis2}
    """
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Create the chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = chat_prompt | model

    results=chain.invoke({"department": department,"diagnosis1": diagnosis1,"diagnosis2": diagnosis2,"medical_history":json.dumps(medical_history)})
    return results

from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from typing import List
import json
class DiagnosisReason(BaseModel):
    category: str = Field(description="The category of the examination, e.g., medical-history, Physical-Examination, Laboratory-Examination, Image-Examination")
    reasons: List[str] = Field(description="A list of precise reasons for the diagnosis based on the examination")
class FinalDiagnosis(BaseModel):
    final_diagnosis: str = Field(description="Name of the most possible disease within the given set of diseases")
    reasons: List[DiagnosisReason] = Field(description="A list of reasoning categories and the associated reasons for the final diagnosis")
def doctor_prompt_disease_restricted_ollama(medical_history, modelname, diseases, department):
    model = OllamaLLM(model=modelname, temperature=0.1, num_predict=1200, num_ctx=12000)
    print("started model ", modelname)
    prompt_template = f"""
    You are an experienced doctor from {department}, and you will be provided with the medical history of a patient containing past medical history,
    physical examination, laboratory examination, and imaging examination results. Your task is to identify the most likely disease of the patient using differential diagnosis from the given set of diseases:
    {diseases}
    Analyze step by step each aspect of the physical examination, laboratory examination, and imaging examination based on the above diseases.
    Once done, select the top possible disease using your analysis and differential diagnosis.
    Patient's medical history: {medical_history}.
    Please format your response as a JSON object with the following fields:
    - final_diagnosis: Name of the most possible disease within the above set of diseases.
    - reasons: A list of categories (e.g., medical-history, Physical-Examination) with associated reasons for the final diagnosis. Each reason should be precise and brief.
    JSON output:"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    output_parser = JsonOutputParser(pydantic_object=FinalDiagnosis)
    chain = prompt | model | output_parser
    output = chain.invoke(
        {
            "medical_history": medical_history,
            "diseases": diseases,
            "department": department,
        }
    )
    return output