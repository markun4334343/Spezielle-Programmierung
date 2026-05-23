from flask import Flask, jsonify
import pandas as pd
import os
import glob

app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # 1. Pfad zum Daten-Ordner
    if os.path.exists('/app/data'):
        data_dir = '/app/data'
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, '..', 'data')

    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

    if not csv_files:
        return jsonify({"error": "Keine CSV Dateien im data Ordner gefunden"}), 404

    results = {}

    # 2. Alle CSVs einlesen ohne strikte Filter
    for file_path in csv_files:
        try:
            # Wir probieren skiprows=1. Wenn das schiefgeht, probieren wir skiprows=2
            try:
                df = pd.read_csv(file_path, skiprows=1)
                if len(df.columns) < 2:
                    df = pd.read_csv(file_path, skiprows=2)
            except Exception:
                continue

            # Wir überspringen einfach die allererste Spalte (Datum) und nehmen den Rest
            for col in df.columns[1:]:
                drink_name = str(col).split(':')[0].strip()

                # Leere oder kaputte Spalten überspringen
                if not drink_name or "Unnamed" in drink_name:
                    continue

                # Werte bereinigen (Google Trends <1 wird zu 0)
                raw_values = df[col].astype(str).str.replace('<1', '0').str.replace(',', '.')
                values = pd.to_numeric(raw_values, errors='coerce').fillna(0)

                # Wenn keine echten Zahlen da sind, überspringen
                if len(values) == 0:
                    continue

                mean_val = values.mean()
                max_val = values.max()
                last_val = values.iloc[-1]

                trend = "steigend" if last_val > mean_val else "fallend"

                results[drink_name] = {
                    "mean": round(float(mean_val), 2),
                    "peak": int(max_val),
                    "trend": trend
                }
        except Exception as e:
            print(f"Fehler bei Datei {file_path}: {e}")

    # Falls wirklich gar nichts verarbeitet werden konnte
    if not results:
        return jsonify({"error": "Die CSV-Dateien konnten gelesen werden, aber es wurden keine passenden Getränkedaten gefunden."}), 500

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)