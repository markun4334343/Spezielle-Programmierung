import os
import requests
from flask import Flask, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)

DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://data-service:5001/api/stats")
AI_API_KEY = os.getenv("AI_API_KEY", "sk-d14d57adef31432f888f312aa56c51ef")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")

# Den Client erst im Request initialisieren, um Fehler besser abzufangen
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET'])
def analyze():
    try:
        # 1. Daten holen
        response = requests.get(DATA_SERVICE_URL)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return jsonify({"error": data["error"]}), 400

        # 2. Prompt bauen
        prompt = f"""
        Du bist ein Datenanalyst. Analysiere die folgenden Google Trends Kennzahlen für die Kategorie 'Cold Drinks'.
        Die Daten beinhalten Durchschnittsinteresse (mean), Spitzeninteresse (peak) und den Trend.
        Fasse die wichtigsten Erkenntnisse in 3-4 Sätzen zusammen. Welche Getränke dominieren, wo gibt es Peaks?
        
        Daten: {data}
        """

        ki_text = "Die KI konnte leider keine Antwort generieren."

        # 3. KI aufrufen (mit Try-Except Block, falls DeepSeek streikt)
        try:
            client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)
            completion = client.chat.completions.create(
                model="deepseek-chat", # Nutze deepseek-chat, das ist sicherer als v4-flash
                messages=[
                    {"role": "system", "content": "Du bist ein präziser Datenanalyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250
            )
            ki_text = completion.choices[0].message.content
        except Exception as api_err:
            print(f"API Fehler: {api_err}")
            ki_text = f"Fehler bei der KI-Generierung: {str(api_err)}"

        # 4. Zurück ans Frontend
        return jsonify({
            "ki_analyse": ki_text,
            "verarbeitete_daten": data
        })

    except Exception as e:
        print(f"Allgemeiner Fehler: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)