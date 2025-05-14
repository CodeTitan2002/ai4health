import os
import json
import base64
import difflib
import requests
from openpyxl import load_workbook
import google.generativeai as genai
from model.model import predict_disease
from dotenv import load_dotenv
from ses.session_manager import session_manager
from brain import analyze_medical_image
from groq import Groq

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_TEXT = "llama3-70b-8192"

class GeminiChatBot:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name=model_name)
        self.chat = self.model.start_chat(history=[])

    def send_message(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text

    def get_history(self):
        return self.chat.history

    def reset_chat(self):
        self.chat = self.model.start_chat(history=[])

def clean_disease_name(disease):
    if ". " in disease:
        return disease.split(". ", 1)[1]
    return disease


def query_groq_with_image_and_text(base64_image, user_text="Hii Doctor", session_id=None):
    try:
        # Initialize chat bot if not exists
        if not session_manager.get_context(session_id, 'chat_bot'):
            session_manager.update_context(session_id, 'chat_bot', GeminiChatBot())

        chat_bot = session_manager.get_context(session_id, 'chat_bot')
        image_description = session_manager.get_context(session_id, 'image_description')
        list_of_disease = session_manager.get_context(session_id, 'image_disease_list')

        # First-time image analysis
        if not image_description and base64_image:
            image_description, raw_disease_list = analyze_medical_image(base64_image)
            list_of_disease = [d.strip() for d in raw_disease_list.split(",") if d.strip()]
            # print(f"{list_of_disease}\n")
            session_manager.update_context(session_id, 'image_description', image_description)
            session_manager.update_context(session_id, 'image_disease_list', list_of_disease)

        # Get conversation history for context
        conversation_history = session_manager.get_conversation(session_id)
        is_first_message = len(conversation_history) < 2
        
        # Prepare prompt based on context
        if is_first_message:
            # For initial message, provide full analysis
            if image_description:
                prompt = f"""Medical Consultation:
Patient presents with eye condition. Image analysis shows: {image_description}

Patient's initial query: {user_text}

Please provide:
1. Possible conditions (be concise)
2. Key questions to help diagnose ( around 2-4)"""
            else:
                prompt = f"""Medical Consultation:
Patient's initial query: {user_text}

Please provide:
1. Possible conditions based on description
2. Key questions to help diagnose"""
        else:
            # For follow-ups, be concise and focused on the question
            prompt = f"""Follow-up Question Context:
Previous diagnosis consideration: {session_manager.get_context(session_id, 'last_diagnosis')}
Current patient question: {user_text}

Please provide a concise, direct answer to the patient's specific question without repeating previous information.
Assume youeself a qualified to give medical advice for disease , medicine , diet and etc."""

        # Get response from chat bot
        treatment_info = chat_bot.send_message(prompt)

        # Only predict disease on first message
        if is_first_message:
            combined_text = f"VISUAL SYMPTOMS: {image_description}\nPATIENT DESCRIPTION: {user_text}" if image_description else user_text
            symptom_array = get_symptom_array_from_text(combined_text)
            predicted = predict_disease(symptom_array)
            print(symptom_array)
            # print(f"{predicted}\n")
            final_disease = verify_predicted_disease(predicted, list_of_disease or [])
            # print(f"{final_disease}\n")
            if isinstance(final_disease, list):
                symptom_array_to_add = symptom_array + [clean_disease_name(final_disease[0])]
            else:
                symptom_array_to_add = symptom_array + [clean_disease_name(final_disease)]
            workbook = load_workbook("data/train_data.xlsx")
            sheet = workbook.active
            sheet.append(symptom_array_to_add)
            workbook.save("data/train_data.xlsx")

            # print(list_of_disease)
            # print(final_disease)
            session_manager.update_context(session_id, 'last_diagnosis', final_disease)
        else:
            final_disease = session_manager.get_context(session_id, 'last_diagnosis') or "Unknown Condition"
        return {
                "predicted_disease": final_disease if is_first_message else None,  # Only show on first message
                "treatment_info": treatment_info,
                "image_description": image_description if is_first_message else None  # Only show on first message
            }
        
    except Exception as e:
        raise Exception(f"Error in query_groq_with_image_and_text: {str(e)}")


def verify_predicted_disease(predicted, disease_list, cutoff=0.4):
    if not disease_list:
        return predicted

    # Try fuzzy matching using difflib
    matches = difflib.get_close_matches(predicted, disease_list, n=3, cutoff=cutoff)
    if matches:
        # If any reasonably close match exists, consider it a valid match
        return predicted
    else:
        # Return top 3 most similar diseases from list
        return matches if matches else disease_list[:3]

def get_symptom_array_from_text(combined_text):
    symptoms_list = get_all_symptoms()
    prompt = f"""
Analyze this medical description and return a JSON response with present and absent symptoms:

{combined_text}

Available symptoms (must use exact names):
{json.dumps(symptoms_list, indent=2)}

Return ONLY JSON format with two arrays:
{{
  "present": ["symptom1", "symptom2"],
  "absent": ["symptom3", "symptom4"]
}}
"""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a medical symptom analyzer. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_TEXT,
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        symptom_data = json.loads(response.choices[0].message.content)
        return [1 if symptom in symptom_data.get("present", []) else 0 for symptom in symptoms_list]
    except Exception as e:
        print(f"Error in symptom extraction: {str(e)}")
        return [0] * len(symptoms_list)

def get_all_symptoms():
    """Return the complete list of symptoms in the correct order"""
    return [
        "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing", 
        "shivering", "chills", "joint_pain", "stomach_pain", "acidity", 
        "ulcers_on_tongue", "muscle_wasting", "vomiting", "burning_micturition",
        "spotting_urination", "fatigue", "weight_gain", "anxiety",
        "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
        "lethargy", "patches_in_throat", "irregular_sugar_level", "cough",
        "high_fever", "sunken_eyes", "breathlessness", "sweating", "dehydration",
        "indigestion", "headache", "yellowish_skin", "dark_urine", "nausea",
        "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "constipation",
        "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
        "yellowing_of_eyes", "acute_liver_failure", "fluid_overload",
        "swelling_of_stomach", "swelled_lymph_nodes", "malaise",
        "blurred_and_distorted_vision", "phlegm", "throat_irritation",
        "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
        "chest_pain", "weakness_in_limbs", "fast_heart_rate",
        "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool",
        "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
        "obesity", "swollen_legs", "swollen_blood_vessels",
        "puffy_face_and_eyes", "enlarged_thyroid", "brittle_nails",
        "swollen_extremeties", "excessive_hunger", "extra_marital_contacts",
        "drying_and_tingling_lips", "slurred_speech", "knee_pain",
        "hip_joint_pain", "muscle_weakness", "stiff_neck", "swelling_joints",
        "movement_stiffness", "spinning_movements", "loss_of_balance",
        "unsteadiness", "weakness_of_one_body_side", "loss_of_smell",
        "bladder_discomfort", "foul_smell_of_urine", "continuous_feel_of_urine",
        "passage_of_gases", "internal_itching", "toxic_look_(typhos)",
        "depression", "irritability", "muscle_pain", "altered_sensorium",
        "red_spots_over_body", "belly_pain", "abnormal_menstruation",
        "dischromic_patches", "watering_from_eyes", "increased_appetite",
        "polyuria", "family_history", "mucoid_sputum", "rusty_sputum",
        "lack_of_concentration", "visual_disturbances",
        "receiving_blood_transfusion", "receiving_unsterile_injections", "coma",
        "stomach_bleeding", "distention_of_abdomen",
        "history_of_alcohol_consumption", "fluid_overload.1", "blood_in_sputum",
        "prominent_veins_on_calf", "palpitations", "painful_walking",
        "pus_filled_pimples", "blackheads", "scurring", "skin_peeling",
        "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails",
        "blister", "red_sore_around_nose", "yellow_crust_ooze"
    ]