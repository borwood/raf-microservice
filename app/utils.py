from pydantic import BaseModel
from vendor.hccinfhir.model_calculate import calculate_raf

# This file contains utilities for cleaning up the output of calculate_raf() so it can be returned as a useful JSON response.

NORM_FACTOR = 1.045  # This is the 2025 normalization factor for the CMS-HCC V28 model. It is defined yearly, and compensates for increase in dx capture over time, making 2025 scores comparable to 2024 and earlier.

# This is a map of all of the possible coefficient keys that can be returned from the calculate_raf() function for CMS HCC V28.
# It is used to map the keys to human readable labels for the API response.
coefficient_labels = {
    "interactions": {
        "DIABETES_HF_V28": "Diabetes with Heart Failure",
        "HF_CHR_LUNG_V28": "Heart Failure with Chronic Lung Disease",
        "HF_KIDNEY_V28": "Heart Failure with Chronic Kidney Disease",
        "CHR_LUNG_CARD_RESP_FAIL_V28": "Chronic Lung Disease with Cardiac or Respiratory Failure",
        "HF_HCC238_V28": "Heart Failure with HCC238",  # THIS IS NOT ENABLED IN HCCINFHIR YET - PR made - Currently vendoring custom fork with fix
        "gSubUseDisorder_gPsych_V28": "Substance Use Disorder with Psychosis",
        "D1": "One payable HCC",
        "D2": "Two payable HCCs",
        "D3": "Three payable HCCs",
        "D4": "Four payable HCCs",
        "D5": "Five payable HCCs",
        "D6": "Six payable HCCs",
        "D7": "Seven payable HCCs",
        "D8": "Eight payable HCCs",
        "D9": "Nine payable HCCs",
        "D10P": "Ten or more payable HCCs",
        "OriginallyDisabled_Male": "Originally Disabled Male",
        "OriginallyDisabled_Female": "Originally Disabled Female",
    },
    "hcc": {
        "1": "HIV/AIDS",
        "2": "Septicemia, Systemic Inflammatory Response Syndrome/Shock",
        "6": "Opportunistic Infections",
        "17": "Cancer Metastatic to Lung, Liver, Brain, and Other Organs; Acute Myeloid Leukemia Except Promyelocytic",
        "18": "Cancer Metastatic to Bone; Other and Unspecified Metastatic Cancer; Acute Leukemia Except Myeloid",
        "19": "Myelodysplastic Syndromes, Multiple Myeoma, and Other Cancers",
        "20": "Lung and Other Severe Cancers",
        "21": "Lymphoma and Other Cancers",
        "22": "Bladder, Colorectal, and Other Cancers",
        "23": "Prostate, Breasts, and Other Cancers",
        "35": "Pancrase Transplant Status",
        "37": "Diabetes with Severe Acute Complications",
        "38": "Diabetes with Glycemic, Unspecified, or No Complications",
        "48": "Morbid Obesity",
        "49": "Specified Lysosoml Storage Disease",
        "50": "Amyloidosis, Porpgyria, and Other Specified Metabolic Disorders",
        "51": "Addison's and Cushing's Diseases, Acromegaly, and Other Specified Endocrine Disorders",
        "62": "Liver Transplant Status/Complications",
        "63": "Chronic Liver Failure/End-Stage Liver Disorders",
        "64": "Cirrhosis of Liver",
        "65": "Chronic Hepatitis",
        "68": "Cholangitis and Obstruction of Bile Duct Without Gallstones",
        "77": "Intestine Trasplant Status/Complications",
        "78": "Intestinal Obstruction/Perforation",
        "79": "Chronic Pancreatitis",
        "80": "Crohn's Disease (Regional Enterititis)",
        "81": "Ulcerative Colitis",
        "92": "Bone/Joint/Muscle/Severe Soft Tissue Infections/Necrosis",
        "93": "Rheumatoid Arthritis and Other Specified Inflammatory Rheumatic Disorders",
        "94": "Systemic Lupus Erythematosus and Other Specified Systemic Connective Tissue Disorders",
        "107": "Sickle Cell Anemia (Hb-SS) and Thalassemia Beta Zero",
        "108": "Sickle Cell Anemia (Hb-SS) and Thalassemia Beta Zero; Beta Thalassemia Major",
        "109": "Acquired HemolyƟc, Aplastic, and Sideroblastic Anemias",
        "111": "Hemophilia, Male",
        "112": "Immune Thrombocytopenia and Specified Coagulation Defects and Hemorrhagic Conditions",
        "114": "Common Variable and Combined Immunodeficiencies",
        "115": "Specified Immunodeficiencies and White Blood cell Disorders",
        "125": "Dementia, Severe",
        "126": "Dementia, Moderate",
        "127": "Dementia, Mild or Unspecified",
        "135": "Drug Use with Psychotic Complications",
        "136": "Alcohol Use with Psychotic Complications",
        "137": "Drug Use Disorder, Moderate/Severe, or Drug Use with Non-Psychotic Complications",
        "138": "Drug Use Disorder, Mild, Uncomplicated, Except Cannabis",
        "139": "Alcohol Use Disorder, Moderate/Severe, or Alcohol Use with Specified Nonpsychotic Complication",
        "151": "Schizophrenia",
        "152": "Psychosis, Except Schizophrenia",
        "153": "Personality Disorders; Anorexia/Bulimia Nervosa",
        "154": "Bipolar Disorders without Psychosis",
        "155": "Major Depression, Moderate or Severe, without Psychosis",
        "180": "Quadriplegia",
        "181": "Paraplegia",
        "182": "Spinal Cord Disorders/Injuries",
        "190": "Amyotrophic Lateral Sclerosis and Other Motor Neuron Disease, Spinal Muscular Atrophy",
        "191": "Quadriplegic Cerebral Palsy",
        "192": "Cerebral Palsy, Except Quadriplegic",
        "193": "Chronic Inflammatory Demyelinating Polyneuritis and Multifocal Motor Neuropathy",
        "195": "Myasthenia Gravis with (Acute) Exacerbation",
        "196": "Myasthenia Gravis without (Acute) Exacerbation and Other Myoneural Disorders",
        "197": "Muscular Dystrophy",
        "198": "Multiple Sclerosis",
        "199": "Parkinson and Other Degenerative Disease of Basal Ganglia",
        "200": "Friedreich and Other Hereditary Ataxias; Huntington Disease",
        "201": "Seizure Disorders and Convulsions",
        "202": "Coma, Brain Compression/Anoxic Damage",
        "211": "Respirator Dependence/Tracheostomy Status/Complications",
        "212": "Respiratory Arrest",
        "213": "Cardio-Respiratory Failure and Shock",
        "221": "Heart Transplant Status/Complications",
        "222": "End-Stage Heart Failure",
        "223": "Heart Failure with Heart Assist Device/Artificial Heart",
        "224": "Acute on Chronic Heart Failure",
        "225": "Acute Heart Failure (Excludes Acute on Chronic)",
        "226": "Heart Failure, Except Endstage and Acute",
        "227": "Cardiomyopathy/Myocarditis",
        "228": "Acute Myocardial Infarction",
        "229": "Unstable Angina and Other Acute Ischemic Heart Disease",
        "238": "Specified Heart Arrhythmias",
        "248": "Intracranial Hemorrhage",
        "249": "Ischemic or Unspecified Stroke",
        "253": "Hemiplegia/Hemiparesis",
        "254": "Monoplegia, Other Paralytic Syndromes",
        "263": "Atherosclerosis of Arteries of the Extremities with Ulceration or Gangrene",
        "264": "Vascular Disease with Complications",
        "267": "Deep Vein Thrombosis and Pulmonary Embolism",
        "276": "Lung Transplant Status/Complications",
        "277": "Cystic Fibrosis",
        "278": "Idiopathic Pulmonary Fibrosis and Lung Involvement in Systemic Sclerosis",
        "279": "Severe Persistent Asthma",
        "280": "Chronic Obstructive Pulmonary Disease, Interstitial Lung Disorders, and Other Chronic Lung Disorders",
        "282": "Aspiration and Specified Bacterial Pneumonias",
        "283": "Empyema, Lung Abscess",
        "298": "Severe Diabetic Eye Disease, Retinal Vein Occlusion, and Vitreous Hemorrhage",
        "300": "Exudative Macular Degeneration",
        "326": "Chronic Kidney Disease, Stage 5",
        "327": "Chronic Kidney Disease, Severe (Stage 4)",
        "328": "Chronic Kidney Disease, Moderate (Stage 3B)",
        "329": "Chronic Kidney Disease, Moderate (Stage 3, Except 3B)",
        "379": "Pressure Ulcer of Skin with Necrosis Through to Muscle, Tendon, or Bone",
        "380": "Chronic Ulcer of Skin, Except Pressure, Through to Bone or Muscle",
        "381": "Pressure Ulcer of Skin with Full Thickness Skin Loss",
        "382": "Pressure Ulcer of Skin with Partial Thickness Skin Loss",
        "383": "Chronic Ulcer of Skin, Except Pressure, Not Specified as Through to Bone or Muscle",
        "385": "Severe Skin Burn",
        "387": "Pemphigus, Pemphigoid, and Other Specified Autoimmune Skin Disorders",
        "397": "Major Head Injury with Loss of Consciousness > 1 Hour",
        "398": "Major Head Injury with Loss of Consciousness < 1 Hour or Unspecified",
        "399": "Major Head Injury without Loss of Consciousness",
        "401": "Vertebral Fractures without Spinal Cord Injury",
        "402": "Hip Fracture/Dislocation",
        "405": "Traumatic Amputations and Complications",
        "409": "Amputation Status, Lower Limb/Amputation Complications",
        "454": "Stem Cell, Including Bone Marrow, Transplant Status/Complications",
        "463": "Artificial Openings for Feeding or Elimination",
    },
    "demographics": {
        "F0_34": "Female, Age 0-34",
        "F35_44": "Female, Age 35-44",
        "F45_54": "Female, Age 45-54",
        "F55_59": "Female, Age 55-59",
        "F60_64": "Female, Age 60-64",
        "F65_69": "Female, Age 65-69",
        "F70_74": "Female, Age 70-74",
        "F75_79": "Female, Age 75-79",
        "F80_84": "Female, Age 80-84",
        "F85_89": "Female, Age 85-89",
        "F90_94": "Female, Age 90-94",
        "F95_GT": "Female, Age 95+",
        "M0_34": "Male, Age 0-34",
        "M35_44": "Male, Age 35-44",
        "M45_54": "Male, Age 45-54",
        "M55_59": "Male, Age 55-59",
        "M60_64": "Male, Age 60-64",
        "M65_69": "Male, Age 65-69",
        "M70_74": "Male, Age 70-74",
        "M75_79": "Male, Age 75-79",
        "M80_84": "Male, Age 80-84",
        "M85_89": "Male, Age 85-89",
        "M90_94": "Male, Age 90-94",
        "M95_GT": "Male, Age 95+",
    },
}


