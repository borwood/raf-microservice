from flask import request
import os

# This module provides authentication decorators for Flask routes.
# It checks for the presence of an Authorization header and validates it.
# The actual authentication logic is not implemented here, but a placeholder is provided.

# The ENFORCE_AUTH environment variable determines whether authentication is required.
ENFORCE_AUTH = os.getenv("ENFORCE_AUTH", "false").lower() == "true"


def require_auth(f):
    """Decorator to require authentication for a Flask route."""

    # TODO: Implement the actual authentication logic here
    def decorated(*args, **kwargs):

        # Check if authentication is enforced, otherwise skip the check
        if not ENFORCE_AUTH:
            return f(*args, **kwargs)

        # Check if the request has the required header
        if "Authorization" not in request.headers:
            return {"error": "Authorization header is missing"}, 401

        # Extract the token from the Authorization header (I'm pretending there's a Bearer token, I don't now if we will have AWS signature or something else)
        try:
            token = request.headers["Authorization"].split(" ")[1]
        except IndexError:
            return {
                "error": "Invalid Authorization header"
            }, 401  # We expect "Bearer <token>" format

        # Placeholder validation logic
        if token != "your_secret_token":
            return {"error": "Invalid token"}, 403

        return f(*args, **kwargs)

    decorated.__name__ = f.__name__  # Preserve the original function name
    return decorated
