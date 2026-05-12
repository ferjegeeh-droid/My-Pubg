import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعدادات التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن الخاص بك
TOKEN = "8752935054:AAEmRFpDOK-tWQNlLzrsPyF-9HOkYseh3kI"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 بوت جودة ببجي الكريستالية (itsscale 4) جاهز!\n\n"
        "أرسل الفيديو كـ (Video) أو (Document) وسأقوم بمعالجته لـ 4K/60fps."
    )

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not hasattr(video, 'file_id'):
        return

    status_msg = await update.message.reply_text("📥 جاري تحميل الفيديو... انتظر قليلاً.")
    
    input_path = f"in_{update.message.chat_id}.mp4"
    output_path = f"crystal_{update.message.chat_id}.mp4"
    
    try:
        video_file = await context.bot.get_file(video.file_id)
        await video_file.download_to_drive(input_path)

        await status_msg.edit_text("⚙️ جاري معالجة الجودة (itsscale 4)...\nقد يستغرق ذلك دقائق حسب طول الفيديو.")

        # الكود المخصص لببجي (توازن بين الجودة وقوة السيرفر)
        command = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', (
                "scale=2160:3840:flags=lanczos,"  # رفع الدقة 4K
                "unsharp=5:5:1.2:5:5:1.2,"        # حدة الكريستال
                "eq=saturation=1.5:contrast=1.1," # ألوان ببجي القوية
                "minterpolate='fps=60:mi_mode=mci'" # سلاسة 60 فريم
            ),
            '-c:v', 'libx264', 
            '-crf', '20', # جودة عالية مع حجم ملف معقول للسيرفر
            '-preset', 'ultrafast', # ضروري جداً لعدم تعليق سيرفر Render
            '-pix_fmt', 'yuv420p',
            output_path
        ]

        subprocess.run(command, check=True)
        
        await status_msg.edit_text("✅ تمت المعالجة! جاري الرفع كملف...")
        
        with open(output_path, 'rb') as doc:
            await update.message.reply_document(
                document=doc,
                filename="Crystal_4K_60fps.mp4",
                caption="✅ تم رفع الجودة (itsscale 4)\n🎬 جاهز للنشر كـ ترند"
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")
    
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, process_video))
    application.run_polling()

if __name__ == '__main__':
    main()
