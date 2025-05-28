import streamlit as st
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import datetime
import base64

# Load environment variables
load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with API key
client = OpenAI(api_key=OpenAI.api_key)

# models = client.models.list()
# for model in models.data:
    # print (model.id)

if not OpenAI.api_key:
    st.error("⚠️ OPENAI_API_KEY not found in environment.")
    st.stop()

st.set_page_config(page_title="PhotoCaption AI", layout="centered")

# Custom background
# Another Background Image: https://images.unsplash.com/photo-1518837695005-2083093ee35b
# OR https://images.unsplash.com/photo-1501785888041-af3ef285b470
st.markdown("""
    <style>
    body {
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', sans-serif;
    }

    .stApp {
        background-image: url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 10px;
        max-width: 800px;
        margin: 10% auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    h1, label, .stButton button {
        color: #333;
    }
    
    .stButton>button {
        background-color: #ff6f61;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
    }
        
    </style>
""", unsafe_allow_html=True)

# Function to fetch usage
def get_openai_usage():
    # Dates in ISO format for current month
    today = datetime.date.today()
    start_date = today.replace(day=1).isoformat()
    end_date = today.isoformat()

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    try:
        response = requests.get(
             f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        if response.status_code == 200:
            usage_data = response.json()
            total_usage = usage_data["total usage"] / 100.0  # Convert cents to USD
            return f"${total_usage:.2f} used this month"
    
        else:
            return "Unable to fetch Usage"

    except Exception as e:
        return f"Error: {str(e)}"

# Display Usage in Sidebar
# st.sidebar.markdown("### 🔒 OpenAI API Usage")
# st.sidebar.info(get_openai_usage())

def image_to_base64(image):
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


# App title
st.title("📸 Photo Caption AI")
st.markdown("Effortless, aesthetic captions for your stunning shots.")

# Upload Image
uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Layout split: Image on Left, controls on right
    col1, col2 = st.columns([1, 1.2])

    with col1:
        image = Image.open(uploaded_file) # Open the image using PIL
        st.image(image, caption="Uploaded Image", use_container_width=True) # Show the image

    with col2: 

        # Changes to Make
        # 	1.	Switch model to gpt-4o
	    #   2.	Pass image as input to gpt-4o
	    #   3.	Auto-detect style if style == "Auto"
	    #   4.	Generate captions using both image and optional text prompt

        #Style Selection
        style = st.selectbox(
            "✨ Choose your caption style",
            ["Auto","Romantic", "Poetic", "Funny", "Short & Punchy", "Professional", "Custom"]
        )

        custom_style=""
        if style == "Custom":
            custom_style = st.text_input("Describe your custom style", placeholder="e.g., Minimal and soulful...")

        shoot_type = st.text_input(
            "📸 Describe the shoot (optional)",
            placeholder="e.g., Golden hour couple shoot in Vancouver",
        )

        # Style based Instructions
        style_instructions = {
            "Romantic": "Make it heartfelt, dreamy, and romantic.",
            "Poetic": "Use vivid imagery and poetic language.",
            "Funny": "Add wit, cleverness, and humor.",
            "Short & Punchy": "Keep it short, bold, and catchy for Instagram.",
            "Professional": "Keep it clean, modern, and appropriate for portfolio or branding.",
            "Custom": custom_style
        }

       # Create the prompt
        prompt = f"""You are a creative social media expert. Write a {style.lower()} Instagram-style caption for this photoshoot description:'{shoot_type}'.{style_instructions.get(style, "")} Keep it modern, punchy & emotional."""


        # Convert image to description
        if st.button("Generate Caption"):
            with st.spinner("Generating Caption..."):

                # Call OpenAI API - Use GPT to generate a creative caption.
                try:
                    # Encode image to base64 
                    base64_image = image_to_base64(image)

                    messages=[
                            {
                                "role": "system", 
                                "content": "You are a creative caption generator for photographers on Social Media. Keep it modern, catchy, and emotionally engaging."
                            },
                            {
                                "role": "user", 
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Generate an Instagram-style caption."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                    ]
                    # Add style & shoot type if available
                    if style != "Auto":
                        choosen_style = custom_style if style == "Custom" else style
                        style_instructions = f"\nUse a {choosen_style.lower()} tone."
                        if shoot_type:
                            style_instructions += f" This was a shoot described as: '{shoot_type}'"
                        messages.append({"role": "user", "content": style_instructions})
                    elif shoot_type:    
                        messages.append({"role": "user", "content": f"This was a shoot described as: '{shoot_type}'"})

                    # Make GPT-4o call
                    response = client.chat.completions.create(
                        # model="gpt-3.5-turbo", 
                        model="gpt-4o", 
                        messages = messages
                    )

                    caption = response.choices[0].message.content.strip()
                    st.success("Caption Generated!")
                    st.markdown(f"### ✨ {caption}")

                    # Caption Copy Button
                    st.code(caption, language="markdown")
                    st.button("📋 Copy to Clipboard")

                    # for easy manual copy
                    st.text_area(caption)

                except Exception as e:
                    st.error(f"🚨 Error generating caption: {str(e)}")
                
                
                
                
             
        
else:
        st.info("👆 Start by uploading a photo.")