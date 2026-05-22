from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # --- PFAD-LOGIK FIX ---
    # Ermittle das Verzeichnis, in dem diese Datei liegt (data_service)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigiere einen Ordner hoch und dann in 'data'
    file_path = os.path.join(base_dir, '..', 'data', 'time_series_DE_20260328-1313_20260428-1313.csv')

    # Debugging-Ausgabe im Terminal
    print(f"Suche Datei unter: {file_path}")

    if not os.path.exists(file_path):
        return jsonify({
            "error": "CSV Datei nicht gefunden",
            "gesuchter_pfad": file_path
        }), 404

    try:
        # CSV einlesen (Überspringe die erste Zeile von Google Trends)
        df = pd.read_csv(file_path, skiprows=1)

        # Spaltennamen säubern (z.B. 'Eistee: (Deutschland)' -> 'Eistee')
        df.columns = [col.split(':')[0] if ':' in col else col for col in df.columns]

        results = {}
        # Berechne Kennzahlen für alle Spalten außer der ersten (Datum)
        for col in df.columns[1:]:
            # Sicherstellen, dass die Daten numerisch sind
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            mean_val = df[col].mean()
            max_val = df[col].max()
            last_val = df[col].iloc[-1]

            trend = "steigend" if last_val > mean_val else "fallend"

            results[col] = {
                "mean": round(float(mean_val), 2),
                "peak": int(max_val),
                "trend": trend
            }

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Fehler beim Verarbeiten der CSV: {str(e)}"}), 500

if __name__ == '__main__':
    # Starte den Service auf Port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)