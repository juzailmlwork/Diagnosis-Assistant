import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

def doctor_prompt_gpt(prompt,medical_history, model, diseases, department):
    chat = ChatOpenAI(model_name=model, temperature=0.1,max_tokens=1500)
    system_template = prompt
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

def evaluate_gpt(ground_truth_disease, prediction):
    chat = ChatOpenAI(model_name="gpt-4o", temperature=0.1, max_tokens=20)
    system_template = """
You are an assistant that compares the ground truth and predicted disease. You will be provided 
with a prediction from an AI model. Your task is to extract the best possible disease from the prediction text 
and compare it with the ground truth. First, extract the best possible disease given in the prediction text. Do not do anything else.
If the predicted result and the ground truth are the same, set the value of final to True; otherwise, set it to False.

Return a list in the exact format: ["best_possible_disease", final].
Do not use variables, extra text, or any additional characters. Only return the list.

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
    print(response.content,flush=True)
    return eval(response.content)

