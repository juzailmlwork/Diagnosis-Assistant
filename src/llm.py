import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

def doctor_prompt_disease_restricted_output_parser(medical_history, model, diseases, department):
    # Initialize the ChatOpenAI model
    chat = ChatOpenAI(model_name=model, temperature=0.01)


    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient. 
    Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis considering all the phyical examination,lab reports and image. 
    Only select from this set of diseases: {diseases}
    output should be formated as a list where each element is a dictionary.each element will have following fields
    1.disease-name:name of the disease based on above set
    2.reason:reason based on past history,physical examination,lab reports and image reports
    3.next-step:possible next examination needed to furthur confirm the disease
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
    print
    # Get the response
    response = chat(messages)
    print(response.content)
    # # Parse the output
    # parsed_output = output_parser.parse(response.content)
    # print("\nParsed output:")
    # print(json.dumps(parsed_output, indent=2))

    return True

def doctor_prompt_disease_restricted_output_parser2(medical_history, model, diseases, department):
    # Initialize the ChatOpenAI model
    chat = ChatOpenAI(model_name=model, temperature=0.01)


    # Create the system message
    system_template = """
    You are an experienced {department} clinician. Based on the given clinical case summary, please
    analyze and provide a professional, detailed, and comprehensive clinical diagnosis, including the
    following 3 parts:
    1. Principal Diagnosis: The name of a disease that is most harmful to the patient’s physical health and
    needs immediate treatment
    2. Diagnostic Basis: List the basis for your preliminary diagnosis based on medical history,physical examination,
    lab examination and image reports
    3. Differential Diagnosis: List several diseases that could cause the patient’s current symptoms and
    briefly explain why you exclude them. If you believe differential diagnosis is unnecessary, please
    directly response “The diagnosis is clear and no differentiation is needed.”
    Only select from this set of diseases {diseases}
    The following is the given clinical case summary:
    {case_summary}
    Your clinical diagnosis:
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])
    
    messages = chat_prompt.format_prompt(
        department=department,
        diseases=diseases,
        case_summary=json.dumps(medical_history)
    ).to_messages()
    response = chat(messages)
    return response