def sanitize_for_JSON(d: dict) -> dict:
    """Utility function: Recursively convert dict values to JSON-serializable formats."""
    if issubclass(type(d), dict):
        return {
            k: sanitize_for_JSON(v) for k, v in d.items()
        }  # Recursively clean dicts
    elif isinstance(d, BaseModel):
        return {
            k: sanitize_for_JSON(v) for k, v in d.model_dump().items()
        }  # Convert Pydantic model to dict
    elif issubclass(type(d), set):
        return list(d)
    else:
        return d


def make_coefficient_breakdown(
    interactions: dict, coefficients: dict, hcc_list: list, cc_to_dx: dict
) -> dict:
    """Utility function: Make dict of coefficients separated by type, with human readable labels."""
    coefficient_breakdown = {"interactions": [], "hcc": [], "demographics": []}
    key_list = []
    # For each interaction that is flagged as present (1), add it to the coefficient breakdown dict
    for key, value in interactions.items():
        if value == 1:
            if key in coefficients:
                coefficient_breakdown["interactions"].append(
                    {
                        "code": key,
                        "label": coefficient_labels["interactions"].get(
                            key, "Unidentified Interaction"
                        ),
                        "coefficient": coefficients[key],
                    }
                )
                key_list.append(key)
    # Now do the same for HCCs
    for hcc in hcc_list:
        if hcc in coefficients:
            coefficient_breakdown["hcc"].append(
                {
                    "code": hcc,
                    "dx": cc_to_dx.get(hcc, "Unidentified Diagnosis Code"),
                    "label": coefficient_labels["hcc"].get(hcc, "Unidentified HCC"),
                    "coefficient": coefficients[hcc],
                }
            )
            key_list.append(hcc)
    # Now remove the hcc and interactions keys from the coefficients dict that are in the key_list, leaving only demographics
    # This is because the coefficients dict contains all coefficients, including demographics, interactions, and HCCs
    for key in key_list:
        if key in coefficients:
            del coefficients[key]
    # Now add the demographics coefficients to the coefficient breakdown dict
    for key in coefficients.keys():
        coefficient_breakdown["demographics"].append(
            {
                "code": key,
                "label": coefficient_labels["demographics"].get(
                    key, "Unidentified Demographic"
                ),
                "coefficient": coefficients[key],
            }
            )

    return coefficient_breakdown


