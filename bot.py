import tweepy
import re
import random
import time
import google.generativeai as genai
from config import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, GEMINI_API_KEY

# Twitter API 認証
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Google Gemini API 認証
genai.configure(api_key=GEMINI_API_KEY)

# ユーザーごとの会話履歴を保存（簡易メモリ）
conversation_memory = {}

# Gemini API に「占い師っぽい返信」を生成させる関数
def gemini_fortune_reply(user_input, user_id):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []

    # プロンプトを作成
    prompt = f"""あなたは神秘的な占い師です。ユーザーが占い結果について質問をしています。
    霊的で不思議な雰囲気を持った占い師のキャラで答えてください。

    【過去の会話】\n""" + "\n".join(conversation_memory[user_id]) + f"""
    
    ユーザー: {user_input}
    
    あなたの返信:"""

    # Gemini API でテキスト生成
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    reply = response.text

    # 会話履歴を更新
    conversation_memory[user_id].append(f"ユーザー: {user_input}")
    conversation_memory[user_id].append(f"占い師: {reply}")

    # 履歴が長くなりすぎたら削除
    if len(conversation_memory[user_id]) > 10:
        conversation_memory[user_id] = conversation_memory[user_id][-10:]

    return reply

# メンションに対して占いの質問や感想に返信
def check_mentions():
    mentions = api.mentions_timeline(count=5)
    for mention in mentions:
        tweet_text = mention.text
        tweet_id = mention.id
        username = mention.user.screen_name
        user_id = mention.user.id_str  # ユーザーの一意なID

        # Google Gemini API で占い師っぽい返信を生成
        reply_text = gemini_fortune_reply(tweet_text, user_id)

        # Twitterに返信
        reply_status = f"@{username} {reply_text}"
        api.update_status(status=reply_status, in_reply_to_status_id=tweet_id)
        print(f"🔮 {username} に返信しました: {reply_text}")

# DMの受信をチェックする関数
def check_dms():
    dms = api.list_direct_messages(count=5)
    for dm in dms:
        sender_id = dm.message_create["sender_id"]
        text = dm.message_create["message_data"]["text"]

        # Google Gemini API に相談
        reply_text = gemini_fortune_reply(text, sender_id)
        send_dm(sender_id, reply_text)

# DMを送信する関数
def send_dm(user_id, text):
    api.send_direct_message(recipient_id=user_id, text=text)
    print(f"📩 DM送信: {text}")

# 60秒ごとにDMとリプライをチェック
while True:
    check_mentions()  # リプライのチェック
    check_dms()  # DMのチェック
    time.sleep(60)
