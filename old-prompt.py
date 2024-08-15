def doctor_prompt_disease_restricted_output_parser(medical_history, model, diseases, department):
    # Initialize the ChatOpenAI model
    chat = ChatOpenAI(model_name=model, temperature=0.01)

    # Define the output parser
    response_schemas = [
        ResponseSchema(name="diagnosis", description="The top 3 most likely diseases based on the medical history"),
        ResponseSchema(name="reasoning", description="Explanation of how you arrived at these diagnoses. State all possible reasons precisely for each disease."),
        ResponseSchema(name="further_examinations", description="A dictionary of additional medical examinations needed, with reasons")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    # Create the system message
    system_template = """You are a experienced doctor from {department} and you will be provided with a medical history of a patient. 
    Your task is to identify the top 3 most likely diseases of the patient using differential diagnosis considering all the phyical examination,lab reports and image. 
    Only select from this set of diseases: {diseases}

    {format_instructions}
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
        format_instructions=format_instructions,
        medical_history=json.dumps(medical_history)
    ).to_messages()

    # Get the response
    response = chat(messages)

    # Parse the output
    parsed_output = output_parser.parse(response.content)
    print("\nParsed output:")
    print(json.dumps(parsed_output, indent=2))

    return parsed_output