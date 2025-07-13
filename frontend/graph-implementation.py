from dotenv import load_dotenv

load_dotenv()
import os
import re
from typing import List, Dict, TypedDict, Optional, Any
from collections import Counter

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END


class DoctorDiagnosis(TypedDict):
    doctor_id: str
    model_used: str
    provider: str
    chosen_disease: Optional[str]
    justification: Optional[str]
    error: Optional[str]

class GraphState(TypedDict):
    clinical_case_summary: Dict[str, str]
    initial_potential_diseases: List[str]
    diseases_to_consider: List[str]
    doctor_diagnoses_history: List[List[DoctorDiagnosis]]
    current_doctor_diagnoses: List[DoctorDiagnosis]
    resolved_diseases_for_next_round: List[str]
    final_diagnosis: Optional[str]
    final_justification: Optional[str]
    round_count: int
    max_rounds: int
    error_message: Optional[str]

DOCTOR_CONFIGS = [
    {
        "id": "Doctor-Alpha (GPT-4o-mini)",
        "provider": "openai",
        "model_name": "gpt-4o-mini"
    },
    {
        "id": "Doctor-Beta (GPT-4o)",
        "provider": "openai",
        "model_name": "gpt-4o"
    },
    # {
    #     "id": "Doctor-Gamma (Gemini-1.5-Flash)",
    #     "provider": "google_gemini",
    #     "model_name": "gemini-1.5-flash-latest" # Or other compatible Gemini models
    # },
    # {
    #     "id": "Doctor-Epsilon (Bedrock-Claude-3-Sonnet)",
    #     "provider": "aws_bedrock",
    #     "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    #     "region_name": "us-east-1"
    # },
    # Add more doctors here if needed
]


def parse_llm_diagnosis_output(text_output: str, doctor_id: str, provider: str) -> Dict[str, Optional[str]]:
    """
    Parses the LLM output to extract disease and justification.
    Returns a dictionary with 'chosen_disease', 'justification', and 'error'.
    """
    try:
        clean_output = text_output.strip().replace('\r\n', '\n').replace('\r', '\n')

        disease_match = re.search(r"^\s*Disease:\s*(.+?)(?:\n|$)", clean_output, re.IGNORECASE | re.MULTILINE)
        justification_match = re.search(r"^\s*Justification:\s*(.+)", clean_output, re.IGNORECASE | re.MULTILINE | re.DOTALL)

        chosen_disease = disease_match.group(1).strip() if disease_match else None
        justification = justification_match.group(1).strip() if justification_match else None
        
        if not justification and disease_match:
            remaining_text_after_disease = clean_output[disease_match.end():].strip()
            if remaining_text_after_disease.lower().startswith("justification:"):
                 justification = remaining_text_after_disease[len("justification:"):].strip()


        if not chosen_disease:
            # Log the problematic output for debugging
            print(f"Debug: Could not parse disease for {doctor_id} ({provider}). Raw output:\n---\n{text_output}\n---")
            error_msg = "Could not parse disease from LLM output."
            if not justification and "justification:" in clean_output.lower():
                 just_fallback_match = re.search(r"Justification:\s*(.+)", clean_output, re.IGNORECASE | re.DOTALL)
                 justification = just_fallback_match.group(1).strip() if just_fallback_match else "Justification present but could not be parsed cleanly."
            return {"chosen_disease": None, "justification": justification, "error": error_msg}

        return {"chosen_disease": chosen_disease, "justification": justification, "error": None}

    except Exception as e:
        print(f"Debug: Exception during parsing for {doctor_id} ({provider}). Raw output:\n---\n{text_output}\n--- Error: {str(e)}")
        return {"chosen_disease": None, "justification": None, "error": f"Parsing error: {str(e)}"}


