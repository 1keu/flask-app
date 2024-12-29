import os
import pandas as pd
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# グローバル変数としてデータを保持
data = None

def load_csv_from_remote():
    csv_url = os.getenv("CSV_URL")
    if not csv_url:
        raise ValueError("環境変数 'CSV_URL' が設定されていません")
    
    try:
        response = requests.get(csv_url)
        response.raise_for_status()  # HTTPエラーチェック
        csv_data = response.content.decode('utf-8')
        return pd.read_csv(pd.compat.StringIO(csv_data))
    except Exception as e:
        print(f"CSVの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame()  # 空のDataFrameを返す

# アプリケーション起動時にデータをロード
data = load_csv_from_remote()

@app.route('/')
def home():
    csv_url = os.getenv("CSV_URL", "環境変数が設定されていません")
    return f"Welcome to Flask API! CSV_URL: {csv_url}"

@app.route('/get_data', methods=['GET'])
def get_data():
    global data
    keyword = request.args.get('keyword', '').lower()
    
    if keyword:
        filtered_data = data[data.apply(lambda row: keyword in ' '.join(row.astype(str)).lower(), axis=1)]
    else:
        filtered_data = data

    result = filtered_data.to_dict(orient='records')
    return jsonify(result)

@app.route('/add_data', methods=['POST'])
def add_data():
    global data
    try:
        new_entry = request.json
        print("受信したデータ:", new_entry)  # デバッグ用
        data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
        return jsonify({"message": "データが追加されました", "data": new_entry}), 201
    except Exception as e:
        return jsonify({"message": "エラーが発生しました", "error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)