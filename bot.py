import os
import subprocess
import asyncio
import threading
import http.server
import socketserver
from pyrogram import Client, filters

# --- بياناتك الخاصة التي قدمتها ---
API_ID = 34854054
API_HASH = "755af2664322b4e5054bb26b278092ac"
BOT_TOKEN = "8752935054:AAEmRFpDOK-tWQNlLzrsPyF-9HOkYseh3kI"

# إنشاء تطبيق البوت باستخدام Pyrogram
app = Client("crystal_pubg_pro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- سيرفر وهمي لإبقاء Render في حالة Live ---
def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Health check running on port {port}")
        httpd.serve_forever()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🚀 **تم تفعيل البوت الاحترافي بنجاح!**\n\n"
        "أرسل الآن أي فيديو ببجي (حتى لو حجمه كبير).\n"
        "سأقوم بتحويله إلى جودة **Crystal 1080p/60fps**."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message):
    # التحقق من أن الملف فيديو
    media = message.video or message.document
    if not media or (message.document and "video" not in message.document.mime_type):
        return

    status_msg = await message.reply_text("📥 جاري تحميل الفيديو من تلجرام...")
    
    # تحميل الفيديو (بدون قيود الـ 20 ميجا)
    input_path = await client.download_media(message)
    output_path = f"crystal_{message.chat.id}.mp4"

    await status_msg.edit_text("⚙️ جاري معالجة الجودة (itsscale 4)...\nقد يستغرق ذلك وقتاً حسب طول المقطع.")

    # أمر FFmpeg المطور (Crystal Quality + Stability)
    # تم ضبط الإعدادات لتكون قوية وبنفس الوقت لا تسبب انهيار لسيرفر Render
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', (
            "scale=1080:1920:flags=lanczos,"  # دقة تيك توك المثالية
            "unsharp=5:5:1.5:5:5:1.5,"        # حدة الكريستال (Sharpness)
            "eq=saturation=1.6:contrast=1.2," # تلوين ببجي المشبع
            "fps=60"                          # سلاسة 60 فريم
        ),
        '-c:v', 'libx264', 
        '-crf', '20',             # جودة عالية جداً
        '-preset', 'ultrafast',   # سرعة قصوى لتجنب الـ Timeout
        '-pix_fmt', 'yuv420p',
        output_path
    ]

    try:
        # تنفيذ المعالجة
        subprocess.run(command, check=True)
        
        await status_msg.edit_text("✅ تمت المعالجة بنجاح! جاري رفع المقطع الكريستالي...")
        
        # الرفع كملف (Document) لضمان الجودة الأصلية
        await client.send_document(
            chat_id=message.chat.id,
            document=output_path,
            caption="💎 **تم تجهيز جودة الكريستال**\n🎬 الدقة: 1080x1920\n⚡️ الفريمات: 60fps"
        )
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ أثناء المعالجة: {e}")
    finally:
        # تنظيف الذاكرة وحذف الملفات المؤقتة
        if input_path and os.path.exists(input_path): os.remove(input_path)
        if output_path and os.path.exists(output_path): os.remove(output_path)
        await status_msg.delete()

if __name__ == '__main__':
    # تشغيل سيرفر الـ Health Check في الخلفية
    threading.Thread(target=run_health_check, daemon=True).start()
    
    print("البوت الاحترافي يعمل الآن...")
    app.run()
