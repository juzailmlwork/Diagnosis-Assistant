import json
def doctor_prompt(client,medical_history,doctor="doctor"):
  completion = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model="gpt-4",
    messages=[
      # {
      #   "role": "system",
      #   "content": """You are a dermotologist and you will be provided with a medical history of a patient 
      #   and your task is to identify possible disease patient might have using differential diagnosis.make sure you have only knolwedge about skin related disease.limit yourself to top 3 possible diseases.
      #   you should give the output in the following format
      #   {diease_name:possible_disease1
      #   reason:the reason for conclusion based on medical history and facts
      #   furthur_reports_needed:the furthur reports needed to conclude
      #   other_doctors:if you cant predict it which specialist will you forward this case to
      #   proof:the proof of conclusion citing document with links},
      #   {diease_name:possible_disease2
      #   reason:the reason for conclusion based on medical history and facts
      #   furthur_reports_needed:the furthur reports needed to conclude
      #   other_doctors:if you cant predict it which specialist will you forward this case to
      #   proof:the proof of conclusion citing document with links}
      # """
      # },
    #   {
    #   "role": "system",
    #   "content": """You are a doctor and you will be provided with a medical history of a patient 
    #   and your task is to identify possible disease patient might have using differential diagnosis.limit yourself to top 3 possible diseases.
    #   rather than mri scan try to use ct scan if possible
    #   you should give the output in the following format
    #   { part/system:body system1
    #     what should be assesed:llist of things to be assesed
    #   }
    #   {diease_name:possible_disease1
    #   reason:the reason for conclusion based on medical history and facts
    #   furthur_reports_needed:the furthur reports needed to conclude
    #   next_step:this can be what furthur report needed or what is the treatment/medication or what is the physical examination that should be checked
    #   department:to which department the case should be forwarded to},
    #   {diease_name:possible_disease2
    #   reason:the reason for conclusion based on medical history and facts
    #   furthur_reports_needed:the furthur reports needed to conclude
    #   next_step:this can be what furthur report needed or what is the treatment/medication or what is the physical examination that should be check
    #   department:to which department the case should be forwarded to
    #   }
    # """
    # },
    {
      "role": "system",
      "content": f"""You are a {doctor} and you will be provided with a medical history of a patient 
      and your task is to identify possible disease patient might have using differential diagnosis.limit yourself to top 3 possible diseases.
      rather than mri scan try to use ct scan if possible
      you have two choices 1.provide a dictionary of medicalexmination you needed furthur citing why they are required 2.possible diseases based on the input and how you came into conclusion
    """
      
    },
      {
        "role": "user",
         "content": json.dumps(medical_history)    
      }
    ],
    temperature=0.01,
    max_tokens=1000,
    top_p=1
  )
  print(completion.choices)
  print(completion.choices[0].message.content)