def diagnose_with_doctors_node(state: GraphState) -> Dict[str, Any]:
    """
    Simulates multiple doctors diagnosing the case using various LLM providers.
    """
    print(f"\n--- Round {state['round_count'] + 1}: Doctors' Consultation ---")
    clinical_case_summary_str = "\n".join([f"{k}: {v}" for k, v in state["clinical_case_summary"].items()])
    diseases_to_consider = state["diseases_to_consider"]
    
    if not diseases_to_consider:
        print("No diseases to consider for this round. Skipping doctor consultations.")
        return {"current_doctor_diagnoses": [], "error_message": "No diseases left to consider."}

    current_round_diagnoses: List[DoctorDiagnosis] = []

    for doctor_config in DOCTOR_CONFIGS:
        doctor_id = doctor_config["id"]
        provider = doctor_config["provider"]
        model_name_or_id = doctor_config.get("model_name") or doctor_config.get("model_id") # Bedrock uses model_id
        
        print(f"Consulting {doctor_id} (Provider: {provider}, Model: {model_name_or_id})...")
        print(f"Diseases under consideration: {', '.join(diseases_to_consider)}")

        llm = None
        try:
            if provider == "openai":
                llm = ChatOpenAI(model=model_name_or_id, temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))
            elif provider == "google_gemini":
                llm = ChatGoogleGenerativeAI(model=model_name_or_id, temperature=0.3, convert_system_message_to_human=True)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

            prompt_template = f"""
You are a medical expert. Based on the following clinical case summary and the provided list of potential diseases,
please choose the SINGLE most likely disease from the list. Provide a brief justification for your choice.

Clinical Case Summary:
---
{clinical_case_summary_str}
---

Potential Diseases to choose from:
---
{', '.join(diseases_to_consider)}
---

Respond ONLY in the following format, with each part on a new line:
Disease: [Chosen Disease Name from the list]
Justification: [Your brief justification]

If you cannot make a definitive choice from the list or if the information is insufficient for one of these specific diseases,
you may state "Disease: Undetermined" and provide a justification.
However, strive to pick one from the provided list if possible.
Your chosen disease MUST be one of the diseases from the "Potential Diseases to choose from" list.
Do not add any preamble or explanation before "Disease:".
"""
            response = llm.invoke([HumanMessage(content=prompt_template)])
            parsed_data = parse_llm_diagnosis_output(response.content, doctor_id, provider)
            
            chosen_disease = parsed_data.get("chosen_disease")
            justification = parsed_data.get("justification")
            parsing_error = parsed_data.get("error")

            doctor_diagnosis_entry: DoctorDiagnosis = {
                "doctor_id": doctor_id,
                "model_used": model_name_or_id,
                "provider": provider,
                "chosen_disease": None, # Default to None
                "justification": justification,
                "error": parsing_error
            }

            if chosen_disease and chosen_disease != "Undetermined":
                if chosen_disease in diseases_to_consider:
                    doctor_diagnosis_entry["chosen_disease"] = chosen_disease
                else:
                    print(f"Warning: {doctor_id} chose '{chosen_disease}', which is not in the current list of considered diseases ({diseases_to_consider}). Treating as undetermined for this round.")
                    doctor_diagnosis_entry["chosen_disease"] = "Undetermined"
                    doctor_diagnosis_entry["justification"] = f"Chose '{chosen_disease}' (not in allowed list). Original justification: {justification}"
                    if doctor_diagnosis_entry["error"]:
                         doctor_diagnosis_entry["error"] += "; Chose disease not in list."
                    else:
                         doctor_diagnosis_entry["error"] = "Chose disease not in the provided list."
            elif chosen_disease == "Undetermined":
                 doctor_diagnosis_entry["chosen_disease"] = "Undetermined"

            if doctor_diagnosis_entry.get("error"):
                print(f"Error or parsing issue with {doctor_id}: {doctor_diagnosis_entry['error']}")
            elif doctor_diagnosis_entry.get("chosen_disease"):
                 print(f"{doctor_id} (Provider: {provider}) diagnosed: {doctor_diagnosis_entry['chosen_disease']}")
            current_round_diagnoses.append(doctor_diagnosis_entry)

        except Exception as e:
            print(f"Error during LLM call or setup for {doctor_id} (Provider: {provider}): {str(e)}")
            current_round_diagnoses.append({
                "doctor_id": doctor_id,
                "model_used": model_name_or_id,
                "provider": provider,
                "chosen_disease": None,
                "justification": None,
                "error": f"LLM call/setup failed: {str(e)}"
            })
            
    return {"current_doctor_diagnoses": current_round_diagnoses}


