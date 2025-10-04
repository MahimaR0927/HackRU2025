from google import genai
from google.genai import types

import requests

image_path = "https://goo.gle/instrument-img"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(
  data=image_bytes, mime_type="image/jpeg"
)

client = genai.Client(api_key ="AIzaSyCgg-000gchPm6qrgxZEkk0l_gJKgrk7qM")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["What is this image?", image],
)

print(response.text)
