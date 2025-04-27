# RAF-microservice

A flask server wrapping github.com/mimilabs/hccinfhir, a python package for calculating patient risk adjustment factors (RAF) according to the CMS HCC model V28. This server provides an API endpoint for posting de-identified patient information and returning a breakdown of the raf score with human-readable labels.

Flask-RESTPlus is used for input validation and documentation. The base URL will show the Swagger UI for easy view of routes and expected request schemas.
![image](https://github.com/user-attachments/assets/90790b99-97fc-4149-8a3d-d7db1cf5a4c1)

The code is extensively commented to allow for easy handoff.

## Routes

### /v1/calculate-raf-v28 `POST`

This route is responsible for returning the risk score, as well as a breakdown of the contributing factors including HCC categories, interaction rules (includes payable-HCC count rules), and demographic factors.

#### Body

The body of the request must contain a patient's age, sex, and list of diagnosis codes (even if it's empty).
```json
  "diagnosis_codes": ["E1121","E1122","I4820","I5021","N1831"], // A list of ICD-10-CM diagnosis codes, with or without the decimal point
  "age": 66, // An integer representing patient age
  "sex": "M", // "M", "1", "F", or "2" representing patient sex
```
There are optional parameters for passing additional context to the calculator. These can potentially have a high impact on the resulting risk score, but they are not always easily accessible information, so by default this API will make certain assumptions.
```json
  "dual_elgbl_cd": "02", // The Medicare-Medicaid dual-eligibilty code of the patient
  "orec": "0", // Code for the patient's original reason for eligibility
  "crec": "0", // Code for the patient's current reason for eligibility
  "new_enrollee": false, // Flag for whether the patient is a new enrollee in this calendar year
  "snp": false // Flag for whether the patient is in a Special Needs Program (SNP)
```
##### Further reading on CMS's standardized code systems used in the optional parameters
 - [Dual-Eligible Codes](https://www.cms.gov/medicare-medicaid-coordination/medicare-and-medicaid-coordination/medicare-medicaid-coordination-office/downloads/mmco_dualeligibledefinition.pdf)
 - [OREC Codes](https://resdac.org/cms-data/variables/medicare-original-reason-entitlement-code-orec)
 - [CREC Codes](https://resdac.org/cms-data/variables/medicare-current-reason-entitlement-code-crec)

#### Response

The response format has been tailored to show the overall risk score, the normalized risk score, and a breakdown of the various coefficients contributing to that score along with human-readable labels. This differs from the raw output of the HCCinFHIR package by providing a lean view of only the pertinent coefficients, and mapping them to labels that make their meaning evident in the response rather than relying on other areas of the application to do that interpretation.

```json
{
  "risk_score": 2.163,
  "risk_score_normalized": 2.07, // The normalized risk score determined by risk_score / 1.045
  "interactions": [ // A list of objects of each interaction applied, including the code, label, and coefficient
    {
      "code": "DIABETES_HF_V28",
      "label": "Diabetes with Heart Failure",
      "coefficient": 0.183
    },
    {
      "code": "HF_KIDNEY_V28",
      "label": "Heart Failure with Chronic Kidney Disease",
      "coefficient": 0.194
    },
    {
      "code": "HF_HCC238_V28",
      "label": "Heart Failure with HCC238",
      "coefficient": 0.14
    },
    {
      "code": "D4",
      "label": "Four payable HCCs",
      "coefficient": 0
    }
  ],
  "hcc": [ // A list of objects for each payable HCC, including the code, list of diagnoses, label, and coefficient
    {
      "code": "37",
      "dx": [
        "E1121",
        "E1122"
      ],
      "label": "Diabetes with Severe Acute Complications",
      "coefficient": 0.186
    },
    {
      "code": "225",
      "dx": [
        "I5021"
      ],
      "label": "Acute Heart Failure (Excludes Acute on Chronic)",
      "coefficient": 0.406
    },
    {
      "code": "329",
      "dx": [
        "N1831"
      ],
      "label": "Chronic Kidney Disease, Moderate (Stage 3, Except 3B)",
      "coefficient": 0.116
    },
    {
      "code": "238",
      "dx": [
        "I4820"
      ],
      "label": "Specified Heart Arrhythmias",
      "coefficient": 0.407
    }
  ],
  "demographics": [ // A list (for uniformity) containing one object with the demographic cohort code, label, and coefficient
    {
      "code": "M65_69",
      "label": "Male, Age 65-69",
      "coefficient": 0.531
    }
  ]
}
```

## Authentication

There is a simple authentication wrapper defined in _auth.py_ which decorates the route in _main.py_. If environment variable ENFORCE_AUTH == true, we anticipate a placeholder Bearer Token containing "your_secret_token". **It will be up to the users of this code to fully implement an authorization system fulfilling the security requirements of their application.**

#### Authorization Header

```http
Authorization: Bearer your_secret_token
```

## Note on HCCinFHIR

This project is based on the HCCinFHIR package from mimilabs, which is the successor to a deprecated HCC calculating repository at github.com/yubin-park/hccpy. HCCinFHIR is used under the Apache 2.0 license included in the repo. Currently RAF-microservice vendors a *very slightly modified* fork of HCCinFHIR to enable the Heart Failure * Specified Heart Arrhythmias interaction (adds one line of code in model_coefficients.py), but if that is patched in the official package, we will switch back to specifying it in requirements.txt.

The author of RAF-microservice makes no promise that 1) he will follow the changes made to the HCC CMS model throughout its annual cycle of proposition, commentary, and finalization; or 2) he will follow the changes made to the HCCinFHIR package and continue to integrate future versions into this repo. Furthermore, there is no guarantee that the HCCinFHIR repo will continue to be maintained by mimilabs, although this appears to be a safe assumption in the near to mid term. **Use at your own risk, with the assumption that you may have to fork and do your own upkeep as CMS releases regular updates to its standards.**
