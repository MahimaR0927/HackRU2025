from google import genai
from google.genai import types
from dotenv import load_dotenv

import os
import requests
load_dotenv()

image_path = "https://goo.gle/instrument-img"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(
  data=image_bytes, mime_type="image/jpeg"
)

with open("tags.txt", "r") as f:
  possible_tags = f.read().splitlines()

prompt = "Given the following "



key = os.getenv("GEMINI_API_KEY")
client = genai.Client()



response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["What is this image?", image],
)

print(response.text)
