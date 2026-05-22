from flask import Flask, jsonify, render_template
import requests
import os
from openai import OpenAI

# Pfad-Logik für Templates
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# URL zum Data Service
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:5001/api/stats")

# Dein DEEPSEEK Key hier eintragen
AI_API_KEY = "sk-d14d57adef31432f888f312aa56c51ef"

client = OpenAI(
    api_key=AI_API_KEY,
    base_url="https://api.deepseek.com"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['GET'])
def analyze():
    # 1. Daten vom Data Service holen
    try:
        response = requests.get(DATA_SERVICE_URL, timeout=5)
        data = response.json()
    except Exception as e:
        return jsonify({"error": f"Data Service nicht erreichbar: {str(e)}"}), 500

    # 2. KI-Anfrage (Deepseek)
    try:
        stats_text = ", ".join([f"{k}: Mean {v['mean']}" for k, v in data.items()])

        # 3. KI-Anfrage senden (Modellname für Deepseek korrigiert)
        try:
            completion = client.chat.completions.create(
                model="deepseek-v4-flash", # Oder "deepseek-v4-pro"
                messages=[
                    {"role": "system", "content": "Du bist ein Datenanalyst für Getränketrends."},
                    {"role": "user", "content": f"Analysiere kurz in 3 Sätzen die Trends für: {stats_text}"}
                ]
            )
            ai_response = completion.choices[0].message.content
        except Exception as ai_err:
            print(f"AI Error: {ai_err}")
            ai_response = f"KI-Fehler: {str(ai_err)}. Bitte Modellnamen oder Key prüfen!"
        ai_response = completion.choices[0].message.content
    except Exception as ai_err:
        # Falls der Key falsch ist: Kein Absturz, sondern Fehlermeldung im JSON
        print(f"Deepseek Error: {ai_err}")
        ai_response = f"KI-Fehler: {str(ai_err)}. Bitte API-Key prüfen!"

    # WICHTIG: Wir geben IMMER verarbeitete_daten zurück, damit die Charts nicht leer bleiben
    return jsonify({
        "ki_analyse": ai_response,
        "verarbeitete_daten": data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)