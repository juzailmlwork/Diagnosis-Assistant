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


# clinical_case_input = {"Patient basic information": "Elderly female, 88 years old.", "Chief complaint": "Fatigue for 1 week, fever, chills, and dysuria for 3 days.", "Medical history": "The patient started to experience general fatigue without any obvious cause a week ago, with poor appetite but no significant nausea, vomiting, abdominal pain, diarrhea, generalized bone and joint pain, chest tightness or asthma, and increased drowsiness. Symptoms such as urgency, frequency and dysuria were not present and were not given special attention; 3 days ago, the aforementioned symptoms worsened, accompanied by chills, fever with a maximum temperature of 38.7\u00b0C, general muscular soreness and discomfort with unclear descriptions, dysuria, particularly towards the end of urination, cloudy urine, without obvious urgency or frequency, discomfort in the lower back with unclear descriptions, no significant cough, sputum production, chest tightness, chest pain, or difficulty breathing, also not given special attention; 2 days ago, intravenous drip treatment with Levofloxacin was administered upon consultation, yet the fever recurred. Past medical history includes hypertension for 8 years.", "Physical examination": "No eyelid swelling, lips were rosy, chest percussion on both lungs showed clear sound, clear breath sounds in both lungs without audible dry or wet rales, rhythmic heart rate without pathological murmurs. Both kidney areas showed no tenderness to pressure and mild tenderness to percussion, no apparent abnormalities in abdominal vascular pulsations, and no significant tenderness upon palpation of bilateral ureteral pressure points. No edema in the lower extremities.", "Laboratory examination": {"routine_blood_test": "1 White Blood Cells WBC 8.1 *10^9/L 3.5-9.5; 2 Lymphocyte Percentage LYMPH% 12.5 \u2193 % 20.0-50.0; 3 Monocyte Percentage MONO% 7.9 % 3.0-10.0; 4 Neutrophil Percentage NEUT% 78.7 \u2191 % 40.0-75.0; 5 Lymphocyte Absolute Value LYMPH# 1.0 \u2193 *10^9/L 1.1-3.2; 6 Monocyte Absolute Value MONO# 0.64 \u2191 *10^9/L 0.10-0.60; 7 Neutrophil Absolute Value NEUT# 6.4 \u2191 *10^9/L 1.8-6.3; 8 Red Blood Cells RBC 4.4 *10^12/L 3.8-5.1; 9 Hemoglobin HGB 135 g/L 115-150; 10 Hematocrit HCT 40.1 % 35.0-45.0; 11 Mean Corpuscular Volume MCV 91 fL 82-100; 12 Mean Corpuscular Hemoglobin MCH 31 pg 27-34; 13 Mean Corpuscular Hemoglobin Concentration MCHC 337 g/L 316-354; 14 Red Cell Distribution Width (CV) RDW-CV 12.6 % <15.0; 15 Platelet Count (Impedance Method) PLT-I 228 *10^9/L 125-350; 16 Mean Platelet Volume MPV 10.5 \u2191 fL 8.0-10.0; 17 Platelet Distribution Width PDW 16.3 fL 9.0-17.0; 18 Eosinophil Percentage EO% 0.4 % 0.4-8.0; 19 Basophil Percentage BASO% 0.5 % 0.0-1.0; 20 Eosinophil Absolute Value EO# 0.03 *10^9/L 0.02-0.52; 21 Basophil Absolute Value BASO# 0.04 *10^9/L 0-0.06; 22 Plateletcrit PCT 0.24 % 0.17-0.35; 23 C-Reactive Protein CRP 68.74 \u2191 mg/L 0-4.00;", "blood_biochemistry_test": "1. Alanine Aminotransferase (ALT) 16 U/L 7-40; 2. Aspartate Aminotransferase (AST) 24 U/L 13-35; 3. Cholinesterase (CHE) 7066 U/L 5300-11300; 4. AST/ALT ratio 1.50; 5. Total Bile Acid (TBA) 2.6 \u03bcmol/L <12.0; 6. Total Protein (TP) 65.1 g/L 65.0-85.0; 7. Albumin (ALB) 38.7 \u2193 g/L 40.0-55.0; 8. Globulin (GLB) 26.4 g/L 20.0-40.0; 9. Albumin/Globulin Ratio (A/G) 1.5 1.2-2.4; 10. Total Bilirubin (TBIL) 44.3 \u2191 \u03bcmol/L <23.0; 11. Direct Bilirubin (DBIL) 7.5 \u2191 \u03bcmol/L <4.0; 12. Indirect Bilirubin (IBIL) 36.8 \u2191 \u03bcmol/L <19.0; 13. Alkaline Phosphatase (ALP) 99 U/L 40-150; 14. Lactate Dehydrogenase (LDH) 212 U/L 120-250; 15. Gamma-Glutamyl Transferase (GGT) 21 U/L 7-45; 16. Prealbumin (PA) 119.9 \u2193 mg/L 180.0-350.0; 17. Creatine Kinase (CK) 34 \u2193 U/L 40-200; 18. Creatine Kinase-MB Mass (CK-MBmass) 0.3 \u2193 ng/mL 0.6-6.3; 19. Alpha-Hydroxybutyrate Dehydrogenase (HBDH) 144 U/L 72-182; 20. Glucose (GLU) 4.91 mmol/L 3.90-6.10; 21. Urea 4.36 mmol/L 3.10-8.80; 22. Creatinine (Cr) 75 \u03bcmol/L 41-81; 23. Uric Acid (UA) 225 \u03bcmol/L 155-357; 24. Total Cholesterol 4.09 mmol/L <5.18; 25. Triglycerides (TG) 0.97 mmol/L <1.70; 26. High-Density Lipoprotein Cholesterol (HDL-C) 1.11 mmol/L >1.04; 27. Low-Density Lipoprotein Cholesterol (LDL-C) 2.86 mmol/L <3.37; 28. Apolipoprotein A1 (ApoA1) 1.20 g/L 1.05-2.05; 29. Apolipoprotein B (ApoB) 0.87 g/L 0.55-1.30; 30. ApoA1/ApoB Ratio 1.38 1.10-2.70; 31. Calcium (Ca) 2.31 mmol/L 2.11-2.52; 32. Phosphorus (P) 1.15 mmol/L 0.85-1.51; 33. Iron (Fe) 4.1 \u2193 \u03bcmol/L 7.8-32.2; 34. Magnesium (Mg) 0.79 mmol/L 0.75-1.02; 35. Potassium (K) 4.00 mmol/L 3.50-5.30; 36. Sodium (Na) 140 mmol/L 137-147; 37. Chloride (Cl) 103.0 mmol/L 99.0-110.0; 38. Bicarbonate (CO2) 22.4 mmol/L 21.0-31.0; 39. Anion Gap (AG) 14.6 mmol/L 8.0-16.0; 40. Adenosine Deaminase (ADA) 17.5 U/L 4.0-22.0; 41. Osmolality (OSM) 279 mOsm/kg 275-300; 42. Cystatin C (cys-c) 0.95 mg/L 0.60-1.30; 43. Hemolysis (HEM) -; 44. Jaundice (ICT) +; 45. Lipemia (LIP) -; 46. Interleukin-6 (IL-6) 16.70 \u2191 pg/mL <6.4; 47. Serum Amyloid A (SAA) 40.20 \u2191 mg/L <10; 48. Procalcitonin (PCT) 0.187 \u2191 ng/mL 0-0.046;", "routine_urine_test": "1 pH 5.5 4.5-8.0; 2 Color Pale Yellow Pale Yellow; 3 Transparency Clear Clear; 4 Specific Gravity SG 1.020 1.003-1.030; 5 Protein PRO Negative (-) Negative; 6 Glucose GLU Negative (-) Negative; 7 Ketone Bodies KET Weakly Positive Negative; 8 Bilirubin BIL Negative (-) Negative; 9 Urobilinogen UBG Normal Normal; 10 Nitrite NIT Negative (-) Negative; 11 Leukocyte Esterase LEU 2+ Negative; 12 Occult Blood BLD 1+ Negative; 13 Vitamin C VC Negative (-) Negative; 14 White Blood Cell Count WBC 226 \u2191 /\u03bcL 0-28; 15 Red Blood Cell Count RBC 44 \u2191 /\u03bcL 0-17; 16 Epithelial Cell Count EC 57 \u2191 /\u03bcL 2-10; 17 Cast Count CAST 19 \u2191 /\u03bcL 0-2; 18 Bacterial Count BACT 85 /\u03bcL 0-100; 19 Pathological Cast Path.CAST 3 \u2191 /\u03bcL 0-1; 20 Small Round Epithelial Cells SRC 43 /\u03bcL; 21 Yeast-Like Cells YLC 0 /\u03bcL; 22 Conductivity CONDCT 10 mS/cm 5-38; 23 Conductivity Information Cond.-Inf 2nd Level; 24 Red Blood Cell Information RBC-Inf Unclassified; 25 Crystal Examination X,TAL 0 /\u03bcL; 26 Mucus Filaments NYS 3 /\u03bcL; 27 White Blood Cells WBC 5-10 /HP 0-5; 28 Red Blood Cells RBC 0-1 /HP 0-5; 29 Epithelial Cells EC Negative Negative; 30 Transparent Cast Negative Negative; 31 Granular Cast Negative Negative; 32 Crystals X,TAL Negative Negative; 33 Other Other Negative; 34 Mucus Filaments Negative Negative; 35 Waxy Cast Negative Negative;"}, "Imageological examination": {"color_doppler_ultrasound": "Kidneys: Both kidneys are normal in shape and size, with smooth and regular outlines. The corticomedullary junction is clear, and the parenchymal echo is evenly distributed. No separation was observed in the collecting system. No obvious dilation was observed in both ureters. Bladder: It is well-filled, with a smooth and continuous wall. No abnormal echo was observed in the cavity. After urination, about 6ml of residue remains in the bladder. CDFI: No abnormal blood flow signals were observed."}, "Auxillary examination": "(1)", "Pathological examination": "Not available."}
# initial_potential_diseases =["Acute pyelonephritis", "Urinary system stones", "Urinary tract tumor", "Urinary tuberculosis"]

