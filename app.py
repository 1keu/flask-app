from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)

CORS(app)

# CSVデータを読み込む
data_file = 'データベース - データ.csv'
data = pd.read_csv(data_file, encoding='utf-8')

# ルートエンドポイントの定義
@app.route('/')
def home():
    return "Welcome to Flask API!"

@app.route('/get_data', methods=['GET'])
def get_data():
    # クエリパラメータ 'keyword' を取得（デフォルトは空文字列）
    keyword = request.args.get('keyword', '').lower()

    if keyword:
        # キーワードが指定されている場合、行全体を検索
        filtered_data = data[data.apply(lambda row: keyword in ' '.join(row.astype(str)).lower(), axis=1)]
    else:
        # キーワードが指定されていない場合、すべてのデータを返す
        filtered_data = data

    # 結果をJSON形式で返す
    result = filtered_data.to_dict(orient='records')
    return jsonify(result)

@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        # リクエストから新しいデータを取得
        new_entry = request.json
        print("受信したデータ:", new_entry)  # デバッグログ


        # 新しいデータをDataFrameに追加
        global data
        data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)

        # CSVファイルに保存
        data.to_csv(data_file, index=False)

        return jsonify({"message": "データが追加されました", "data": new_entry}), 201
    except Exception as e:
        return jsonify({"message": "エラーが発生しました", "error": str(e)}), 400
    


if __name__ == '__main__':
    app.run(debug=True)