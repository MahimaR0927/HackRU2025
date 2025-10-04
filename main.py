from google import genai
from google.genai import types
from dotenv import load_dotenv

import os
import requests

import re

load_dotenv()

image_path = "https://i5.walmartimages.com/seo/YYDGH-Mens-High-Stretch-Dress-Shirts-Short-Sleeve-Button-Up-Shirts-Business-Casual-Shirt-with-Pocket-Red-S_f5280d40-e2db-4a67-ba20-4db7e5f032b9.fb1b33342f5ff31de56a550d772a285e.jpeg?odnHeight=768&odnWidth=768&odnBg=FFFFFF"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(
  data=image_bytes, mime_type="image/jpeg"
)

key = os.getenv("GEMINI_API_KEY")
client = genai.Client()

def generate_tags(image):
  with open("tags.txt", "r") as f:
    tags = f.read()

  prompt = "Select which tag or tags from the following list best fit the clothing style of the attached image:\n" + tags + "Output only the selected tags with each tag on a new line preceded and followed by two asterisks."

  response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[prompt, image],
  ).text

  tag_matches = re.findall("(?<=\\*\\*).*(?=\\*\\*)", response)
  print(tag_matches)


generate_tags(image)
