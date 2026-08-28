import os
import requests
import datetime
import wikipedia
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# This is the exact line Render is looking for and failing to find!
app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_FREE_GROQ_API_KEY")

def get_ai_response(command):
    try:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are Jarvis, a concise web-based voice assistant."},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message.content
    except Exception:
        return "I encountered an error connecting to the AI processor."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_command():
    data = request.get_json()
    command = data.get("command", "").strip().lower()
    
    response = {"reply": "", "action": "none", "url": ""}
    
    if "open youtube shorts" in command or "open shorts" in command:
        response["reply"] = "Opening YouTube Shorts in a new window."
        response["action"] = "open_url"
        response["url"] = "https://www.youtube.com/shorts"
        
    elif "open youtube" in command:
        response["reply"] = "Opening YouTube."
        response["action"] = "open_url"
        response["url"] = "https://www.youtube.com"
        
    elif command.startswith("play") and "on youtube" in command:
        song = command.replace("play", "").replace("on youtube", "").strip()
        response["reply"] = f"Playing {song} on YouTube."
        response["action"] = "open_url"
        response["url"] = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
    
    elif "scroll down" in command or "scroll up" in command or command.startswith("write ") or "lock screen" in command:
        response["reply"] = "As a web-based assistant, I do not have permission to control your computer's keyboard or mouse."
        
    elif "weather" in command:
        try:
            report = requests.get("https://wttr.in/Surat?format=%C+with+a+temperature+of+%t").text
            response["reply"] = f"The current weather in Surat is {report.replace('+', ' ').strip()}"
        except:
            response["reply"] = "Unable to fetch live weather data."
            
    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            response["reply"] = wikipedia.summary(topic, sentences=2)
        except:
            response["reply"] = "I couldn't find a summary for that on Wikipedia."
            
    elif "time" in command:
        response["reply"] = f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "date" in command:
        response["reply"] = f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}"
        
    else:
        response["reply"] = get_ai_response(command)

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
