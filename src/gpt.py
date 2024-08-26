import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def doctor_prompt_gpt(medical_history, model, diseases, department):
    print("the model name is",model)
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1000)#0.01

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

    # Format the messages
    messages = chat_prompt.format_prompt(
        department=department,
        diseases=diseases,
        medical_history=json.dumps(medical_history)
    ).to_messages()
    response = chat(messages)
    print("done for model",model)
    return response.content

def doctor_prompt_gpt_self_confinement(medical_history, model, diseases, department,diagnosis):
    print("the model name is",model)
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1000)#0.01

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

    # Format the messages
    messages = chat_prompt.format_prompt(
        department=department,
        diseases=diseases,
        medical_history=json.dumps(medical_history),
        diagnosis=diagnosis
    ).to_messages()
    response = chat(messages)
    print("done for model",model)
    return response.content

