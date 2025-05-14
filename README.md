AI4Health - Medical Chatbot

This is a medical chatbot that predicts diseases based on both symptom text and medical images. It uses image captioning, an LLM to convert symptoms to a binary vector, and a trained Random Forest classifier to predict the disease. The chatbot also supports follow-up questions using context memory.

Project Features:

Upload symptom text

Upload related medical image (e.g., X-ray)

Generates symptom vector using LLM (Gemini / Groq)

Predicts disease using Random Forest model

Uses chat history to answer follow-up questions

Built with Streamlit for a clean UI

Project Structure:

app.py – Main Streamlit app

brain.py – Central logic controller

llm/llm_handler.py – Gemini or Groq LLM handler

model/model.py – Random Forest prediction

ses/session_manager.py – Session memory for chat

data/ – Input datasets

doctors_data.csv – Sample doctor data

model3.png – Project architecture image

requirements.txt – Required Python packages

.env – API keys (ignored by git)

.gitignore – To ignore venv, .env, and other files

Setup Instructions:

Clone the repo:
git clone https://github.com/CodeTitan2002/ai4health

Navigate to the folder:
cd ai4health

Create a virtual environment:
python -m venv venv

Activate the environment:

On Windows: venv\Scripts\activate

On Mac/Linux: source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Add your API key to a .env file:
Example:
GEMINI_API_KEY=your_gemini_api_key

Run the app:
streamlit run app.py

Technologies Used:

Python

Streamlit

Scikit-learn (Random Forest)

Gemini / Groq LLM APIs

Custom session manager

Pandas, NumPy

Author:
Subham Rathi
GitHub: github.com/CodeTitan2002
