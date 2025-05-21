# RAF-microservice

A Flask server wrapping [`hccinfhir`](https://github.com/mimilabs/hccinfhir), a Python package for calculating patient risk adjustment factors (RAF) according to the CMS HCC model V28. This server provides an API endpoint for posting de-identified patient information and returning a breakdown of the RAF score with human-readable labels.

Flask-RESTX is used for input validation and documentation. The base URL will show the Swagger UI for easy view of routes and expected request schemas.

The code is extensively commented to allow for easy handoff.

---

## Routes

### `POST /v1/raf-v28/multi`

Calculates RAF from a list of diagnosis codes and demographic factors.

#### Request Body

```json
{
  "diagnosis_codes": ["E1121", "E1122", "I4820", "I5021", "N1831"],
  "age": 66,
  "sex": "M",
  "dual_elgbl_cd": "02",
  "orec": "0",
  "crec": "0",
  "new_enrollee": false,
  "snp": false
}
```

#### Response

```json
{
  "risk_score": 2.163,
  "risk_score_normalized": 2.07,
  "interactions": [
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
  "hcc": [
    {
      "code": "37",
      "dx": ["E1121", "E1122"],
      "label": "Diabetes with Severe Acute Complications",
      "coefficient": 0.186
    },
    {
      "code": "225",
      "dx": ["I5021"],
      "label": "Acute Heart Failure (Excludes Acute on Chronic)",
      "coefficient": 0.406
    },
    {
      "code": "329",
      "dx": ["N1831"],
      "label": "Chronic Kidney Disease, Moderate (Stage 3, Except 3B)",
      "coefficient": 0.116
    },
    {
      "code": "238",
      "dx": ["I4820"],
      "label": "Specified Heart Arrhythmias",
      "coefficient": 0.407
    }
  ],
  "demographics": [
    {
      "code": "M65_69",
      "label": "Male, Age 65-69",
      "coefficient": 0.531
    }
  ]
}
```

---

### `POST /v1/raf-v28/single`

Calculates the RAF impact of a single diagnosis code.

#### Request Body

```json
{
  "diagnosis_code": "I10",
  "age": 72,
  "sex": "M",
  "dual_elgbl_cd": "02",
  "orec": "0",
  "crec": "0",
  "new_enrollee": false,
  "snp": false
}
```

#### Response

```json
{
  "community": "Community, Full Benefit Dual-Enrolled, Aged 65+",
  "hcc": [...]
}
```

---

## Authentication

A simple decorator is provided in `auth.py`. It checks for a bearer token if `ENFORCE_AUTH=true` in the environment.

Example header:

```
Authorization: Bearer your_secret_token
```

This should be replaced with a production-grade system (e.g. JWT, OAuth2).

---

## Normalization

The output includes a normalized risk score. This is calculated by dividing by the **2025 CMS normalization constant**:

```
risk_score_normalized = risk_score / 1.045
```

---

## Note on HCCinFHIR

This project is based on the [`hccinfhir`](https://github.com/mimilabs/hccinfhir) package from Mimilabs.

> Currently, this project vendors a **slightly modified fork** of `hccinfhir` to enable a missing interaction:
>
> - `HF_HCC238_V28`: Heart Failure × Specified Heart Arrhythmias

This was added in `model_interactions.py` by inserting:

```python
'HF_HCC238_V28': diagnostic_cats['HF_V28'] * int('238' in hcc_set),
```

Once this patch is accepted upstream, we will remove the vendored copy and revert to installing the original via `requirements.txt`.

---

## License

RAF-microservice is provided as-is under terms outlined by its dependencies, notably the Apache 2.0 license from HCCinFHIR.