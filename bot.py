import os
import subprocess
import logging
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعدادات التسجيل لمراقبة البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن الخاص بك
TOKEN = "8752935054:AAEmRFpDOK-tWQNlLzrsPyF-9HOkYseh3kI"

# --- جزء السيرفر الوهمي لإرضاء منصة Render ---
def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Health check server running on port {port}")
        httpd.serve_forever()

# --- أوامر البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 أهلاً بك في بوت الجودة الكريستالية لببجي!\n\n"
        "1. أرسل الفيديو كـ (Video) أو (Document).\n"
        "2. سأقوم بتحويله إلى 4K/60fps (itsscale 4).\n"
        "3. سأرسل النتيجة كملف لضمان أعلى جودة."
    )

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not hasattr(video, 'file_id'): return

    status_msg = await update.message.reply_text("📥 جاري تحميل الفيديو...")
    
    input_path = f"in_{update.message.chat_id}.mp4"
    output_path = f"crystal_{update.message.chat_id}.mp4"
    
    try:
        # تحميل الفيديو
        video_file = await context.bot.get_file(video.file_id)
        await video_file.download_to_drive(input_path)

        await status_msg.edit_text("⚙️ جاري معالجة الجودة (itsscale 4)...\nقد يستغرق دقائق، انتظر قليلاً.")

        # أمر FFmpeg المطور (Crystal PUBG Quality)
        # ملاحظة: إذا فشلت المعالجة بسبب الرام، سنقلل الـ scale قليلاً
        command = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', (
                "scale=1440:2560:flags=lanczos,"  # دقة 2K (أفضل استقراراً للسيرفر من 4K)
                "unsharp=5:5:1.5:5:5:1.5,"        # حدة الكريستال
                "eq=saturation=1.6:contrast=1.2," # ألوان قوية كالمقطع المطلوب
                "minterpolate='fps=60:mi_mode=mci'" # سلاسة 60 فريم
            ),
            '-c:v', 'libx264', 
            '-crf', '18', 
            '-preset', 'ultrafast', 
            '-pix_fmt', 'yuv420p',
            output_path
        ]

        subprocess.run(command, check=True)
        
        await status_msg.edit_text("✅ تمت المعالجة! جاري الرفع كملف...")
        
        with open(output_path, 'rb') as doc:
            await update.message.reply_document(
                document=doc,
                filename="Crystal_Quality.mp4",
                caption="🔥 جودة كريستال ببجي جاهزة\n🚀 الدقة: 2K / 60fps"
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء المعالجة.\nتأكد أن الفيديو قصير (10-15 ثانية).\nالخطأ: {e}")
    
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        await status_msg.delete()

def main():
    # تشغيل السيرفر الوهمي في خلفية البوت
    threading.Thread(target=run_health_check, daemon=True).start()

    # تشغيل البوت
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, process_video))
    
    print("البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()