clinical_case_input ={
            "Patient Basic Information":"Elderly female, 59 years old.",
            "Chief Complaint":"Poor appetite, nausea accompanied by oliguria for over a month.",
            "Medical History":"One month ago, the patient developed poor appetite, nausea, and oliguria (specific urine volume unknown) without any obvious cause. This was accompanied by occasional dizziness. Symptoms did not alleviate and remained untreated. The patient later reported that the aforementioned symptoms persisted and worsened compared to before. The patient has a history of hypertension for 9 years and a history of diabetes for over 4 years.",
            "Physical Examination":"Coarse breath sounds in both lungs, no dry or moist rales heard. Regular heartbeat with no pathological murmurs. Abdominal distention without tenderness or rebound tenderness. No clear kidney-area tenderness or percussion pain. Non-tender bilateral ureteral regions and no edema in both lower limbs.",
            "Auxiliary Examination":"(1)",
            "Imaging Examination":"Color Doppler ultrasound: 1. No obvious abnormalities in the liver, gallbladder, pancreas, spleen, and kidneys; 2. Approximately 80ml of urine in the bladder.\n(2)",
            "Laboratory Examination":"Complete Blood Count: 1. Lymphocyte percentage (LYMPH%) 14.4% \u2193; 2. Neutrophil percentage (NEUT%) 80.7% \u2191; 3. Absolute neutrophil count (NEUT#) 7.7*10^9\/L \u2191; 4. Red blood cells (RBC) 5.3*10^12\/L \u2191; 5. Hemoglobin (HGB) 173g\/L \u2191; 6. Hematocrit (HCT) 50.3% \u2191; 7. Platelet count (impedance method) (PLT-I) 447*10^9\/L \u2191; 8. Eosinophil percentage (EO%) 0.2% \u2193; 9. Absolute eosinophil count (EO#) 0.01*10^9\/L \u2193; 10. Plateletcrit (PCT) 0.40% \u2191.\nBlood Biochemistry: 1. Cholinesterase (dry) (CHE) 12503U\/L \u2191; 2. Albumin\/Globulin ratio (dry) (A\/G) 1.3 \u2193 1.5-2.5; 3. Alkaline phosphatase (dry) (ALP) 138U\/L \u2191; 4. \u03b3-glutamyl transpeptidase (dry) (GGT) 102U\/L \u2191; 5. Total cholesterol (dry) (TC) 5.60mmol\/L \u2191; 6. Chloride (dry) (CL) 96.0mmol\/L \u2193; 7. Amylase (dry) (AMY) 175U\/L \u2191; 8. Ammonia (dry) (AMON) 32.00\u03bcmol\/L \u2191; 9. Creatinine (Cr) 108\u03bcmol\/L \u2191; 10. Cystatin C (cys-c) 1.34mg\/L \u2191.\n(3)",
            "Pathological Examination":"None available."
        }
initial_potential_diseases =[
                        "Acute renal failure",
                        "Chronic renal insufficiency",
                        "Digestive system diseases"
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
print("the final result is",result)