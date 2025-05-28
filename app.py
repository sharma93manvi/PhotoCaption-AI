import streamlit as st
from PIL import Image
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("📸 Photo Caption AI")

# Upload Image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file) # Open the image using PIL
    st.image(image, caption="Uploaded Image", use_column_width=True) # Show the image

    # Optionally convert image to description (this part is placeholder)
    if st.button("Generate Caption"):
        with st.spinner("Generating Caption..."):
            prompt = "Describe this image in a poetic, Intagram-style caption."

            # Optional: encode image to base64 or describe via tags (future)
            # For now, hardcoded caption generation prompt

            # Call OpenAI API - Use GPT to generate a creative caption.
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", 
                    messages=[
                        {"role": "system", "content": "You are a creative caption generator."},
                        {"role": "user", "content": prompt}
                    ]
                )
                caption = response["choices"][0]["message"]["content"]
                st.success("Caption Generated!")
                st.write(caption)
            except Exception as e:
                st.error(f"Error generating caption: {str(e)}");