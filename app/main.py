from flask import Flask
from flask_restx import Api, Resource, fields
from hccinfhir.model_calculate import calculate_raf
from app.auth import require_auth
from app.utils import format_response

app = Flask(__name__)

# Initialize Flask-RESTPlus API
api = Api(
    app,
    version="1.0",
    title="RAF Calculation API",
    description="API for calculating RAF using CMS-HCC Model V28",
)

# Defining request schema
raf_model = api.model(
    "RAFRequest",
    {
        "diagnosis_codes": fields.List(
            fields.String,
            required=True,
            example=["E119", "I10", "E11.9"],
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
                "",
            ],
            description="Dual eligibility code for this month: 01 - 10. Default is 02 which is a 'full dual' code, this code can be retrieved from service level data in the FHIR resource EOB. \n\nDual codes: https://resdac.org/cms-data/variables/medicare-medicaid-dual-eligibility-code-january \n\nFHIR EOB: https://build.fhir.org/explanationofbenefit.html",
        ),
        "orec": fields.String(
            default="0",
            enum=[
                "0",
                "1",
                "2",
                "3",
            ],
            description="Original reason for entitlement code: 0 - 3. Default is 0 which is 'age'. \n\nOREC codes: https://resdac.org/cms-data/variables/medicare-original-reason-entitlement-code-orec",
        ),
        "crec": fields.String(
            default="0",
            enum=[
                "0",
                "1",
                "2",
                "3",
                "4",
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
        "model_name": fields.String(
            default="CMS-HCC Model V28",
            description='Model name, default is "CMS-HCC Model V28". CMS defines annual updates to the model and will eventually deprecate this version.',
        ),
    },
)

# Defining calculate-raf route with POST method
@api.route("/calculate-raf")
class CalculateRAF(Resource):
    @api.expect(raf_model)
    @require_auth
    def post(self):
        """Calculate RAF using the provided diagnosis codes, age, sex, and optional model name."""
        data = api.payload
        try:
            response = format_response(
                calculate_raf(
                    diagnosis_codes=data["diagnosis_codes"],
                    model_name=data.get("model_name"),
                    age=data["age"],
                    sex=data["sex"],
                    dual_elgbl_cd=data.get("dual_elgbl_cd"),
                    orec=data.get("orec"),
                    crec=data.get("crec"),
                    new_enrollee=data.get("new_enrollee"),
                    snp=data.get("snp"),
                )
            )
            return response, 200
        except Exception as e:
            return {"error": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True)
