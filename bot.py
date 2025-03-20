import requests
import json
import tweepy
import schedule
import time
from config import ACCESS_SECRET, Access_Token, API_KEY, API_SECRET, GEMINI_API_KEY

# Twitter認証
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, Access_Token, ACCESS_SECRET)
api = tweepy.API(auth)

# Google Gemini API のエンドポイント
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_gemini_text(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_API_URL, params=params, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "エラー: APIのレスポンス解析に失敗しました。"
    else:
        return f"エラー: APIリクエスト失敗 ({response.status_code})"

# 送信する占いメッセージを生成
def create_fortune_message():
    prompt = "今日の運勢を占ってください。"
    message = generate_gemini_text(prompt)
    return f"🌟 今日の運勢 🌟\n\n{message}\n\n#占い #今日の運勢"

# Twitterに投稿
def post_to_twitter():
    tweet = create_fortune_message()
    try:
        api.update_status(tweet)
        print("✅ ツイート成功！")
    except Exception as e:
        print(f"⚠️ ツイート失敗: {e}")

# 定期実行スケジュール（1時間ごとに投稿）
schedule.every(1).hours.do(post_to_twitter)

print("🚀 Botが起動しました！")

while True:
    schedule.run_pending()
    time.sleep(60)