def format_response(raf_response: dict) -> dict:
    """Utility function: Strip out unnecessary fields from the calculate_raf() output, and insert the coefficient breakdown."""
    raf_response = sanitize_for_JSON(raf_response)
    return {
        "risk_score": round(raf_response["risk_score"], 3),
        "risk_score_normalized": round(raf_response["risk_score"] / NORM_FACTOR, 3),
        **make_coefficient_breakdown(
            interactions=raf_response["interactions"],
            coefficients=raf_response["coefficients"],
            hcc_list=raf_response["hcc_list"],
            cc_to_dx=raf_response["cc_to_dx"],
        ),
    }


def get_v28_response(
    diagnosis_codes: list,
    age: int,
    sex: str,
    dual_elgbl_cd: str = None,
    orec: str = None,
    crec: str = None,
    new_enrollee: bool = False,
    snp: bool = False,
) -> dict:
    """Get the V28 RAF response from calculate_raf() and apply formatting."""
    raw_response = calculate_raf(
        diagnosis_codes=diagnosis_codes,
        model_name="CMS-HCC Model V28",
        age=age,
        sex=sex,
        dual_elgbl_cd=dual_elgbl_cd,
        orec=orec,
        crec=crec,
        new_enrollee=new_enrollee,
        snp=snp,
    )
    return format_response(raw_response)
