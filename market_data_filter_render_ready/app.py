from flask import Flask, request, render_template, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        try:
            data_file = request.files['data_file']
            symbols_file = request.files['symbols_file']

            data_filename = secure_filename(data_file.filename)
            symbols_filename = secure_filename(symbols_file.filename)

            data_path = os.path.join(UPLOAD_FOLDER, data_filename)
            symbols_path = os.path.join(UPLOAD_FOLDER, symbols_filename)
            output_path = os.path.join(UPLOAD_FOLDER, 'filtered_output.csv')

            data_file.save(data_path)
            symbols_file.save(symbols_path)

            filter_data_by_SYMBOLs(data_path, symbols_path, output_path)

            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"❌ Error: {e}"
    return render_template('index.html')

def filter_data_by_SYMBOLs(data_file: str, SYMBOLs_file: str, output_file: str):
    try:
        df_data = pd.read_csv(data_file)
        df_data.columns = df_data.columns.str.replace(r'[\n\r]', '', regex=True)
        df_data.columns = df_data.columns.str.replace('"', '')
        df_data.columns = df_data.columns.str.strip().str.upper()
    except Exception as e:
        raise Exception(f"Error reading or cleaning data file: {e}")

    try:
        df_SYMBOLs = pd.read_csv(SYMBOLs_file)
        df_SYMBOLs.columns = df_SYMBOLs.columns.str.strip().str.upper()
    except Exception as e:
        raise Exception(f"Error reading SYMBOLs file: {e}")

    try:
        df_data['SYMBOL'] = df_data['SYMBOL'].astype(str).str.strip().str.upper()
        df_SYMBOLs['SYMBOL'] = df_SYMBOLs['SYMBOL'].astype(str).str.strip().str.upper()
    except KeyError:
        raise Exception("'SYMBOL' column not found after cleaning. Check the input files.")

    filtered_data = df_data[df_data['SYMBOL'].isin(df_SYMBOLs['SYMBOL'])]
    filtered_data.to_csv(output_file, index=False)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
