from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import json
import re
import os

TOKEN = os.getenv("TOKEN")  # يجب وضع التوكن في ملف .env

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا! أرسل لي نص دورة، وسأحوّله لك إلى JSON بصيغة جاهزة للمصفوفة."
    )

# دالة لتحويل نص الدورة إلى JSON بالشكل المطلوب
def parse_course_text_to_array(text):
    course = {}

    course['id'] = "hifz-quran"

    title_match = re.search(r'🌟 دورة "(.*?)" 🌟', text, re.DOTALL)
    course['title'] = title_match.group(1).strip() if title_match else ""

    desc_match = re.search(r'✨ النبذة القصيرة\n(.*?)\n---', text, re.DOTALL)
    course['description'] = desc_match.group(1).strip() if desc_match else ""

    marquee_match = re.search(r'🚨.*?\n\n(📢 .*?)\n---', text, re.DOTALL)
    course['marquee'] = marquee_match.group(1).strip() if marquee_match else f"📢 سجّل الآن في دورة {course['title']}!"

    obj_match = re.search(r'🎯 أهداف الدورة\n(.*?)\n---', text, re.DOTALL)
    course['objectives'] = [line.strip() for line in obj_match.group(1).strip().split('\n') if line.strip()] if obj_match else []

    axes_match = re.search(r'📌 المحاور الأساسية\n(.*?)\n---', text, re.DOTALL)
    course['axes'] = [line.strip() for line in axes_match.group(1).strip().split('\n') if line.strip()] if axes_match else []

    instructors_match = re.search(r'👨‍🏫 فريق المدربين\n(.*?)\n---', text, re.DOTALL)
    instructors = []
    if instructors_match:
        lines = [line for line in instructors_match.group(1).strip().split('\n') if line.strip()]
        for line in lines:
            parts = line.split('–')
            if len(parts) == 2:
                instructors.append({'name': parts[0].strip(), 'expertise': parts[1].strip()})
    course['instructors'] = instructors

    testimonials_match = re.search(r'💬 آراء المتدربين\n(.*?)\n---', text, re.DOTALL)
    testimonials = []
    if testimonials_match:
        test_entries = re.findall(r'"(.*?)"\s*–\s*(.*)', testimonials_match.group(1).strip())
        for t in test_entries:
            testimonials.append({'text': t[0], 'name': t[1]})
    course['testimonials'] = testimonials

    faq_match = re.search(r'❓ الأسئلة الشائعة\n(.*?)\n---', text, re.DOTALL)
    faq = []
    if faq_match:
        faq_lines = [line.strip() for line in faq_match.group(1).strip().split('\n') if line.strip()]
        for i in range(0, len(faq_lines), 2):
            if i+1 < len(faq_lines):
                faq.append({'question': faq_lines[i], 'answer': faq_lines[i+1]})
    course['faq'] = faq

    ach_match = re.search(r'🏆 إنجازك بعد الدورة\n(.*?)\n---', text, re.DOTALL)
    if ach_match:
        course['achievements'] = "<br>".join([line.strip() for line in ach_match.group(1).strip().split('\n') if line.strip()])
    else:
        course['achievements'] = "إنجازات الدورة ستكون متاحة بعد المشاركة."

    return course

# التعامل مع أي رسالة نصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        data = parse_course_text_to_array(text)
        json_text = json.dumps(data, ensure_ascii=False, indent=4)

        await update.message.reply_text(
            f"✅ تم تحويل النص إلى JSON:\n\n```json\n{json_text}\n```",
            parse_mode="MarkdownV2"
        )

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