def conflict_resolution_node(state: GraphState) -> Dict[str, Any]:
    """
    Resolves conflicts among doctor diagnoses.
    If all agree, sets final_diagnosis.
    Otherwise, narrows down the list of potential diseases for the next round.
    """
    print("\n--- Conflict Resolution ---")
    current_diagnoses = state["current_doctor_diagnoses"]
    history = state.get("doctor_diagnoses_history", [])
    updated_history = history + [current_diagnoses]

    if not current_diagnoses:
        print("No diagnoses received in this round for conflict resolution.")
        return {
            "doctor_diagnoses_history": updated_history,
            "final_diagnosis": None,
            "resolved_diseases_for_next_round": state["diseases_to_consider"],
            "error_message": "No diagnoses to resolve."
        }

    valid_choices = [
        d["chosen_disease"] for d in current_diagnoses 
        if d["chosen_disease"] and d["chosen_disease"] != "Undetermined" and not d["error"]
    ]
    
    num_valid_choosing_doctors = len(valid_choices)

    if not valid_choices:
        print("No valid (non-Undetermined, no error) disease choices from doctors this round.")
        return {
            "doctor_diagnoses_history": updated_history,
            "final_diagnosis": None,
            "resolved_diseases_for_next_round": state["diseases_to_consider"], # No change
            "error_message": "No valid disease choices from doctors in this round."
        }

    if num_valid_choosing_doctors > 0 and len(set(valid_choices)) == 1:
        final_disease = valid_choices[0]
        final_just = next((d["justification"] for d in current_diagnoses if d["chosen_disease"] == final_disease), "Consensus reached.")
        print(f"Consensus reached among {num_valid_choosing_doctors} doctor(s): {final_disease}")
        return {
            "doctor_diagnoses_history": updated_history,
            "final_diagnosis": final_disease,
            "final_justification": final_just,
            "resolved_diseases_for_next_round": [final_disease]
        }
    else:
        disease_counts = Counter(valid_choices)
        next_round_diseases = list(disease_counts.keys())
        
        print(f"No consensus. Diagnoses: {dict(disease_counts)}")
        if not next_round_diseases:
            print("No specific diseases were positively identified by any doctor. Discussion might be stuck.")
            if len(state["diseases_to_consider"]) == 1:
                 return {
                    "doctor_diagnoses_history": updated_history,
                    "final_diagnosis": None,
                    "final_justification": "Stalemate: Doctors could not agree on or affirm the single remaining option.",
                    "resolved_diseases_for_next_round": [],
                    "error_message": "Stalemate on single option."
                }
            next_round_diseases = state["diseases_to_consider"]

        print(f"Diseases for next round: {', '.join(next_round_diseases)}")
        return {
            "doctor_diagnoses_history": updated_history,
            "final_diagnosis": None,
            "resolved_diseases_for_next_round": next_round_diseases
        }

def increment_round_counter_node(state: GraphState) -> Dict[str, Any]:
    """Increments the round counter and prepares diseases for the next round."""
    new_round_count = state["round_count"] + 1
    return {
        "round_count": new_round_count,
        "diseases_to_consider": state["resolved_diseases_for_next_round"] # This was set by conflict_resolution
    }


def should_continue_discussion_edge(state: GraphState) -> str:
    """Determines the next step based on the current state."""
    print("\n--- Evaluating Next Step ---")
    if state.get("error_message") and "Stalemate on single option" in state["error_message"]:
        print("Ending due to stalemate on a single option.")
        return "end_process_no_consensus"

    if state.get("final_diagnosis"):
        print(f"Final diagnosis reached: {state['final_diagnosis']}. Ending process.")
        return "end_process_consensus"

    if state["round_count"] >= state["max_rounds"]:
        print(f"Max rounds ({state['max_rounds']}) reached. Ending process.")
        return "end_process_max_rounds"

    if not state.get("diseases_to_consider"):
         print("No more diseases to consider. Ending process.")
         return "end_process_no_diseases_left"
    

    print("Continuing to next round of diagnosis.")
    return "continue_diagnosing"


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("doctor_diagnosis_round", diagnose_with_doctors_node)
    workflow.add_node("resolve_conflicts", conflict_resolution_node)
    workflow.add_node("increment_round", increment_round_counter_node)

    workflow.set_entry_point("doctor_diagnosis_round")

    workflow.add_edge("doctor_diagnosis_round", "resolve_conflicts")
    workflow.add_edge("resolve_conflicts", "increment_round")

    workflow.add_conditional_edges(
        "increment_round",
        should_continue_discussion_edge,
        {
            "continue_diagnosing": "doctor_diagnosis_round",
            "end_process_consensus": END,
            "end_process_max_rounds": END,
            "end_process_no_consensus": END,
            "end_process_no_diseases_left": END
        }
    )
    
    app = workflow.compile()
    return app

