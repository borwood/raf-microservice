# bottled_hcc
A flask server wrapping github.com/mimilabs/hccinfhir, a python lib for calculating patient risk adjustment according to the CMS HCC model. This server provides API endpoints for common functionalities and basically serves as a calculator microservice.

Flask-RESTPlus is used for input validation and documentation. The base URL will show the Swagger UI for easy view of routes and expected request schemas.

## Routes
### /calculate-raf   `POST`

This route is responsible for returning the risk score, as well as a breakdown of the contributing factors including HCC categories, interaction rules, count rules, and demographic factors.

#### Body

The body of the request should contain a patient's age, sex, and diagnosis codes.

````json
{
	"age": 1, // A non-negative number, 1 or greater
    "sex": "F", // Can be 'M', 1, 'F', or 2
    "diagnosis_codes": [ // A list of ICD-10-CM codes, with or without the decimal point
        "E119",
        "I19"
    ]
}
````

#### Response

*Currently the response is a JSONification of the unedited output of the hccinfhir.model_calculate.calculate_raf() method.* ***The response format will be updated when finer requirements are determined.***

```json
{
    "risk_score": 0.429,
    "risk_score_demographics": 0.238,
    "risk_score_chronic_only": 0.191,
    "risk_score_hcc": 0.191,
    "hcc_list": [
        "38"
    ],
    "cc_to_dx": {
        "38": [
            "E119"
        ]
    },
    "coefficients": {
        "F0_34": 0.238,
        "38": 0.191,
        "D1": 0.0
    },
    "interactions": {
        "OriginallyDisabled_Female": 0,
        "OriginallyDisabled_Male": 0,
        "LTI_Aged": 0,
        "LTI_NonAged": 0,
        "NMCAID_NORIGDIS_F0_34": 1,
        "MCAID_NORIGDIS_F0_34": 0,
        "NMCAID_ORIGDIS_F0_34": 0,
        "MCAID_ORIGDIS_F0_34": 0,
        "DIABETES_HF_V28": 0,
        "HF_CHR_LUNG_V28": 0,
        "HF_KIDNEY_V28": 0,
        "CHR_LUNG_CARD_RESP_FAIL_V28": 0,
        "gSubUseDisorder_gPsych_V28": 0,
        "DISABLED_CANCER_V28": 0,
        "DISABLED_NEURO_V28": 0,
        "DISABLED_HF_V28": 0,
        "DISABLED_CHR_LUNG_V28": 0,
        "DISABLED_ULCER_V28": 0,
        "D1": 1,
        "D2": 0,
        "D3": 0,
        "D4": 0,
        "D5": 0,
        "D6": 0,
        "D7": 0,
        "D8": 0,
        "D9": 0,
        "D10P": 0
    },
    "demographics": {
        "age": 1,
        "sex": "2",
        "dual_elgbl_cd": "NA",
        "orec": "0",
        "crec": "0",
        "new_enrollee": false,
        "snp": false,
        "version": "V2",
        "low_income": false,
        "graft_months": null,
        "category": "F0_34",
        "non_aged": true,
        "orig_disabled": false,
        "disabled": false,
        "esrd": false,
        "lti": false,
        "fbd": false,
        "pbd": false
    },
    "model_name": "CMS-HCC Model V28",
    "version": "V2",
    "diagnosis_codes": [
        "E119",
        "I10",
        ""
    ]
}
```



## Authentication

There is a simple authentication wrapper defined in *auth.py* which decorates the route in *main.py*. It anticipates a placeholder Bearer Token containing "your_secret_token". **It will be up to the users of this code to fully implement an authorization system fulfilling the security requirements of their application.**

#### Authorization Header

```http
Authorization: Bearer your_secret_token
```

