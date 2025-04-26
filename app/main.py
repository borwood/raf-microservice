from flask import Flask, request, jsonify
from pydantic import BaseModel
from hccinfhir.model_calculate import calculate_raf

app = Flask(__name__)


def clean_dict(d):
    """Recursively convert all sets in a dictionary to lists."""
    if issubclass(type(d), dict):
        return {k: clean_dict(v) for k, v in d.items()}  # Recursively clean dicts
    elif isinstance(d, BaseModel):
        return {
            k: clean_dict(v) for k, v in d.model_dump().items()
        }  # Convert Pydantic model to dict
    elif issubclass(type(d), set):
        return list(d)
    else:
        return d


@app.route("/calculate-raf-v28", methods=["POST"])
def calculate():
    data = request.json
    try:
        result = clean_dict(
            calculate_raf(
                diagnosis_codes=data["diagnosis_codes"],
                model_name="CMS-HCC Model V28",
                age=data["age"],
                sex=data["sex"],
            )
        )

        # Debugging output: jsonify can't serialize the result directly even though it's a dict
        # so we need to determine which value in the result is coming up as a 'set', including inside nested dicts
        print(type(result))
        # result.pop("demographics", None)  # Remove demographics if present
        # cleaned_result = {}

        # for key, value in result.items():
        #     if isinstance(value, set):
        #         cleaned_result[key] = list(value)  # Convert set to list
        #     else:
        #         cleaned_result[key] = value
        # for key, value in result.items():
        #     print(f"{key}: {type(value)}")

        # response =

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


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
