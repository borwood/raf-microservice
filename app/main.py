from flask import Flask
from flask_restx import Api, Resource, fields
from pydantic import BaseModel
from hccinfhir.model_calculate import calculate_raf
from app.auth import require_auth

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
        "model_name": fields.String(
            default="CMS-HCC Model V28",
            description='Model name, default is "CMS-HCC Model V28". CMS defines annual updates to the model and will eventually deprecate this version.',
        ),
    },
)


def sanitize_for_JSON(d):
    """Utility function: Recursively convert all sets in a dict to lists and process BaseModel objects as dict."""
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

def only_required_fields(raf_response):
    """Utility function: Strip out unnecessary fields from the calculate_raf() output."""
    raf_response = sanitize_for_JSON(raf_response)
    return {
        "risk_score": raf_response["risk_score"],
        "coefficients": raf_response["coefficients"],
    }


# Defining calculate-raf route with POST method
@api.route("/calculate-raf")
class CalculateRAF(Resource):
    @api.expect(raf_model)
    @require_auth
    def post(self):
        """Calculate RAF using the provided diagnosis codes, age, sex, and optional model name."""
        data = api.payload
        try:
            result = only_required_fields(
                calculate_raf(
                    diagnosis_codes=data["diagnosis_codes"],
                    model_name="CMS-HCC Model V28",
                    age=data["age"],
                    sex=data["sex"],
                )
            )
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True)
    # print(
    #     calculate_raf(
    #         diagnosis_codes=["E119"],
    #         model_name="CMS-HCC Model V28",
    #         age=66,
    #         sex="F",
    #     )
    # )
