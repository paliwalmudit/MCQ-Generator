import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st
# key=open("env/key.txt", "r", encoding='utf-8').read()


# Load environment variables
load_dotenv()

# Set up Google API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')



def generate_mcqs(text, number, tone):
    
    prompt_txt = open("prompts/mcq.txt", "r", encoding='utf-8').read()

    prompt = f"""
    Text: {text}
    Number: {number}
    Tone: {tone}
    {prompt_txt}
    """

    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = model.generate_content(prompt)
            quiz = response.text
            
            # Parse the generated quiz
            mcqs = quiz.split('\n\n')
            quiz_data = []
            answer_key = {}
            for mcq in mcqs:
                lines = mcq.split('\n')
                if len(lines) < 5:
                    continue
                question = lines[0].strip()  # Keep the question as is
                options = {chr(ord('a') + i): line[3:].strip() for i, line in enumerate(lines[1:5])}  # Start from index 3
                correct = lines[5][14:].strip()  # Remove "Correct answer: " and strip whitespace
                quiz_data.append({"Question": question, "Options": options})
                answer_key[question] = correct  # Store the correct answer
                
            return quiz_data, answer_key
        
        except Exception as e:
            if "500" in str(e):
                st.warning("Internal server error occurred. Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                st.error(f"An error occurred: {str(e)}")
                return None, None
    
    st.error("Failed to generate MCQs after multiple attempts.")
    return None, None
