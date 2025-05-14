# import streamlit as st
# import base64
# import uuid
# from PIL import Image
# from io import BytesIO

# from ses.session_manager import (
#     add_message, get_conversation, clear_session,
#     session_manager
# )
# from llm.llm_handler import query_groq_with_image_and_text

# # Helper to convert image to base64
# def encode_image(img):
#     buffered = BytesIO()
#     img.save(buffered, format="JPEG")
#     return base64.b64encode(buffered.getvalue()).decode("utf-8")

# # Helper to decode base64 to Image object
# def decode_image(base64_str):
#     return Image.open(BytesIO(base64.b64decode(base64_str)))

# # Initialize session state
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())
#     st.session_state.image_uploaded = False
#     st.session_state.base64_image = None

# st.set_page_config(page_title="Medical Diagnosis Chatbot", layout="centered")
# st.title("🩺 Medical Diagnosis Chatbot")

# # Sidebar controls
# with st.sidebar:
#     st.markdown("### Session Controls")
#     if st.button("🔄 Reset Session"):
#         clear_session(st.session_state.session_id)
#         st.session_state.image_uploaded = False
#         st.session_state.base64_image = None
#         st.session_state.session_id = str(uuid.uuid4())
#         st.rerun()
# if st.session_state.image_uploaded:
#     st.markdown("### 🖼️ Uploaded Image")
#     st.image(
#         decode_image(st.session_state.base64_image),
#         width=300,
#         caption="Uploaded Medical Image"
#     )

# # Upload Image Section
# if not st.session_state.image_uploaded:
#     with st.expander("📷 Upload Medical Image (Optional)", expanded=True):
#         image_file = st.file_uploader("Upload medical image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
#         if image_file:
#             try:
#                 if image_file.size > 1_000_000:
#                     st.error("❌ Image too large (max 1MB)")
#                 else:
#                     org_img = Image.open(image_file)
#                     base64_img = encode_image(org_img)
#                     st.session_state.base64_image = base64_img
#                     st.session_state.image_uploaded = True
#                     session_manager.update_context(st.session_state.session_id, "image_uploaded", True)
#                     session_manager.update_context(st.session_state.session_id, "base64_image", base64_img)
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"❌ Error processing image: {str(e)}")

# # Display conversation history
# conversation = get_conversation(st.session_state.session_id)
# for msg in conversation:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # Chat Input
# if prompt := st.chat_input("💬 Describe your symptoms or ask a medical question"):
#     session_id = st.session_state.session_id
    
#     # Add user message to chat
#     add_message(session_id, "user", prompt)
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     base64_img = st.session_state.base64_image or session_manager.get_context(session_id, "base64_image")
#     org_img = decode_image(base64_img) if base64_img else None
    
#     # Query the LLM + model
#     try:
#         with st.spinner("🔍 Analyzing your symptoms..."):
#             response = query_groq_with_image_and_text(
#                 org_img,
#                 prompt,
#                 session_id
#             )
            
#             with st.chat_message("assistant"):
#                 if response.get("predicted_disease") and len(get_conversation(session_id)) < 3:
#                     st.success(f"🩺 Possible Condition: **{response['predicted_disease']}**")
                
#                 if response.get("image_description") and len(get_conversation(session_id)) < 3:
#                     with st.expander("📷 Image Analysis"):
#                         st.write(response["image_description"])
                
#                 st.markdown(response["treatment_info"])
            
#             assistant_response = response["treatment_info"]
#             add_message(session_id, "assistant", assistant_response)
#     except Exception as e:
#         error_msg = f"❌ An error occurred: {str(e)}"
#         with st.chat_message("assistant"):
#             st.error(error_msg)
#         add_message(session_id, "assistant", error_msg)
# --------------------------------------------------------------
# # Add this near the top
import streamlit as st
import base64
import uuid
from PIL import Image
from io import BytesIO

from ses.session_manager import (
    add_message, get_conversation, clear_session,
    session_manager
)
from llm.llm_handler import query_groq_with_image_and_text

# Helper to convert image to base64
def encode_image(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Helper to decode base64 to Image object
def decode_image(base64_str):
    return Image.open(BytesIO(base64.b64decode(base64_str)))

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.image_uploaded = False
    st.session_state.base64_image = None

st.set_page_config(page_title="Medical Diagnosis Chatbot", layout="centered")
st.title("🩺 Medical Diagnosis Chatbot")

# 🔗 Link to Find Doctor Page
# st.markdown("[🔍 Find a Doctor]()")

# Sidebar controls
with st.sidebar:
    st.markdown("### Session Controls")
    if st.button("🔄 Reset Session"):
        clear_session(st.session_state.session_id)
        st.session_state.image_uploaded = False
        st.session_state.base64_image = None
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Show uploaded image if available
if st.session_state.image_uploaded:
    st.markdown("### 🖼️ Uploaded Image")
    st.image(
        decode_image(st.session_state.base64_image),
        width=300,
        caption="Uploaded Medical Image"
    )

# Upload image section
if not st.session_state.image_uploaded:
    with st.expander("📷 Upload Medical Image (Optional)", expanded=True):
        image_file = st.file_uploader("Upload medical image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if image_file:
            try:
                if image_file.size > 1_000_000:
                    st.error("❌ Image too large (max 1MB)")
                else:
                    org_img = Image.open(image_file)
                    base64_img = encode_image(org_img)
                    st.session_state.base64_image = base64_img
                    st.session_state.image_uploaded = True
                    session_manager.update_context(st.session_state.session_id, "image_uploaded", True)
                    session_manager.update_context(st.session_state.session_id, "base64_image", base64_img)
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")

# Display conversation history
conversation = get_conversation(st.session_state.session_id)
for msg in conversation:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("💬 Describe your symptoms or ask a medical question"):
    session_id = st.session_state.session_id
    
    add_message(session_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    base64_img = st.session_state.base64_image or session_manager.get_context(session_id, "base64_image")
    org_img = decode_image(base64_img) if base64_img else None

    try:
        with st.spinner("🔍 Analyzing your symptoms..."):
            response = query_groq_with_image_and_text(org_img, prompt, session_id)
            
            with st.chat_message("assistant"):
                if response.get("predicted_disease") and len(get_conversation(session_id)) < 3:
                    st.success(f"🩺 Possible Condition: **{response['predicted_disease']}**")
                
                if response.get("image_description") and len(get_conversation(session_id)) < 3:
                    with st.expander("📷 Image Analysis"):
                        st.write(response["image_description"])
                
                st.markdown(response["treatment_info"])
            
            assistant_response = response["treatment_info"]
            add_message(session_id, "assistant", assistant_response)
    except Exception as e:
        error_msg = f"❌ An error occurred: {str(e)}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        add_message(session_id, "assistant", error_msg)
