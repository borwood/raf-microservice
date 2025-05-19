import bootstrap  # ensure bootstrap is imported first, adds vendor to sys.path
from flask import Flask
from flask_restx import Api, Resource, fields
from app.auth import require_auth
from app.utils import get_multi_response_v28, get_single_response_v28

app = Flask(__name__)


# Initialize Flask-RESTPlus API
api = Api(
    app,
    version="1.0",
    title="RAF Calculation API",
    description="API for calculating RAF using CMS-HCC Model V28",
)

ns_v1 = api.namespace(
    "v1", description="Version 1 namespace in case of future versions"
)
api.add_namespace(ns_v1, path="/v1")

# Defining request schema
multi_raf_model = api.model(
    "MultiRAFRequest",
    {
        "diagnosis_codes": fields.List(
            fields.String,
            required=True,
            example=["E119", "I10", "I490", "N1831", "E1122"],
            description="List of ICD-10-CM diagnosis codes with or without the decimal point.",
        ),
        "age": fields.Integer(
            required=True, min=1, description="Patient age as a non-negative integer."
        ),
        "sex": fields.String(
            required=True,
            enum=[
                "M",
                "F",
                "1",
                "2",
            ],
            description="Patient sex: M || 1 || F || 2",
        ),
        "dual_elgbl_cd": fields.String(
            default="02",
            example="02",
            enum=[
                "00",
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "PBDual",
                "FBDual",
                "NonDual"
            ],
            description="Dual eligibility code for this month: 01 - 10. Default is 02 which is a 'full dual' code, this code can be retrieved from service level data in the FHIR resource EOB. \n\nDual codes: https://resdac.org/cms-data/variables/medicare-medicaid-dual-eligibility-code-january \n\nFHIR EOB: https://build.fhir.org/explanationofbenefit.html",
        ),
        "orec": fields.String(
            default="",
            enum=[
                "0",
                "1",
                "2",
                "3",
                ""
            ],
            description="Original reason for entitlement code: 0 - 3. Default is 0 which is 'age'. \n\nOREC codes: https://resdac.org/cms-data/variables/medicare-original-reason-entitlement-code-orec",
        ),
        "crec": fields.String(
            default="",
            enum=[
                "0",
                "1",
                "2",
                "3",
                "4",
                ""
            ],
            description="Current reason for entitlement code: 0 - 4. Default is 0 which is 'age'. \n\nCREC codes: https://resdac.org/cms-data/variables/current-reason-entitlement-code",
        ),
        "new_enrollee": fields.Boolean(
            default=False,
            description="Whether the patient is a new enrollee. Default is False.",
        ),
        "snp": fields.Boolean(
            default=False,
            description="Whether the patient is in a Special Needs Plan. Default is False.",
        ),
    },
)

single_raf_model = api.model(
    "SingleRAFRequest",
    {
        "diagnosis_code": fields.String(
            required=True,
            example="E119",
            description="A single ICD-10-CM diagnosis code (str) with or without the decimal point.",
        ),
        "age": fields.Integer(
            required=True, min=1, description="Patient age as a non-negative integer."
        ),
        "sex": fields.String(
            required=True,
            enum=[
                "M",
                "F",
                "1",
                "2",
            ],
            description="Patient sex: M || 1 || F || 2",
        ),
        "dual_elgbl_cd": fields.String(
            default="02",
            example="02",
            enum=[
                "00",
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "PBDual",
                "FBDual",
                "NonDual"
            ],
            description="Dual eligibility code for this month: 01 - 10. Default is 02 which is a 'full dual' code, this code can be retrieved from service level data in the FHIR resource EOB. \n\nDual codes: https://resdac.org/cms-data/variables/medicare-medicaid-dual-eligibility-code-january \n\nFHIR EOB: https://build.fhir.org/explanationofbenefit.html",
        ),
        "orec": fields.String(
            default="",
            enum=[
                "0",
                "1",
                "2",
                "3",
                ""
            ],
            description="Original reason for entitlement code: 0 - 3. Default is 0 which is 'age'. \n\nOREC codes: https://resdac.org/cms-data/variables/medicare-original-reason-entitlement-code-orec",
        ),
        "crec": fields.String(
            default="",
            enum=[
                "0",
                "1",
                "2",
                "3",
                "4",
                ""
            ],
            description="Current reason for entitlement code: 0 - 4. Default is 0 which is 'age'. \n\nCREC codes: https://resdac.org/cms-data/variables/current-reason-entitlement-code",
        ),
        "new_enrollee": fields.Boolean(
            default=False,
            description="Whether the patient is a new enrollee. Default is False.",
        ),
        "snp": fields.Boolean(
            default=False,
            description="Whether the patient is in a Special Needs Plan. Default is False.",
        ),
    },
)

# Defining calculate-raf-v28 route with POST method
# CMS-HCC Model V28 is the latest version of the CMS-HCC risk adjustment model. CMS defines annual updates to the model and will eventually deprecate this version.
@ns_v1.route("/raf-v28/multi")
class CalculateRAF(Resource):
    @api.expect(multi_raf_model)
    @require_auth
    def post(self):
        """Calculate RAF using the provided diagnosis codes, age, and sex."""
        data = api.payload
        try:
            response = get_multi_response_v28(**data)
            return response, 200
        except Exception as e:
            return {"error": str(e)}, 400
        
@ns_v1.route("/raf-v28/single")
class CalculateRAF(Resource):
    @api.expect(single_raf_model)
    @require_auth
    def post(self):
        """Calculate the RAF coefficient of a single diagnosis, with the ICD-10, age, and sex."""
        data = api.payload
        try:
            response = get_single_response_v28(**data)
            return response, 200
        except Exception as e:
            return {"error": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True)
