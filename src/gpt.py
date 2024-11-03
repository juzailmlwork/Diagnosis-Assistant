import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

def doctor_prompt_gpt_semi_ended(medical_history, model, diseases, department):
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1500)
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

    # Format the messages
    messages = chat_prompt.format_prompt(
        department=department,
        diseases=diseases,
        medical_history=json.dumps(medical_history)
    ).to_messages()
    response = chat(messages)
    return response.content

def doctor_prompt_gpt_intrinsic_knowledge(medical_history, model, diseases, department):
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1500)
    system_template = """
    You are an experienced doctor from {department}, and you will be provided with a medical case of a patient containing their past medical history, physical examination, laboratory examination, and imaging examination results. Your task is to identify the top most likely disease of the patient using differential diagnosis from the given list of diseases:

    Patient's medical case: {medical_history}
    
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

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Format the messages
    messages = chat_prompt.format_prompt(
        department=department,
        diseases=diseases,
        medical_history=json.dumps(medical_history)
    ).to_messages()
    response = chat(messages)
    return response.content

def doctor_prompt_gpt_COT(medical_history, model, diseases, department):
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1500)#0.01
    
    system_template = """
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
    return response.content


def doctor_prompt_gpt_single_shot(medical_history, model, diseases, department):
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1000)#0.01

    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient containing the past medical history
    ,physical examination,laboratory examination and Imaging examination results.Your task is to identify the top  most likely disease of the patient 
    
    Patient's medical case: {medical_history}
    
    The possible set of diseases are {diseases}.
    
    Answer:Most possible disease
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
    return response.content

def doctor_prompt_gpt_open_ended(medical_history, model, department):
    print("the model name is",model)
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1000)#0.01

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

    # Format the messages
    messages = chat_prompt.format_prompt(
        department=department,
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


def evaluate_gpt(ground_truth_disease, prediction):
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1, max_tokens=20)
    system_template = """
    You are an assistant that compares the ground truth and predicted disease. You will be provided 
    with a prediction from an AI model. Your task is to extract the best possible disease from the prediction text 
    and compare it with the ground truth. First, extract the best possible disease given in the prediction text. Do not do anything else.
    Then If the predicted result and the ground truth are the same, set the value 
    of final to True; otherwise, set it to False. Now return a list like [best_possible_disease, final].
    
    The ground truth is: {ground_truth_disease}
    The predicted text is: {prediction}
    """ 

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])

    # Format the messages
    messages = chat_prompt.format_prompt(
        ground_truth_disease=ground_truth_disease,
        prediction=json.dumps(prediction)
    ).to_messages()
    
    response = chat(messages)

    return eval(response.content)

