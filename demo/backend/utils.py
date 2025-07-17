from PyPDF2 import PdfReader
from graph import run_diagnosis
def get_final_diagnosis(case,differential_diagnosis):
    final_diagnosis,reasoning=run_diagnosis(case,differential_diagnosis)    
    # final_diagnosis="disease1"
    # reasoning="reason1,reason2,reason3"
    return final_diagnosis,reasoning

def info_extract(file_path):
    reader = PdfReader(file_path)
    words = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            for line in text.splitlines():
                word = line.strip()
                if word:
                    words.append(word)
    # Step 2: Include both short and long headings
    known_headings = {
        "Name":"name",
        "Age":"age",
        "Sex":"sex",
        "Chief Complaint":"chief_complaint",
        "Medical History":"previous_medical_history",
        "Physical Examination":"physical_examination",
        "Imaging Examination":"imageological_examination",
        "Laboratory Examination":"laboratory_examination",
        "Pathological Examination":"pathological_examination"
    }

    # Step 3: Go through words and build sections
    data = {}
    current_heading = None
    buffer = []

    i = 0
    while i < len(words):
        found_heading = None
        # Try 4 down to 1-word combinations
        for span in range(4, 0, -1):
            if i + span <= len(words):
                candidate = " ".join(words[i:i+span])
                if candidate in known_headings.keys():
                    found_heading = candidate
                    i += span
                    break

        if found_heading:
            if current_heading and buffer:
                data[current_heading] = " ".join(buffer).strip()
            current_heading = found_heading
            buffer = []
        else:
            if current_heading:
                buffer.append(words[i])
            i += 1

    # Capture last section
    if current_heading and buffer:
        data[current_heading] = " ".join(buffer).strip()

    # # Step 4: Display result
    # for heading, content in data.items():
    #     print(f"\n--- {heading} ---\n{content}\n")

    refined_data={}
    for key in data:
        refined_data[known_headings[key]]=data[key]

    # print(refined_data)
    return refined_data


