from collections import defaultdict, deque
import os
import telebot
from google import genai

# Render 환경변수나 코드 내에 직접 입력
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8962293588:AAGCMG6JyEGnREaa_o54GRKckKBrXSDm2hk")
GEMINI_API_KEY = os.getenv("")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

chat_memory = defaultdict(lambda: deque(maxlen=100))

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    text = message.text
    chat_id = message.chat.id
    user_name = message.from_user.first_name if message.from_user else "알 수 없음"

    if text in ["/요약", "/summary", "요약"]:
        messages = list(chat_memory[chat_id])
        if not messages:
            bot.reply_to(message, "아직 모아둔 대화 내용이 없습니다.")
            return

        bot.reply_to(message, f"🤖 최근 대화 {len(messages)}건을 AI가 요약 중입니다...")
        
        conversation_text = "\n".join(messages)
        prompt = (
            "다음은 텔레그램 채팅방의 최근 대화 내역이야. "
            "핵심 주제와 결론, 주요 내용을 글머리 기호(•)를 사용해 한국어로 깔끔하게 요약해 줘.\n\n"
            f"[대화 내역]\n{conversation_text}"
        )

        try:
            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            bot.reply_to(message, f"📋 **대화 요약 결과**\n\n{response.text}")
        except Exception as e:
            bot.reply_to(message, f"요약 중 오류가 발생했습니다: {e}")
            
    else:
        if not text.startswith('/'):
            chat_memory[chat_id].append(f"{user_name}: {text}")

if __name__ == "__main__":
    print("🤖 렌더 클라우드에서 봇이 실행 중입니다!")
    bot.infinity_polling()