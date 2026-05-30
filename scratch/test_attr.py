from google import genai
from google.genai import types

def get_products():
    return "products"

client = genai.Client(api_key="dummy")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["test"],
        config=types.GenerateContentConfig(tools=[get_products])
    )
    print("Function calls helper exists?", hasattr(response, "function_calls"))
except Exception as e:
    print(e)