# case = {"Patient basic information": "Elderly female, 88 years old.", 
#                            "Chief complaint": "Fatigue for 1 week, fever, chills, and dysuria for 3 days.", 
#                            "Medical history": "The patient started to experience general fatigue without any obvious cause a week ago, with poor appetite but no significant nausea, vomiting, abdominal pain, diarrhea, generalized bone and joint pain, chest tightness or asthma, and increased drowsiness. Symptoms such as urgency, frequency and dysuria were not present and were not given special attention; 3 days ago, the aforementioned symptoms worsened, accompanied by chills, fever with a maximum temperature of 38.7\u00b0C, general muscular soreness and discomfort with unclear descriptions, dysuria, particularly towards the end of urination, cloudy urine, without obvious urgency or frequency, discomfort in the lower back with unclear descriptions, no significant cough, sputum production, chest tightness, chest pain, or difficulty breathing, also not given special attention; 2 days ago, intravenous drip treatment with Levofloxacin was administered upon consultation, yet the fever recurred. Past medical history includes hypertension for 8 years.", 
#                            "Physical examination": "No eyelid swelling, lips were rosy, chest percussion on both lungs showed clear sound, clear breath sounds in both lungs without audible dry or wet rales, rhythmic heart rate without pathological murmurs. Both kidney areas showed no tenderness to pressure and mild tenderness to percussion, no apparent abnormalities in abdominal vascular pulsations, and no significant tenderness upon palpation of bilateral ureteral pressure points. No edema in the lower extremities.", 
#                            "Laboratory examination": {"routine_blood_test": "1 White Blood Cells WBC 8.1 *10^9/L 3.5-9.5; 2 Lymphocyte Percentage LYMPH% 12.5 \u2193 % 20.0-50.0; 3 Monocyte Percentage MONO% 7.9 % 3.0-10.0; 4 Neutrophil Percentage NEUT% 78.7 \u2191 % 40.0-75.0; 5 Lymphocyte Absolute Value LYMPH# 1.0 \u2193 *10^9/L 1.1-3.2; 6 Monocyte Absolute Value MONO# 0.64 \u2191 *10^9/L 0.10-0.60; 7 Neutrophil Absolute Value NEUT# 6.4 \u2191 *10^9/L 1.8-6.3; 8 Red Blood Cells RBC 4.4 *10^12/L 3.8-5.1; 9 Hemoglobin HGB 135 g/L 115-150; 10 Hematocrit HCT 40.1 % 35.0-45.0; 11 Mean Corpuscular Volume MCV 91 fL 82-100; 12 Mean Corpuscular Hemoglobin MCH 31 pg 27-34; 13 Mean Corpuscular Hemoglobin Concentration MCHC 337 g/L 316-354; 14 Red Cell Distribution Width (CV) RDW-CV 12.6 % <15.0; 15 Platelet Count (Impedance Method) PLT-I 228 *10^9/L 125-350; 16 Mean Platelet Volume MPV 10.5 \u2191 fL 8.0-10.0; 17 Platelet Distribution Width PDW 16.3 fL 9.0-17.0; 18 Eosinophil Percentage EO% 0.4 % 0.4-8.0; 19 Basophil Percentage BASO% 0.5 % 0.0-1.0; 20 Eosinophil Absolute Value EO# 0.03 *10^9/L 0.02-0.52; 21 Basophil Absolute Value BASO# 0.04 *10^9/L 0-0.06; 22 Plateletcrit PCT 0.24 % 0.17-0.35; 23 C-Reactive Protein CRP 68.74 \u2191 mg/L 0-4.00;", "blood_biochemistry_test": "1. Alanine Aminotransferase (ALT) 16 U/L 7-40; 2. Aspartate Aminotransferase (AST) 24 U/L 13-35; 3. Cholinesterase (CHE) 7066 U/L 5300-11300; 4. AST/ALT ratio 1.50; 5. Total Bile Acid (TBA) 2.6 \u03bcmol/L <12.0; 6. Total Protein (TP) 65.1 g/L 65.0-85.0; 7. Albumin (ALB) 38.7 \u2193 g/L 40.0-55.0; 8. Globulin (GLB) 26.4 g/L 20.0-40.0; 9. Albumin/Globulin Ratio (A/G) 1.5 1.2-2.4; 10. Total Bilirubin (TBIL) 44.3 \u2191 \u03bcmol/L <23.0; 11. Direct Bilirubin (DBIL) 7.5 \u2191 \u03bcmol/L <4.0; 12. Indirect Bilirubin (IBIL) 36.8 \u2191 \u03bcmol/L <19.0; 13. Alkaline Phosphatase (ALP) 99 U/L 40-150; 14. Lactate Dehydrogenase (LDH) 212 U/L 120-250; 15. Gamma-Glutamyl Transferase (GGT) 21 U/L 7-45; 16. Prealbumin (PA) 119.9 \u2193 mg/L 180.0-350.0; 17. Creatine Kinase (CK) 34 \u2193 U/L 40-200; 18. Creatine Kinase-MB Mass (CK-MBmass) 0.3 \u2193 ng/mL 0.6-6.3; 19. Alpha-Hydroxybutyrate Dehydrogenase (HBDH) 144 U/L 72-182; 20. Glucose (GLU) 4.91 mmol/L 3.90-6.10; 21. Urea 4.36 mmol/L 3.10-8.80; 22. Creatinine (Cr) 75 \u03bcmol/L 41-81; 23. Uric Acid (UA) 225 \u03bcmol/L 155-357; 24. Total Cholesterol 4.09 mmol/L <5.18; 25. Triglycerides (TG) 0.97 mmol/L <1.70; 26. High-Density Lipoprotein Cholesterol (HDL-C) 1.11 mmol/L >1.04; 27. Low-Density Lipoprotein Cholesterol (LDL-C) 2.86 mmol/L <3.37; 28. Apolipoprotein A1 (ApoA1) 1.20 g/L 1.05-2.05; 29. Apolipoprotein B (ApoB) 0.87 g/L 0.55-1.30; 30. ApoA1/ApoB Ratio 1.38 1.10-2.70; 31. Calcium (Ca) 2.31 mmol/L 2.11-2.52; 32. Phosphorus (P) 1.15 mmol/L 0.85-1.51; 33. Iron (Fe) 4.1 \u2193 \u03bcmol/L 7.8-32.2; 34. Magnesium (Mg) 0.79 mmol/L 0.75-1.02; 35. Potassium (K) 4.00 mmol/L 3.50-5.30; 36. Sodium (Na) 140 mmol/L 137-147; 37. Chloride (Cl) 103.0 mmol/L 99.0-110.0; 38. Bicarbonate (CO2) 22.4 mmol/L 21.0-31.0; 39. Anion Gap (AG) 14.6 mmol/L 8.0-16.0; 40. Adenosine Deaminase (ADA) 17.5 U/L 4.0-22.0; 41. Osmolality (OSM) 279 mOsm/kg 275-300; 42. Cystatin C (cys-c) 0.95 mg/L 0.60-1.30; 43. Hemolysis (HEM) -; 44. Jaundice (ICT) +; 45. Lipemia (LIP) -; 46. Interleukin-6 (IL-6) 16.70 \u2191 pg/mL <6.4; 47. Serum Amyloid A (SAA) 40.20 \u2191 mg/L <10; 48. Procalcitonin (PCT) 0.187 \u2191 ng/mL 0-0.046;", "routine_urine_test": "1 pH 5.5 4.5-8.0; 2 Color Pale Yellow Pale Yellow; 3 Transparency Clear Clear; 4 Specific Gravity SG 1.020 1.003-1.030; 5 Protein PRO Negative (-) Negative; 6 Glucose GLU Negative (-) Negative; 7 Ketone Bodies KET Weakly Positive Negative; 8 Bilirubin BIL Negative (-) Negative; 9 Urobilinogen UBG Normal Normal; 10 Nitrite NIT Negative (-) Negative; 11 Leukocyte Esterase LEU 2+ Negative; 12 Occult Blood BLD 1+ Negative; 13 Vitamin C VC Negative (-) Negative; 14 White Blood Cell Count WBC 226 \u2191 /\u03bcL 0-28; 15 Red Blood Cell Count RBC 44 \u2191 /\u03bcL 0-17; 16 Epithelial Cell Count EC 57 \u2191 /\u03bcL 2-10; 17 Cast Count CAST 19 \u2191 /\u03bcL 0-2; 18 Bacterial Count BACT 85 /\u03bcL 0-100; 19 Pathological Cast Path.CAST 3 \u2191 /\u03bcL 0-1; 20 Small Round Epithelial Cells SRC 43 /\u03bcL; 21 Yeast-Like Cells YLC 0 /\u03bcL; 22 Conductivity CONDCT 10 mS/cm 5-38; 23 Conductivity Information Cond.-Inf 2nd Level; 24 Red Blood Cell Information RBC-Inf Unclassified; 25 Crystal Examination X,TAL 0 /\u03bcL; 26 Mucus Filaments NYS 3 /\u03bcL; 27 White Blood Cells WBC 5-10 /HP 0-5; 28 Red Blood Cells RBC 0-1 /HP 0-5; 29 Epithelial Cells EC Negative Negative; 30 Transparent Cast Negative Negative; 31 Granular Cast Negative Negative; 32 Crystals X,TAL Negative Negative; 33 Other Other Negative; 34 Mucus Filaments Negative Negative; 35 Waxy Cast Negative Negative;"}, 
#                            "Imageological examination": {"color_doppler_ultrasound": "Kidneys: Both kidneys are normal in shape and size, with smooth and regular outlines. The corticomedullary junction is clear, and the parenchymal echo is evenly distributed. No separation was observed in the collecting system. No obvious dilation was observed in both ureters. Bladder: It is well-filled, with a smooth and continuous wall. No abnormal echo was observed in the cavity. After urination, about 6ml of residue remains in the bladder. CDFI: No abnormal blood flow signals were observed."},
#                            "Auxillary examination": "(1)", 
#                            "Pathological examination": "Not available."}
# differential_diagnosis =["Acute pyelonephritis", "Urinary system stones", "Urinary tract tumor", "Urinary tuberculosis"]

# _,_=get_final_diagnosis(case,differential_diagnosis)