from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM

# Define LLMs
llm_gpt4o = LLM(
    model="openai/gpt-4o",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

llm_gpt4o_mini = LLM(
    model="openai/gpt-4o",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

llm_gpt4o_mini_2 = LLM(
    model="openai/gpt-4o-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY")
)

llm_gemini = LLM(
    model="gemini/gemini-1.5-flash-latest",
    temperature=0.3,
    api_key=os.getenv("GOOGLE_API_KEY")
)



def create_diagnostic_agent(name, llm):
    return Agent(
        role=f"Diagnostic Physician {name}",
        goal="Analyze a clinical case and select the most likely diagnosis using available data.",
        backstory=(
            "A highly skilled physician trained in internal medicine with deep experience in interpreting "
            "clinical cases involving respiratory, infectious, and oncological conditions."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )




def generate_diagnostic_prompt(case_data, differentials):
    return f"""
You are a diagnostic physician reviewing a clinical case. Your task:

1. Carefully interpret the structured clinical information.
2. Use your clinical reasoning to select the **single most likely diagnosis**.
3. Provide a clear, evidence-based rationale considering symptoms, labs, imaging, and history.
4. If necessary, discuss why other listed differentials are less likely.

Clinical Case:
{case_data}

Candidate Differentials:
{differentials}
"""

def create_diagnostic_task(agent,clinical_case_input,initial_potential_diseases):
    return Task(
        description=generate_diagnostic_prompt(clinical_case_input,initial_potential_diseases),
        expected_output="""
- Top Diagnosis: [Your chosen disease]
- Rationale: [Summarize your evidence-based reasoning]
""",
        agent=agent
    )


manager = Agent(
    role="Diagnostic Consensus Coordinator",
    goal="Facilitate diagnostic agreement between specialists through structured analysis and iterative discussion.",
    backstory="An expert clinical coordinator responsible for resolving differing diagnostic opinions among physicians through evidence-based discussion and conflict resolution.",
    llm=llm_gpt4o,
    allow_delegation=True,
    verbose=True
)


consensus_task = Task(
    description=f"""
As the **Diagnostic Consensus Coordinator**, you will perform a rigorous, stepwise evaluation of conflicting opinions from specialists. Follow this exact process:

### PHASE 1: DIAGNOSTIC SYNOPSIS
1. List all three physicians' diagnoses verbatim
2. Identify:
   - Points of agreement (≥2 physicians)
   - Critical disagreements (single-physician outliers)
3. Map rationales to clinical evidence:
   - Symptom pattern matching
   - Imaging pattern interpretation
   - Lab/result correlation
   - Epidemiological relevance

### PHASE 2: CONFLICT RESOLUTION FRAMEWORK
If diagnoses differ:
1. Create a weighted differential matrix using these criteria:
   - Specificity of imaging findings (cavitary lesions, distribution)
   - Temporal progression (subacute vs chronic)
   - Host factors (travel history, immune status)
   - Test performance characteristics (PPD vs Quantiferon reliability)
   - Inflammatory markers pattern (CRP vs ESR)

2. Initiate structured debate with these prompts:
   a) "Dr. X, explain why you prioritized [Diagnosis] over [Alternative Diagnosis]"
   b) "Dr. Y, justify your weighting of [Key Evidence] in your reasoning"
   c) "Dr. Z, clarify how you reconciled [Conflicting Data Point]"

3. Enforce evidence-based rebuttals:
   - Require citation of diagnostic criteria (e.g., ATS/IDSA guidelines)
   - Mandate discussion of test sensitivity/specificity
   - Demand quantification of pre-test probability

### PHASE 3: FINAL DIAGNOSTIC ASSESSMENT
Provide:
1. Final diagnosis with pathophysiological explanation
2. Diagnostic certainty scale:
   ★★★★★ Definitive (confirmatory test available)
   ★★★★☆ Strong (highly suggestive features)
   ★★★☆☆ Moderate (plausible but incomplete evidence)
3. Risk-stratified next steps:
   - Immediate interventions (if life-threatening)
   - Confirmatory testing algorithm
   - Alternative diagnosis monitoring plan
""",
    expected_output="""
DIAGNOSTIC PROCESS:
- Round 1 Diagnoses: [List all three]
- Disagreement Analysis: [Brief summary of divergent points]
- Shortlisted Diseases: [1-2 most plausible conditions]

ROUND 2 DISCUSSION:
[Simulated back-and-forth between doctors]

FINAL DIAGNOSIS:
- Diagnosis: [Final consensus result]
- Confidence Level: [High/Moderate/Low]
- Confirmatory Steps: [Recommended next tests or procedures]
""",
    agent=manager
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"crew_output_{timestamp}.log"

clinical_case_input = {
    "Patient Basic Information": "45-year-old male.",
    "Chief Complaint": "Chronic dry cough, night sweats, and weight loss over 4 weeks.",
    "Medical History": "Previously healthy. Worked in healthcare in India 6 months ago. No known TB contact. Non-smoker.",
    "Physical Examination": "T: 37.5°C, P: 78 bpm, R: 16, BP: 130/80 mmHg. Thin build, no acute distress. Lungs: Bibasilar crackles. No clubbing.",
    "Auxiliary Examination": "PPD Skin Test: Indeterminate. QuantiFERON-TB Gold: Negative.",
    "Imaging Examination": "Chest X-ray: Fibrocavitary lesions in upper lobes.",
    "Laboratory Examination": "WBC: 7.2×10⁹/L, CRP: 15 mg/L, ESR: 50 mm/hr.",
    "Pathological Examination": "None."
}

initial_potential_diseases = [
    "Pulmonary Tuberculosis (Latent/Reactivation)",
    "Fungal Pneumonia (e.g., Histoplasmosis)",
    "Chronic Bronchitis with Superimposed Infection",
    "Lung Cancer with Recurrent Infections"
]

doctor_1 = create_diagnostic_agent("Dr. Alpha", llm_gpt4o_mini)
doctor_2 = create_diagnostic_agent("Dr. Beta", llm_gpt4o_mini_2)

task_1 = create_diagnostic_task(doctor_1,clinical_case_input,initial_potential_diseases)
task_2 = create_diagnostic_task(doctor_2,clinical_case_input,initial_potential_diseases)

crew = Crew(
    agents=[doctor_1, doctor_2],
    tasks=[task_1, task_2, consensus_task],
    process=Process.hierarchical,
    manager_agent=manager,
    output_log_file=log_filename,
    verbose=True
)

result = crew.kickoff()
print(result)