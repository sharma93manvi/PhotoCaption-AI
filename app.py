import streamlit as st
from PIL import Image
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
import datetime
import base64
import pyperclip

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

    .emoji-button {
        background-color: #444;
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        font-size: 1.5rem;
        cursor: pointer;
        transition: 0.3s;
        width: 100%;
    }

    .emoji-button:hover {
        transform: scale(1.05);
        opacity: 0.9;
    }

    .love { background-color: #ff69b4; }      /* Pink */
    .like { background-color: #6fa8dc; }      /* Blue */
    .dislike { background-color: #f4a460; }   /* Orange */ 
            
    .regen-button {
        background-color: #4CAF50;
        color: white;
        padding: 0.7rem 1.5rem;
        font-size: 1.1rem;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        margin-top: 1.5rem;
        transition: 0.3s;
    }
    .regen-button:hover {
        background-color: #45a049;
        transform: scale(1.03);
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

                    # ---- Generate 1 Caption -----
                    # caption = response.choices[0].message.content.strip()
                    # st.success("Caption Generated!")
                    # st.markdown(f"### ✨ {caption}")

                    # ---- Generate 3 captions -----
                    captions = []
                    for i in range(3):
                        varied_messages = messages.copy()
                        varied_messages[0] = {
                            "role": "system",
                            "content": f"You are a creative caption generator for photographers. Style: {style.lower()}. Try to make this version slightly different from the others."
                        }

                        # Make GPT-4o call
                        response = client.chat.completions.create(
                            # model="gpt-3.5-turbo", 
                            model="gpt-4o", 
                            messages = varied_messages,
                            temperature=1.0  #Add Creativity
                        )

                        variant = response.choices[0].message.content.strip()
                        captions.append(variant)

                    # Store caption and inputs in session state so we can regenerate without reloading everything
                    st.session_state.captions = captions
                    st.success("✨ 3 Captions Generated!")
                    st.session_state.image = image
                    st.session_state.shoot_type = shoot_type
                    st.session_state.style = style
                    st.session_state.custom_style = custom_style

                    # if "captions" in st.session_state:
                    #     st.markdown("### ✨ Choose from these caption ideas:")

                    #     for i, cap in enumerate(st.session_state.captions):
                    #         st.markdown(f"**Caption {i+1}:**")
                    #         st.markdown(f"> {cap}")

                    #         col_feedback = st.columns([1, 1, 1, 2])

                    #         with col_feedback[0]:
                    #             if st.button("😍", key=f"love_{i}"):
                    #                 st.success("Thanks! You loved this one 💖")

                    #         with col_feedback[1]:
                    #             if st.button("🙂", key=f"ok_{i}"):
                    #                 st.info("Marked as okay 👍")

                    #         with col_feedback[2]:
                    #             if st.button("👎", key=f"nope_{i}"):
                    #                 st.warning("Got it. We'll improve next time.")

                    #         with col_feedback[3]:
                    #             st.download_button(
                    #                 label="💾 Download",
                    #                 data=cap,
                    #                 file_name=f"caption_{i+1}.txt",
                    #                 mime="text/plain",
                    #                 key=f"download_{i}"
                    #             )

                    #         st.markdown("---")

                except Exception as e:
                    st.error(f"🚨 Error generating caption: {str(e)}")

        # Show captions from session state if available (on first run or after rerun)
        if "captions" in st.session_state:
            st.markdown("### ✨ Choose from these caption ideas:")

            for i, cap in enumerate(st.session_state.captions):
                st.markdown(f"**Caption {i+1}:**")
                st.markdown(f"> {cap}")

                col_feedback = st.columns([1, 1, 1, 2])

                with col_feedback[0]:
                    if st.button("😍", key=f"love_{i}"):
                        st.session_state[f"feedback_{i}"] = "love"

                with col_feedback[1]:
                    if st.button("🙂", key=f"ok_{i}"):
                        st.session_state[f"feedback_{i}"] = "ok"

                with col_feedback[2]:
                    if st.button("👎", key=f"dislike_{i}"):
                        st.session_state[f"feedback_{i}"] = "dislike"

                with col_feedback[3]:
                    st.download_button(
                        label="💾 Download",
                        data=cap,
                        file_name=f"caption_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_{i}"
                    )

                # Display feedback message
                if f"feedback_{i}" in st.session_state:
                    if st.session_state[f"feedback_{i}"] == "love":
                        st.success("Thanks! You loved this one 💖")
                    elif st.session_state[f"feedback_{i}"] == "ok":
                        st.info("Marked as okay 👍")
                    elif st.session_state[f"feedback_{i}"] == "dislike":
                        st.warning("Got it. We'll improve next time.")

                st.markdown("---")

            # # Regenerate button section
            # st.markdown("### 🔁 Want a different version?")
            # col_regen, _ = st.columns([1, 3])
            # with col_regen:
            #     if st.button("🔁 Regenerate Caption", key="regen_button"):
            #         with st.spinner("Re-generating..."):
            #             try:
            #                 base64_image = image_to_base64(st.session_state.image)

            #                 messages = [
            #                     {
            #                         "role": "system", 
            #                         "content": "You are a creative caption generator for photographers on Social Media. Keep it modern, catchy, and emotionally engaging."
            #                     },
            #                     {
            #                         "role": "user", 
            #                         "content": [
            #                             {
            #                                 "type": "text",
            #                                 "text": "Generate an Instagram-style caption."
            #                             },
            #                             {
            #                                 "type": "image_url",
            #                                 "image_url": {
            #                                     "url": f"data:image/jpeg;base64,{base64_image}"
            #                                 }
            #                             }
            #                         ]
            #                     }
            #                 ]

            #                 # Rebuild prompt based on style and shoot type
            #                 chosen_style = st.session_state.custom_style if st.session_state.style == "Custom" else st.session_state.style
            #                 if st.session_state.style != "Auto":
            #                     style_instruction = f"\nUse a {chosen_style.lower()} tone."
            #                     if st.session_state.shoot_type:
            #                         style_instruction += f" This was a shoot described as: '{st.session_state.shoot_type}'"
            #                     messages.append({"role": "user", "content": style_instruction})
            #                 elif st.session_state.shoot_type:
            #                     messages.append({"role": "user", "content": f"This was a shoot described as: '{st.session_state.shoot_type}'"})

            #                 response = client.chat.completions.create(
            #                     model="gpt-4o",
            #                     messages=messages
            #                 )
            #                 st.session_state.caption = response.choices[0].message.content.strip()
            #                 st.experimental_rerun()
            #             except Exception as e:
            #                 st.error(f"🚨 Error generating caption: {str(e)}")

            # # Feedback section
            # if "caption" in st.session_state and st.session_state.caption:
            #     st.markdown("### 💬 How do you feel about this caption?")
            #     feedback_col1, feedback_col2, feedback_col3 = st.columns(3)

            #     if "feedback_given" not in st.session_state:
            #         st.session_state.feedback_given = False
            #         st.session_state.feedback_value = None

            #     with feedback_col1:
            #         if st.button("😍 Love it", key="love_btn"):
            #             st.session_state.feedback_given = True
            #             st.session_state.feedback_value = "love"

            #     with feedback_col2:
            #         if st.button("🙂 It's okay", key="like_btn"):
            #             st.session_state.feedback_given = True
            #             st.session_state.feedback_value = "okay"

            #     with feedback_col3:
            #         if st.button("👎 Not great", key="dislike_btn"):
            #             st.session_state.feedback_given = True
            #             st.session_state.feedback_value = "dislike"

            #     if st.session_state.feedback_given:
            #         if st.session_state.feedback_value == "love":
            #             st.success("Thanks for your feedback! 💖")
            #         elif st.session_state.feedback_value == "okay":
            #             st.info("Noted! Thanks for sharing. 👍")
            #         elif st.session_state.feedback_value == "dislike":
            #             st.warning("Got it! We’ll try to do better next time. 🙏")

            #     # Add download button for the caption below the feedback section.
            #     st.download_button(
            #         label="💾 Download Caption as .txt",
            #         data=st.session_state.caption,
            #         file_name="photo_caption.txt",
            #         mime="text/plain"
            #     )

else:
        st.info("👆 Start by uploading a photo.")

st.markdown(
    """
    <div style='position: fixed; bottom: 15px; width: 100%; text-align: center;'>
        <span style='color: white; font-size: 20px; font-weight: bold;'>
            © 2025 HappyHungryHues 📸 | 
            <a href='https://www.instagram.com/happyhungryhues/' target='_blank' style='color: white; text-decoration: underline;'>
                Instagram
            </a> |
            <a href='https://happyhungryhues.mypixieset.com/' target='_blank' style='color: white; text-decoration: underline;'>
                Website
            </a>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)