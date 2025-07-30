from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
from model import run_model_with_probs
from config import CONFIG

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/'

@app.route("/", methods=["GET", "POST"])
def index():
    predictions = None
    probs = None
    chart_url = None
    error = None

    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename.endswith('.csv'):
            error = "Please upload a valid CSV file."
        else:
            try:
                df = pd.read_csv(file)
                if 'target' not in df.columns:
                    error = "Missing 'target' column in CSV."
                else:
                    predictions, probs = run_model_with_probs(df)
                    fig, ax = plt.subplots()
                    ax.hist(probs, bins=10)
                    ax.set_title("Prediction Confidence")
                    ax.set_xlabel("Probability")
                    ax.set_ylabel("Count")
                    chart_filename = f"static/{uuid.uuid4().hex}.png"
                    fig.savefig(chart_filename)
                    plt.close(fig)
                    chart_url = '/' + chart_filename
            except Exception as e:
                error = f"Error processing file: {e}"

    return render_template("index.html", predictions=predictions, probs=probs, chart_url=chart_url, error=error)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
