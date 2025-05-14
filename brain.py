import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import mimetypes
import tkinter as tk
from tkinter import filedialog

# Load environment variables
load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_medical_image(image_path: str) -> tuple[str, str]:
    """
    Analyze medical image and return two text outputs:
    1. Detailed description of symptoms and characteristics 
    2. Possible disease that could cause these symptoms  ( disease name only in this format for ex.['1. Cataract', '2. Corneal opacity', '3. Uveitis', '4. Glaucoma', '5.  Nuclear sclerosis'])
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # First prompt for symptoms and characteristics
        symptoms_prompt = """Analyze this medical image thoroughly and provide:
        1. Detailed description of all visible symptoms
        2. Characteristics (color, texture, pattern, location)
        
        Be objective and factual. Focus only on what is visible in the image.(max limit 150 words)"""
        
        symptoms_response = model.generate_content([symptoms_prompt, image_path])
        
        # Second prompt for possible conditions
        conditions_prompt = """Based on the visible symptoms in this medical image,
        suggest 3-5 possible disease that could cause these symptoms. ( disease names only without any deatail or anu other messgae direct there names ) for ex. 1. Acne vulgaris' '2. Rosacea'  '3. Perioral dermatitis' """
        
        conditions_response = model.generate_content([conditions_prompt, image_path])
        # Inside analyze_medical_image (end of function):
        return (symptoms_response.text, conditions_response.text.replace("\n", ", "))

        # return (symptoms_response.text, conditions_response.text)
    
    except Exception as e:
        return (f"Error analyzing image: {str(e)}", "")

