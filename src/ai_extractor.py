import os
import json
import time
from google import genai
from google.genai import types
from google.genai import errors

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

EXTRACTION_PROMPT = """You are a financial receipt data extraction system. Analyze the provided image of a Brazilian Pix payment receipt and extract exactly the following four fields.

Return ONLY a valid JSON object, with no additional text, no explanations, and no markdown code fences. The JSON must have exactly these keys:

- "name": the full name of the sender (the person who made the payment, usually listed under "Origem" or "De")
- "date": the transaction date, in DD/MM/YYYY format
- "amount": the transaction value, as a string in Brazilian currency format (e.g. "220,00"), without the "R$" symbol
- "receiver": the full name of the recipient (the person who received the payment, usually listed under "Destino" or "Para")

If any field cannot be identified in the image, use the string "not_identified" as its value instead of omitting the key.

Example of expected output format:
{"name": "John Doe", "date": "05/08/2026", "amount": "220,00", "receiver": "Jane Smith"}
"""

def _parse_response(text):
    parsed = json.loads(text)
    return parsed

def extract_data_from_receipt(image_bytes, max_retries = 3):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg',
                    ),
                    EXTRACTION_PROMPT
                ]
            )
            data = _parse_response(response.text)
            return data
        except errors.ServerError as e:
            if attempt == max_retries:
                raise e
            time.sleep(2 ** attempt)