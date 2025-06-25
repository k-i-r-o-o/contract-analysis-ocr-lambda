# main.py
import json
import logging
from lambda_function.handler import lambda_handler

# Configure logger so INFO shows up
logging.basicConfig(level=logging.INFO)

# Load event
with open('test_event.json') as f:
    event = json.load(f)

# Run handler
response = lambda_handler(event, None)
print("Handler response:")
print(response)