if __name__ == "__main__":

    clinical_case_input = {"Patient basic information": "Elderly female, 88 years old.", "Chief complaint": "Fatigue for 1 week, fever, chills, and dysuria for 3 days.", "Medical history": "The patient started to experience general fatigue without any obvious cause a week ago, with poor appetite but no significant nausea, vomiting, abdominal pain, diarrhea, generalized bone and joint pain, chest tightness or asthma, and increased drowsiness. Symptoms such as urgency, frequency and dysuria were not present and were not given special attention; 3 days ago, the aforementioned symptoms worsened, accompanied by chills, fever with a maximum temperature of 38.7\u00b0C, general muscular soreness and discomfort with unclear descriptions, dysuria, particularly towards the end of urination, cloudy urine, without obvious urgency or frequency, discomfort in the lower back with unclear descriptions, no significant cough, sputum production, chest tightness, chest pain, or difficulty breathing, also not given special attention; 2 days ago, intravenous drip treatment with Levofloxacin was administered upon consultation, yet the fever recurred. Past medical history includes hypertension for 8 years.", "Physical examination": "No eyelid swelling, lips were rosy, chest percussion on both lungs showed clear sound, clear breath sounds in both lungs without audible dry or wet rales, rhythmic heart rate without pathological murmurs. Both kidney areas showed no tenderness to pressure and mild tenderness to percussion, no apparent abnormalities in abdominal vascular pulsations, and no significant tenderness upon palpation of bilateral ureteral pressure points. No edema in the lower extremities.", "Laboratory examination": {"routine_blood_test": "1 White Blood Cells WBC 8.1 *10^9/L 3.5-9.5; 2 Lymphocyte Percentage LYMPH% 12.5 \u2193 % 20.0-50.0; 3 Monocyte Percentage MONO% 7.9 % 3.0-10.0; 4 Neutrophil Percentage NEUT% 78.7 \u2191 % 40.0-75.0; 5 Lymphocyte Absolute Value LYMPH# 1.0 \u2193 *10^9/L 1.1-3.2; 6 Monocyte Absolute Value MONO# 0.64 \u2191 *10^9/L 0.10-0.60; 7 Neutrophil Absolute Value NEUT# 6.4 \u2191 *10^9/L 1.8-6.3; 8 Red Blood Cells RBC 4.4 *10^12/L 3.8-5.1; 9 Hemoglobin HGB 135 g/L 115-150; 10 Hematocrit HCT 40.1 % 35.0-45.0; 11 Mean Corpuscular Volume MCV 91 fL 82-100; 12 Mean Corpuscular Hemoglobin MCH 31 pg 27-34; 13 Mean Corpuscular Hemoglobin Concentration MCHC 337 g/L 316-354; 14 Red Cell Distribution Width (CV) RDW-CV 12.6 % <15.0; 15 Platelet Count (Impedance Method) PLT-I 228 *10^9/L 125-350; 16 Mean Platelet Volume MPV 10.5 \u2191 fL 8.0-10.0; 17 Platelet Distribution Width PDW 16.3 fL 9.0-17.0; 18 Eosinophil Percentage EO% 0.4 % 0.4-8.0; 19 Basophil Percentage BASO% 0.5 % 0.0-1.0; 20 Eosinophil Absolute Value EO# 0.03 *10^9/L 0.02-0.52; 21 Basophil Absolute Value BASO# 0.04 *10^9/L 0-0.06; 22 Plateletcrit PCT 0.24 % 0.17-0.35; 23 C-Reactive Protein CRP 68.74 \u2191 mg/L 0-4.00;", "blood_biochemistry_test": "1. Alanine Aminotransferase (ALT) 16 U/L 7-40; 2. Aspartate Aminotransferase (AST) 24 U/L 13-35; 3. Cholinesterase (CHE) 7066 U/L 5300-11300; 4. AST/ALT ratio 1.50; 5. Total Bile Acid (TBA) 2.6 \u03bcmol/L <12.0; 6. Total Protein (TP) 65.1 g/L 65.0-85.0; 7. Albumin (ALB) 38.7 \u2193 g/L 40.0-55.0; 8. Globulin (GLB) 26.4 g/L 20.0-40.0; 9. Albumin/Globulin Ratio (A/G) 1.5 1.2-2.4; 10. Total Bilirubin (TBIL) 44.3 \u2191 \u03bcmol/L <23.0; 11. Direct Bilirubin (DBIL) 7.5 \u2191 \u03bcmol/L <4.0; 12. Indirect Bilirubin (IBIL) 36.8 \u2191 \u03bcmol/L <19.0; 13. Alkaline Phosphatase (ALP) 99 U/L 40-150; 14. Lactate Dehydrogenase (LDH) 212 U/L 120-250; 15. Gamma-Glutamyl Transferase (GGT) 21 U/L 7-45; 16. Prealbumin (PA) 119.9 \u2193 mg/L 180.0-350.0; 17. Creatine Kinase (CK) 34 \u2193 U/L 40-200; 18. Creatine Kinase-MB Mass (CK-MBmass) 0.3 \u2193 ng/mL 0.6-6.3; 19. Alpha-Hydroxybutyrate Dehydrogenase (HBDH) 144 U/L 72-182; 20. Glucose (GLU) 4.91 mmol/L 3.90-6.10; 21. Urea 4.36 mmol/L 3.10-8.80; 22. Creatinine (Cr) 75 \u03bcmol/L 41-81; 23. Uric Acid (UA) 225 \u03bcmol/L 155-357; 24. Total Cholesterol 4.09 mmol/L <5.18; 25. Triglycerides (TG) 0.97 mmol/L <1.70; 26. High-Density Lipoprotein Cholesterol (HDL-C) 1.11 mmol/L >1.04; 27. Low-Density Lipoprotein Cholesterol (LDL-C) 2.86 mmol/L <3.37; 28. Apolipoprotein A1 (ApoA1) 1.20 g/L 1.05-2.05; 29. Apolipoprotein B (ApoB) 0.87 g/L 0.55-1.30; 30. ApoA1/ApoB Ratio 1.38 1.10-2.70; 31. Calcium (Ca) 2.31 mmol/L 2.11-2.52; 32. Phosphorus (P) 1.15 mmol/L 0.85-1.51; 33. Iron (Fe) 4.1 \u2193 \u03bcmol/L 7.8-32.2; 34. Magnesium (Mg) 0.79 mmol/L 0.75-1.02; 35. Potassium (K) 4.00 mmol/L 3.50-5.30; 36. Sodium (Na) 140 mmol/L 137-147; 37. Chloride (Cl) 103.0 mmol/L 99.0-110.0; 38. Bicarbonate (CO2) 22.4 mmol/L 21.0-31.0; 39. Anion Gap (AG) 14.6 mmol/L 8.0-16.0; 40. Adenosine Deaminase (ADA) 17.5 U/L 4.0-22.0; 41. Osmolality (OSM) 279 mOsm/kg 275-300; 42. Cystatin C (cys-c) 0.95 mg/L 0.60-1.30; 43. Hemolysis (HEM) -; 44. Jaundice (ICT) +; 45. Lipemia (LIP) -; 46. Interleukin-6 (IL-6) 16.70 \u2191 pg/mL <6.4; 47. Serum Amyloid A (SAA) 40.20 \u2191 mg/L <10; 48. Procalcitonin (PCT) 0.187 \u2191 ng/mL 0-0.046;", "routine_urine_test": "1 pH 5.5 4.5-8.0; 2 Color Pale Yellow Pale Yellow; 3 Transparency Clear Clear; 4 Specific Gravity SG 1.020 1.003-1.030; 5 Protein PRO Negative (-) Negative; 6 Glucose GLU Negative (-) Negative; 7 Ketone Bodies KET Weakly Positive Negative; 8 Bilirubin BIL Negative (-) Negative; 9 Urobilinogen UBG Normal Normal; 10 Nitrite NIT Negative (-) Negative; 11 Leukocyte Esterase LEU 2+ Negative; 12 Occult Blood BLD 1+ Negative; 13 Vitamin C VC Negative (-) Negative; 14 White Blood Cell Count WBC 226 \u2191 /\u03bcL 0-28; 15 Red Blood Cell Count RBC 44 \u2191 /\u03bcL 0-17; 16 Epithelial Cell Count EC 57 \u2191 /\u03bcL 2-10; 17 Cast Count CAST 19 \u2191 /\u03bcL 0-2; 18 Bacterial Count BACT 85 /\u03bcL 0-100; 19 Pathological Cast Path.CAST 3 \u2191 /\u03bcL 0-1; 20 Small Round Epithelial Cells SRC 43 /\u03bcL; 21 Yeast-Like Cells YLC 0 /\u03bcL; 22 Conductivity CONDCT 10 mS/cm 5-38; 23 Conductivity Information Cond.-Inf 2nd Level; 24 Red Blood Cell Information RBC-Inf Unclassified; 25 Crystal Examination X,TAL 0 /\u03bcL; 26 Mucus Filaments NYS 3 /\u03bcL; 27 White Blood Cells WBC 5-10 /HP 0-5; 28 Red Blood Cells RBC 0-1 /HP 0-5; 29 Epithelial Cells EC Negative Negative; 30 Transparent Cast Negative Negative; 31 Granular Cast Negative Negative; 32 Crystals X,TAL Negative Negative; 33 Other Other Negative; 34 Mucus Filaments Negative Negative; 35 Waxy Cast Negative Negative;"}, "Imageological examination": {"color_doppler_ultrasound": "Kidneys: Both kidneys are normal in shape and size, with smooth and regular outlines. The corticomedullary junction is clear, and the parenchymal echo is evenly distributed. No separation was observed in the collecting system. No obvious dilation was observed in both ureters. Bladder: It is well-filled, with a smooth and continuous wall. No abnormal echo was observed in the cavity. After urination, about 6ml of residue remains in the bladder. CDFI: No abnormal blood flow signals were observed."}, "Auxillary examination": "(1)", "Pathological examination": "Not available."}
    initial_potential_diseases_input =["Acute pyelonephritis", "Urinary system stones", "Urinary tract tumor", "Urinary tuberculosis"]
    # clinical_case_input ={
    #         "Patient Basic Information":"Elderly female, 59 years old.",
    #         "Chief Complaint":"Poor appetite, nausea accompanied by oliguria for over a month.",
    #         "Medical History":"One month ago, the patient developed poor appetite, nausea, and oliguria (specific urine volume unknown) without any obvious cause. This was accompanied by occasional dizziness. Symptoms did not alleviate and remained untreated. The patient later reported that the aforementioned symptoms persisted and worsened compared to before. The patient has a history of hypertension for 9 years and a history of diabetes for over 4 years.",
    #         "Physical Examination":"Coarse breath sounds in both lungs, no dry or moist rales heard. Regular heartbeat with no pathological murmurs. Abdominal distention without tenderness or rebound tenderness. No clear kidney-area tenderness or percussion pain. Non-tender bilateral ureteral regions and no edema in both lower limbs.",
    #         "Auxiliary Examination":"(1)",
    #         "Imaging Examination":"Color Doppler ultrasound: 1. No obvious abnormalities in the liver, gallbladder, pancreas, spleen, and kidneys; 2. Approximately 80ml of urine in the bladder.\n(2)",
    #         "Laboratory Examination":"Complete Blood Count: 1. Lymphocyte percentage (LYMPH%) 14.4% \u2193; 2. Neutrophil percentage (NEUT%) 80.7% \u2191; 3. Absolute neutrophil count (NEUT#) 7.7*10^9\/L \u2191; 4. Red blood cells (RBC) 5.3*10^12\/L \u2191; 5. Hemoglobin (HGB) 173g\/L \u2191; 6. Hematocrit (HCT) 50.3% \u2191; 7. Platelet count (impedance method) (PLT-I) 447*10^9\/L \u2191; 8. Eosinophil percentage (EO%) 0.2% \u2193; 9. Absolute eosinophil count (EO#) 0.01*10^9\/L \u2193; 10. Plateletcrit (PCT) 0.40% \u2191.\nBlood Biochemistry: 1. Cholinesterase (dry) (CHE) 12503U\/L \u2191; 2. Albumin\/Globulin ratio (dry) (A\/G) 1.3 \u2193 1.5-2.5; 3. Alkaline phosphatase (dry) (ALP) 138U\/L \u2191; 4. \u03b3-glutamyl transpeptidase (dry) (GGT) 102U\/L \u2191; 5. Total cholesterol (dry) (TC) 5.60mmol\/L \u2191; 6. Chloride (dry) (CL) 96.0mmol\/L \u2193; 7. Amylase (dry) (AMY) 175U\/L \u2191; 8. Ammonia (dry) (AMON) 32.00\u03bcmol\/L \u2191; 9. Creatinine (Cr) 108\u03bcmol\/L \u2191; 10. Cystatin C (cys-c) 1.34mg\/L \u2191.\n(3)",
    #         "Pathological Examination":"None available."
    #     }
    # initial_potential_diseases_input =[
    #                     "Acute renal failure",
    #                     "Chronic renal insufficiency",
    #                     "Digestive system diseases"
    #                 ]

    initial_state: GraphState = {
        "clinical_case_summary": clinical_case_input,
        "initial_potential_diseases": initial_potential_diseases_input,
        "diseases_to_consider": initial_potential_diseases_input,
        "doctor_diagnoses_history": [],
        "current_doctor_diagnoses": [],
        "resolved_diseases_for_next_round": [], # Will be populated by conflict_resolution
        "final_diagnosis": None,
        "final_justification": None,
        "round_count": 0,
        "max_rounds": 3,
        "error_message": None
    }

    diagnostic_graph = build_graph()
    config = {"recursion_limit": 15}

    print("Starting Clinical Diagnosis Process...")
    print("Ensure you have installed necessary packages: langchain-openai, langchain-google-genai, langchain-aws, boto3")
    
    final_state = diagnostic_graph.invoke(initial_state, config=config)

    print("\n\n--- Final Diagnosis Outcome ---")
    if final_state.get("final_diagnosis"):
        print(f"Final Agreed Diagnosis: {final_state['final_diagnosis']}")
        print(f"Justification: {final_state['final_justification']}")
    elif final_state["round_count"] >= final_state["max_rounds"]:
        print("Max rounds reached. No consensus achieved.")
        print(f"Diseases last considered after {final_state['max_rounds']} rounds: {', '.join(final_state.get('diseases_to_consider', ['None']))}")
    elif final_state.get("error_message"):
         print(f"Process ended due to an error or specific condition: {final_state['error_message']}")
         print(f"Diseases last considered: {', '.join(final_state.get('diseases_to_consider', ['None']))}")
    else:
        print("Process ended without a conclusive diagnosis and not due to max rounds or a specific error message.")
        print(f"Diseases last considered: {', '.join(final_state.get('diseases_to_consider', ['None']))}")

    print(f"\nTotal rounds of discussion: {final_state['round_count']}")
    print("\n--- Full Diagnostic History ---")
    for i, round_data in enumerate(final_state.get("doctor_diagnoses_history", [])):
        print(f"Round {i + 1} Diagnoses:")
        if not round_data:
            print("  No diagnoses recorded for this round.")
            continue
        for diagnosis in round_data:
            chosen = diagnosis.get('chosen_disease', 'N/A')
            just = diagnosis.get('justification', 'N/A')
            err = diagnosis.get('error')
            prov = diagnosis.get('provider', 'N/A')
            mod_used = diagnosis.get('model_used', 'N/A')
            print(f"  - {diagnosis['doctor_id']} (Provider: {prov}, Model: {mod_used}):")
            print(f"    Chosen: {chosen}")
            print(f"    Justification: {just}")
            if err:
                print(f"    Error: {err}")

