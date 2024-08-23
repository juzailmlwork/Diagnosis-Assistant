import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def doctor_prompt_disease_restricted_gpt(medical_history, model, diseases, department):
    print("the model name is",model)
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1000)#0.01

    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top most likely diseases of the patient using differential diagnosis using given below diseases 
    the possible set of diseases are {diseases}
    Analyze by thinking step by step each physical examination,laboratory examination and Imaging examination based on above disases
    Once it is done select the top possible disease using above analysis and differential diagnosis
    
    output should be formated in the below format
    ##Final Diagnosis##:Name of the most possible disease within above set of diseases
    ##reasons##:
    medical-history:list of precise reasons you are confident about based on given medical history
    Physical-Examination:list of precise reasons you are confident about based on Physical examination
    Laboratory-Examination:list of precise reasons you are confident about based on Laboratory examination
    Image-Examination:list of precise reasons you are confident about based on Image examination
    Each reasonings should be precise and small.you can list any number of reasons you are confident about
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

