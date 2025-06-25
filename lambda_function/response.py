import json

def make_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }
