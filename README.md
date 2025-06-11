# 📸 PhotoCaption AI
An AI-powered web app that transforms your photos into stylish, Instagram-worthy captions — instantly. Built with Streamlit, powered by OpenAI's GPT-4o, and backed by PostgreSQL to store caption data and user feedback.

## Features

- Upload an image and generate 3 unique captions at once
- Supports multiple styles: Romantic, Poetic, Funny, Punchy, Professional, or Custom
- Rate each caption using emoji-based feedback
- Download captions as `.txt` files
- Stores captions and feedback in a PostgreSQL database
- Secure API key handling with `st.secrets`
- Beautiful UI with background imagery and responsive layout

## Tech Stack

- **Frontend & Backend**: [Streamlit](https://streamlit.io)
- **AI Captioning**: [OpenAI GPT-4o](https://platform.openai.com/docs/models/gpt-4)
- **Database**: PostgreSQL (locally or scalable for production)
- **Deployment**: [Streamlit Cloud](https://streamlit.io/cloud)

## Setup Instructions

1. Clone the Repository

```bash
git clone https://github.com/your-username/photo-caption-ai.git
cd photo-caption-ai

2. Install Dependencies

pip install -r requirements.txt

3. Set environment variables (for local testing)
Create a .env file and add the following:

OPENAI_API_KEY=your_openai_api_key
DB_NAME=photodb
DB_USER=your_username
DB_PASSWORD=your_password

4. Run the app
streamlit run app.py
