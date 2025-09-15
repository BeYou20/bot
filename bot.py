import nest_asyncio
nest_asyncio.apply()

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import json
import re

# توكن البوت
TOKEN = "8362086980:AAEKp_KIRSVAB8NbAjbs130VOYL6E9wRCUU"

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا! أرسل لي نص دورة بهذا الشكل، وسأحوّله لك إلى JSON تلقائيًا."
    )

# دالة لتحويل نص الدورة إلى JSON
def parse_course_text(text):
    course = {}

    title_match = re.search(r'🌟 دورة "(.*?)" 🌟', text, re.DOTALL)
    course['course_title'] = title_match.group(1).strip() if title_match else ""

    short_desc_match = re.search(r'✨ النبذة القصيرة\n(.*?)\n---', text, re.DOTALL)
    course['short_description'] = short_desc_match.group(1).strip() if short_desc_match else ""

    about_match = re.search(r'📖 نبذة عن الدورة\n(.*?)\n---', text, re.DOTALL)
    course['about'] = about_match.group(1).strip() if about_match else ""

    goals_match = re.search(r'🎯 أهداف الدورة\n(.*?)\n---', text, re.DOTALL)
    course['goals'] = [line.strip() for line in goals_match.group(1).strip().split('\n') if line.strip()] if goals_match else []

    topics_match = re.search(r'📌 المحاور الأساسية\n(.*?)\n---', text, re.DOTALL)
    course['main_topics'] = [line.strip() for line in topics_match.group(1).strip().split('\n') if line.strip()] if topics_match else []

    testimonials_match = re.search(r'💬 آراء المتدربين\n(.*?)\n---', text, re.DOTALL)
    testimonials = []
    if testimonials_match:
        test_entries = re.findall(r'"(.*?)"\s*–\s*(.*)', testimonials_match.group(1).strip())
        for t in test_entries:
            testimonials.append({'text': t[0], 'name': t[1]})
    course['testimonials'] = testimonials

    trainers_match = re.search(r'👨‍🏫 فريق المدربين\n(.*?)\n---', text, re.DOTALL)
    trainers = []
    if trainers_match:
        trainer_lines = [line for line in trainers_match.group(1).strip().split('\n') if line.strip()]
        for line in trainer_lines:
            parts = line.split('–')
            if len(parts) == 2:
                trainers.append({'name': parts[0].strip(), 'specialty': parts[1].strip()})
    course['trainers'] = trainers

    faq_match = re.search(r'❓ الأسئلة الشائعة\n(.*?)\n---', text, re.DOTALL)
    faq = []
    if faq_match:
        faq_lines = [line.strip() for line in faq_match.group(1).strip().split('\n') if line.strip()]
        for i in range(0, len(faq_lines), 2):
            if i+1 < len(faq_lines):
                faq.append({'question': faq_lines[i], 'answer': faq_lines[i+1]})
    course['faq'] = faq

    accomplishments_match = re.search(r'🏆 إنجازك بعد الدورة\n(.*?)\n---', text, re.DOTALL)
    course['accomplishments'] = [line.strip() for line in accomplishments_match.group(1).strip().split('\n') if line.strip()] if accomplishments_match else []

    return [course]

# دالة التعامل مع أي رسالة نصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        data = parse_course_text(text)
        json_text = json.dumps(data, ensure_ascii=False, indent=4)
        # نرسل JSON داخل صندوق كود قابل للنسخ
        await update.message.reply_text(f"✅ تم تحويل النص إلى JSON:\n\n```json\n{json_text}\n```", parse_mode="MarkdownV2")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحويل: {e}")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 Bot started... أرسل نص دورة لتحويله إلى JSON")
    app.run_polling()

if __name__ == "__main__":
    main()