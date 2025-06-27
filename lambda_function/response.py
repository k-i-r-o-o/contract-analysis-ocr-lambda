import json

def make_response(status_code: int, body) -> dict:
    """Format HTTP-style JSON response."""
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }
