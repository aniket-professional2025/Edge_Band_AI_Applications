# Import required packages
import os
from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO
from dotenv import load_dotenv

# Loading Environmental variables
load_dotenv()

# Initialize client with API key (make sure OPENAI_API_KEY is set in your env)
key = os.getenv("OPEN_API_KEY")
client = OpenAI(api_key = key)

# Function to generate image with OpenAI
def generate_image(prompt):
    response = client.images.generate(
        model = "dall-e-3",  # dall-e-3 dall-e-2
        prompt = prompt,
        size = "1024x1024", # The "512x512" will work for dall-e-2
        response_format =  "b64_json"
    )
    
    # Get the image as base64 and convert to PIL Image
    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_bytes))
    
    return image