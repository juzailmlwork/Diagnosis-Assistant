from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_ollama.llms import OllamaLLM
import json

def doctor_prompt_ollama(medical_history, modelname, diseases, department):
    model = OllamaLLM(model=modelname,temperature=0.1,num_predict=1200,num_ctx=12000)#4096)
    print("started model ",modelname)

    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top  most likely disease of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis
    
    output should be formated in the following format
    ##Final Diagnosis##:Name of the most possible disease within above set of diseases
    **Possible Reasons:**
    - ****Medical History****: List of precise reasons based on the medical history.
    - ****Physical Examination****: List of precise reasons based on the physical examination.
    - ****Laboratory Examination****: List of precise reasons based on the laboratory examination.
    - ****Imaging Examination****: List of precise reasons based on the imaging examination.
    Each reasonings should be precise and small.you can list any number of reasons you are confident about.Only
    focus on the current most possible Disease dont talk about other diseases in the above list
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


def doctor_prompt_ollama(medical_history, modelname, diseases, department,diagnosis):
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
