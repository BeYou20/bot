from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import json
import re
import os

TOKEN = os.getenv("TOKEN") # ضع التوكن هنا أو في ملف .env

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا! أرسل لي نص دورة، وسأحوّله لك إلى JSON بصيغة جاهزة للمصفوفة."
    )

# دالة لتحويل نص الدورة إلى JSON بنفس المفاتيح المطلوبة
def parse_course_text(text):
    course = {}

    course['id'] = "hifz-quran"

    # عنوان الدورة
    title_match = re.search(r'🌟 دورة "(.*?)" 🌟', text, re.DOTALL)
    course['title'] = f"🌟 دورة {title_match.group(1).strip()} 🌟" if title_match else ""

    # وصف الدورة
    desc_match = re.search(r'✨ النبذة القصيرة\n(.*?)\n---', text, re.DOTALL)
    course['description'] = desc_match.group(1).strip() if desc_match else ""

    # الماركيه
    course['marquee'] = f"📢 سجّل الآن في دورة {title_match.group(1).strip()}، وابدأ رحلتك!" if title_match else ""

    # الأهداف
    goals_match = re.search(r'🎯 أهداف الدورة\n(.*?)\n---', text, re.DOTALL)
    course['objectives'] = [line.strip() for line in goals_match.group(1).strip().split('\n') if line.strip()] if goals_match else []

    # المحاور
    topics_match = re.search(r'📌 المحاور الأساسية\n(.*?)\n---', text, re.DOTALL)
    course['axes'] = [line.strip() for line in topics_match.group(1).strip().split('\n') if line.strip()] if topics_match else []

    # المدربون
    trainers_match = re.search(r'👨‍🏫 فريق المدربين\n(.*?)\n---', text, re.DOTALL)
    instructors = []
    if trainers_match:
        for line in trainers_match.group(1).strip().split('\n'):
            parts = line.split('–')
            if len(parts) == 2:
                instructors.append({'name': parts[0].strip(), 'expertise': parts[1].strip()})
    course['instructors'] = instructors

    # آراء المتدربين
    testimonials_match = re.search(r'💬 آراء المتدربين\n(.*?)\n---', text, re.DOTALL)
    testimonials = []
    if testimonials_match:
        test_entries = re.findall(r'"(.*?)"\s*–\s*(.*)', testimonials_match.group(1).strip())
        for t in test_entries:
            testimonials.append({'text': t[0], 'name': t[1]})
    course['testimonials'] = testimonials

    # الأسئلة الشائعة
    faq_match = re.search(r'❓ الأسئلة الشائعة\n(.*?)\n---', text, re.DOTALL)
    faq = []
    if faq_match:
        faq_lines = [line.strip() for line in faq_match.group(1).strip().split('\n') if line.strip()]
        for i in range(0, len(faq_lines), 2):
            if i+1 < len(faq_lines):
                faq.append({'question': faq_lines[i], 'answer': faq_lines[i+1]})
    course['faq'] = faq

    # الإنجازات
    accomplishments_match = re.search(r'🏆 إنجازك بعد الدورة\n(.*?)\n---', text, re.DOTALL)
    if accomplishments_match:
        course['achievements'] = "<br>".join([line.strip() for line in accomplishments_match.group(1).strip().split('\n') if line.strip()])
    else:
        course['achievements'] = "إنجازات الدورة ستكون متاحة بعد المشاركة."

    return course

# التعامل مع أي رسالة نصية
# التعامل مع أي رسالة نصية
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        data = parse_course_text(text)

        # تحويل باقي JSON بدون id
        json_lines = json.dumps({k: v for k, v in data.items() if k != "id"}, ensure_ascii=False, indent=4).splitlines()

        # دمج id في الأعلى مع علامات اقتباس
        json_text = "{\n" + f"id: \"{data['id']}\"," + "\n" + "\n".join(json_lines[1:]) + ","

        # إرسال JSON داخل صندوق كود
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
   
  
 





