from google import genai
from google.genai import types
from dotenv import load_dotenv

import os
import requests
import re

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
client = genai.Client()

def generate_tags(image_path):

  with open("./resources/tags.txt", "r") as f:
    tags = f.read()

  prompt = "Select which tag or tags from the following list best fit the clothing style of the attached image:\n" + tags + "Output only the selected tags with each tag on a new line preceded and followed by two asterisks."


  with open(image_path, 'rb') as f:
      image_bytes = f.read()

  client = genai.Client()
  response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
      types.Part.from_bytes(
        data=image_bytes,
        mime_type='image/jpeg',
      ),
      prompt
    ]
  )

  tag_matches = re.findall("(?<=\\*\\*).*(?=\\*\\*)", response.text)
  print(tag_matches)

  return tag_matches

  with open("./resources/temp_tags.txt", "w") as f:
    f.write("\n".join(tag_matches))

#generate_tags(image_path)
