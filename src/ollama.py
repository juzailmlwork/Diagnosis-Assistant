from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_ollama.llms import OllamaLLM
import json

def doctor_prompt_disease_restricted_ollama(medical_history, model, diseases, department):
    model = OllamaLLM(model=model,temperature=0.1,num_predict=1000,num_ctx=12000)#4096)


    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top 3 possible disease using above analysis and differential diagnosis
    output should be formated as a list where each element is a dictionary.each element will have following fields
    1.disease-name:name of the disease based on above set
    2.reason:Detailed reason based on past history,physical examination,lab reports and image reports
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    # Create the human message
    human_template = "Patient's medical history: {medical_history}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    # Create the chat prompt
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = chat_prompt | model

    results=chain.invoke({"department": department,"diseases": diseases,"medical_history":json.dumps(medical_history)})
    return results


def doctor_prompt_disease_restricted_ollama_combined(medical_history, model, diagnosis1, diagnosis2,department):
    model = OllamaLLM(model=model)


    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis.I need you to not miss any examination reports and think step by step what each
    examination report suggest
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
    Detailed reasons based on past medical history,physical examination,laboratory examination and image examination
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