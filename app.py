"""
app.py — servidor web básico para buscar-cuit.

Uso local:
    python -m venv venv
    source venv/bin/activate   (Windows: venv\\Scripts\\activate)
    pip install -r requirements.txt
    python app.py

Después abrí http://127.0.0.1:5000 en el navegador.
"""

from flask import Flask, render_template, jsonify
from cuit_lookup import consultar_cuit, formatear_dict, CuitInvalido, ConsultaError

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cuit/<cuit>")
def api_cuit(cuit):
    try:
        data = consultar_cuit(cuit)
        return jsonify({"ok": True, "resultado": formatear_dict(data)})
    except CuitInvalido as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except ConsultaError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


if __name__ == "__main__":
    app.run(debug=True)
