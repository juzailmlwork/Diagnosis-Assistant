from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_ollama.llms import OllamaLLM
import json
def doctor_prompt_ollama(prompt,medical_history, modelname, diseases, department):
    model = OllamaLLM(model=modelname,temperature=0.1,num_predict=1500,num_ctx=4096)#1500

    system_template = prompt
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])
    chain = chat_prompt | model
    results=chain.invoke({"department": department,"diseases": diseases,"medical_history":json.dumps(medical_history)})
    print("done for model",modelname)
    return results


# def doctor_prompt_ollama_combined(medical_history, model, diagnosis1, diagnosis2,department):
#     model = OllamaLLM(model=model)


#     # Create the system message
#     system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient
#     and 2 clinical diagnosis from 2 different doctors. Your task is to identify the best disease based on the input from 2 different doctors 
#     Investrigate both the diagnosis based on your expert knowledge and come to the best possible conclusion.Also note that sometimes those doctors make 
#     mistakes too.I want you to thoroughly investrigate the case and use their views too
#     output should be dictionary with  following fields
#     1.disease-name:name of the disease based on above set
#     2.reason:reason based on past history,physical examination,lab reports and image reports
    
#     """
#     system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

#     # Create the human message
#     human_template = """
#     medical case: {medical_history}
#     diagnosis1: {diagnosis1}
#     diagnosis2: {diagnosis2}
#     """
#     human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

#     # Create the chat prompt
#     chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
#     chain = chat_prompt | model

#     results=chain.invoke({"department": department,"diagnosis1": diagnosis1,"diagnosis2": diagnosis2,"medical_history":json.dumps(medical_history)})
#     return results

# from langchain.prompts import ChatPromptTemplate
# from langchain_ollama.llms import OllamaLLM
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_core.output_parsers import JsonOutputParser
# from typing import List
# import json
# class DiagnosisReason(BaseModel):
#     category: str = Field(description="The category of the examination, e.g., medical-history, Physical-Examination, Laboratory-Examination, Image-Examination")
#     reasons: List[str] = Field(description="A list of precise reasons for the diagnosis based on the examination")
# class FinalDiagnosis(BaseModel):
#     final_diagnosis: str = Field(description="Name of the most possible disease within the given set of diseases")
#     reasons: List[DiagnosisReason] = Field(description="A list of reasoning categories and the associated reasons for the final diagnosis")


# def doctor_prompt_disease_restricted_ollama(medical_history, modelname, diseases, department):
#     model = OllamaLLM(model=modelname, temperature=0.1, num_predict=1200, num_ctx=12000)
#     print("started model ", modelname)
#     prompt_template = f"""
#     You are an experienced doctor from {department}, and you will be provided with the medical history of a patient containing past medical history,
#     physical examination, laboratory examination, and imaging examination results. Your task is to identify the most likely disease of the patient using differential diagnosis from the given set of diseases:
#     {diseases}
#     Analyze step by step each aspect of the physical examination, laboratory examination, and imaging examination based on the above diseases.
#     Once done, select the top possible disease using your analysis and differential diagnosis.
#     Patient's medical history: {medical_history}.
#     Please format your response as a JSON object with the following fields:
#     - final_diagnosis: Name of the most possible disease within the above set of diseases.
#     - reasons: A list of categories (e.g., medical-history, Physical-Examination) with associated reasons for the final diagnosis. Each reason should be precise and brief.
#     JSON output:"""
#     prompt = ChatPromptTemplate.from_template(prompt_template)
#     output_parser = JsonOutputParser(pydantic_object=FinalDiagnosis)
#     chain = prompt | model | output_parser
#     output = chain.invoke(
#         {
#             "medical_history": medical_history,
#             "diseases": diseases,
#             "department": department,
#         }
#     )
#     return output