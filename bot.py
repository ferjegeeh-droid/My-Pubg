import os
import subprocess
import asyncio
import threading
import http.server
import socketserver
from pyrogram import Client, filters

# --- بياناتك الخاصة ---
API_ID = 34854054
API_HASH = "755af2664322b4e5054bb26b278092ac"
BOT_TOKEN = "8752935054:AAEmRFpDOK-tWQNlLzrsPyF-9HOkYseh3kI"

# إنشاء البوت
app = Client("crystal_pro_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# سيرفر وهمي لإبقاء Render مستيقظاً (Live)
def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "💎 **بوت جودة الكريستال (itsscale 4) جاهز!**\n\n"
        "🎬 **الإعدادات الحالية:**\n"
        "- الدقة: 2K (1440x2560) لخداع التيك توك.\n"
        "- الفريمات: 60fps ثابتة.\n"
        "- الفلتر: كريستال حاد + ألوان مشبعة.\n\n"
        "⚠️ **ملاحظة:** أرسل لقطات قصيرة (10-15 ثانية) لضمان أسرع معالجة."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message):
    media = message.video or message.document
    if not media: return

    # رسالة الحالة
    status_msg = await message.reply_text("📥 جاري سحب الفيديو ومعالجته بجودة 2K الكريستالية...")
    
    input_path = await client.download_media(message)
    output_path = f"crystal_{message.chat.id}.mp4"

    # --- الكود "السحري" لخداع التيك توك وجودة الكريستال ---
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', (
            "scale=1440:2560:flags=lanczos," # رفع الدقة لـ 2K لجلب أعلى Bitrate
            "unsharp=5:5:1.5:5:5:1.5,"       # فلتر الكريستال (itsscale 4)
            "eq=saturation=1.6:contrast=1.2:brightness=0.02," # تلوين ببجي الاحترافي
            "fps=60"                         # إجبار التيك توك على الـ 60 فريم
        ),
        '-c:v', 'libx264', 
        '-crf', '17',             # جودة فائقة جداً
        '-preset', 'ultrafast',   # سرعة قصوى لتناسب سيرفر Render
        '-maxrate', '15M',        # Bitrate عالي جداً للوضوح
        '-bufsize', '20M',
        '-pix_fmt', 'yuv420p',
        output_path
    ]

    try:
        # بدء عملية الرندر
        subprocess.run(command, check=True)
        
        await status_msg.edit_text("✅ تمت المعالجة بنجاح! جاري رفع المقطع...")
        
        # إرسال الملف كـ Document لضمان عدم ضياع أي بكسل
        await client.send_document(
            chat_id=message.chat.id,
            document=output_path,
            caption="🔥 **تم استخراج جودة الكريستال بنجاح!**\n🎬 الدقة: 2K (1440x2560)\n🚀 الفريمات: 60fps\n✨ جاهز للرفع على تيك توك"
        )
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ في الرندر: {e}\nتأكد أن الفيديو قصير.")
    finally:
        # تنظيف الملفات
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        await status_msg.delete()

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    print("Crystal Bot is Running...")
    app.run()
