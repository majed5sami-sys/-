import discord
from discord.ext import commands
import datetime
import asyncio
from easy_pil import Canvas, Editor, Font, LoadUrl
from flask import Flask
from threading import Thread

# ==========================================
# 0. إعداد سيرفر Flask للاستضافة على Render
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==========================================
# 1. إعدادات البوت والـ Intents
# ==========================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.moderation = True

bot = commands.Bot(command_prefix='', intents=intents) # بدون بادئة

# متغيرات الإعدادات والروابط (سيتم تحديثها تلقائياً عند تشغيل أمر 'لوق')
CONFIG = {
    'TOKEN': 'MTUzMjUxNDQ1OTcxNTc2ODQxMA.GiXqxX.E3HbFrnLFq-B5hSBvz8OSC5wIvJWAFMM6wntRE',
    'AUTO_ROLE_ID': None,
    'WELCOME_CHANNEL_ID': None,
    'TEXT_LOG_CHANNEL': None,
    'VOICE_LOG_CHANNEL': None,
    'SECURITY_LOG_CHANNEL': None,
    'ALLOWED_ROLES': [],  # أيديات الرتب المسموح لها بالحذف والتعديل
    'RIGHTS_FOOTER': 'Developed with Majed  ❤️ 
}

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح كـ: {bot.user.name}')

# ==========================================
# 2. أمر إنشاء رومات اللوقات تلقائياً (امر لوق)
# ==========================================
@bot.command(name='لوق')
@commands.has_permissions(administrator=True)
async def create_logs(ctx):
    guild = ctx.guild
    await ctx.send("⏳ جاري إنشاء كCategory ورومات اللوقات تلقائياً...")

    # إنشاء كاتجوري خاص باللوقات
    category = await guild.create_category("📋-سجلات-البوت")

    # إنشاء الرومات
    welcome_ch = await guild.create_text_channel("👋-الترحيب", category=category)
    text_log_ch = await guild.create_text_channel("💬-لوق-الشات", category=category)
    voice_log_ch = await guild.create_text_channel("🔊-لوق-الفويس", category=category)
    security_log_ch = await guild.create_text_channel("🚨-لوق-الحماية", category=category)

    # حفظ الأيديات في الإعدادات
    CONFIG['WELCOME_CHANNEL_ID'] = welcome_ch.id
    CONFIG['TEXT_LOG_CHANNEL'] = text_log_ch.id
    CONFIG['VOICE_LOG_CHANNEL'] = voice_log_ch.id
    CONFIG['SECURITY_LOG_CHANNEL'] = security_log_ch.id

    embed = discord.Embed(
        title="✅ تم إنشاء رومات اللوقات بنجاح!",
        description="تم إنشاء الفئة والرومات التالية وربطها بالبوت تلقائياً:",
        color=discord.Color.green()
    )
    embed.add_field(name="روم الترحيب:", value=welcome_ch.mention, inline=False)
    embed.add_field(name="لوق الشات:", value=text_log_ch.mention, inline=False)
    embed.add_field(name="لوق الفويس:", value=voice_log_ch.mention, inline=False)
    embed.add_field(name="لوق الحماية:", value=security_log_ch.mention, inline=False)
    embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])

    await ctx.send(embed=embed)

# ==========================================
# 3. أمر عرض الأوامر (امر اوامر)
# ==========================================
@bot.command(name='اوامر')
async def show_commands(ctx):
    embed = discord.Embed(
        title="📜 قائمة أوامر البوت الإدارية والحماية",
        color=discord.Color.blue()
    )
    embed.add_field(name="`لوق`", value="إنشاء رومات اللوقات تلقائياً وتفعيلها (للأدمن فقط)", inline=False)
    embed.add_field(name="`مسح [العدد]`", value="مسح عدد محدد من الرسائل في الروم", inline=False)
    embed.add_field(name="`بان @العضو [السبب]`", value="حظر عضو من السيرفر", inline=False)
    embed.add_field(name="`طرد @العضو [السبب]`", value="طرد عضو من السيرفر", inline=False)
    embed.add_field(name="`كتم @العضو [المدة]`", value="كتم عضو لمدة معينة بالدقائق", inline=False)
    embed.add_field(name="`فك_كتم @العضو`", value="إلغاء الكتم عن العضو", inline=False)
    embed.add_field(name="`قفل` / `فتح`", value="قفل أو فتح الكتابة في الروم الحالية", inline=False)
    embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])

    await ctx.send(embed=embed)

# ==========================================
# 4. الترحيب بالصورة والتصميم المضبوط
# ==========================================
@bot.event
async def on_member_join(member):
    # 1. إعطاء الرول التلقائي
    if CONFIG['AUTO_ROLE_ID']:
        role = member.guild.get_role(CONFIG['AUTO_ROLE_ID'])
        if role:
            try:
                await member.add_roles(role)
            except Exception as e:
                print(f"خطأ في إعطاء الرول: {e}")

    # 2. إنشاء بطاقة الترحيب
    if CONFIG['WELCOME_CHANNEL_ID']:
        channel = member.guild.get_channel(CONFIG['WELCOME_CHANNEL_ID'])
        if channel:
            try:
                # 1. تحميل صورة الخلفية الخاصة بك
                bg = Editor("welcome.png")

                # 2. جلب وتجهيز افتار العضو (حجم 235x235 ليطابق الدائرة)
                avatar_image = await LoadUrl(member.display_avatar.url)
                avatar = Editor(avatar_image).resize((235, 235)).circle_image()

                # 3. وضع الافتار بالضبط في منتصف الدائرة الإطار
                # الإحداثيات المحددة للدائرة: X=172, Y=172
                bg.paste(avatar, (172, 172))

                # 4. كتابة اسم اليوزر مكان @USERNAME
                # الإحداثيات المحددة لليوزر: المنتصف عند X=290, Y=752
                font = Font.poppins(size=32, bold=True)
                bg.text((290, 752), f"@{member.name}", color="#E0E0E0", font=font, align="center")

                # 5. تحويل الصورة وتصديرها
                file = discord.File(fp=bg.image_bytes, filename="welcome_card.png")

                # رسالة النص المرافقة (منشن)
                welcome_msg = f"يا هلا والله بـ {member.mention} 👋\nنورت السيرفر!"

                await channel.send(content=welcome_msg, file=file)

            except Exception as e:
                print(f"خطأ في معالجة صورة الترحيب: {e}")
# ==========================================
# 5. الحماية الفائقة (Anti-Delete)
# ==========================================
@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        executor = entry.user
        if executor.id == channel.guild.owner_id:
            return

        # فحص الرتب المسموح لها
        has_permission = any(role.id in CONFIG['ALLOWED_ROLES'] for role in executor.roles)
        if not has_permission:
            # 1. تصفير المخرب (سحب رتبه)
            try:
                await executor.edit(roles=[], reason="حماية: حذف روم بدون إذن")
            except:
                pass

            # 2. إعادة إنشاء الروم
            new_channel = await channel.clone(reason="إعادة إنشاء روم محذوف تلقائياً")

            # 3. إرسال لوق الحماية
            if CONFIG['SECURITY_LOG_CHANNEL']:
                sec_log = channel.guild.get_channel(CONFIG['SECURITY_LOG_CHANNEL'])
                if sec_log:
                    embed = discord.Embed(
                        title="🚨 خرق حماية - تم التصدي",
                        color=discord.Color.red(),
                        timestamp=datetime.datetime.utcnow()
                    )
                    embed.description = f"قام المخرب {executor.mention} (`{executor.id}`) بحذف روم."
                    embed.add_field(name="الإجراءات المتخذة:", value="• تم سحب جميع رتب المخرب (تصفير).\n• تم إعادة إنشاء الروم تلقائياً.")
                    embed.add_field(name="الروم الجديد:", value=new_channel.mention)
                    embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])
                    await sec_log.send(embed=embed)

# ==========================================
# 6. لوقات الصوت والحذف والأوامر الإدارية
# ==========================================
@bot.event
async def on_voice_state_update(member, before, after):
    if not CONFIG['VOICE_LOG_CHANNEL']:
        return
    log_channel = member.guild.get_channel(CONFIG['VOICE_LOG_CHANNEL'])
    if not log_channel:
        return

    # دخول
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(title="🔊 دخول روم صوتي", color=discord.Color.green())
        embed.description = f"دخل العضو {member.mention} إلى {after.channel.mention}"
        embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])
        await log_channel.send(embed=embed)

    # خروج / ديسكونكت
    elif before.channel is not None and after.channel is None:
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_disconnect):
            if entry.created_at > (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)):
                embed = discord.Embed(title="🚫 طرد من الصوت (Disconnect)", color=discord.Color.red())
                embed.description = f"قام {entry.user.mention} بطرد العضو {member.mention} من الروم {before.channel.mention}"
                embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])
                await log_channel.send(embed=embed)
                return

        embed = discord.Embed(title="🔇 خروج من روم صوتي", color=discord.Color.orange())
        embed.description = f"خرج العضو {member.mention} من {before.channel.mention}"
        embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])
        await log_channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot or not CONFIG['TEXT_LOG_CHANNEL']:
        return
    log_channel = message.guild.get_channel(CONFIG['TEXT_LOG_CHANNEL'])
    if not log_channel:
        return

    embed = discord.Embed(title="🗑️ تم حذف رسالة", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
    embed.add_field(name="صاحب الرسالة:", value=message.author.mention, inline=True)
    embed.add_field(name="الروم:", value=message.channel.mention, inline=True)
    embed.add_field(name="المحتوى:", value=message.content or "صورة/ملف", inline=False)
    embed.set_footer(text=CONFIG['RIGHTS_FOOTER'])
    await log_channel.send(embed=embed)

# الأوامر الإدارية العربية
@bot.command(name='مسح')
@commands.has_permissions(manage_messages=True)
async def clear_msgs(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 تم مسح {amount} رسالة.")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name='بان')
@commands.has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 تم حظر {member.mention} | السبب: {reason}")

@bot.command(name='طرد')
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await member.kick(reason=reason)
    await ctx.send(f"🚪 تم طرد {member.mention} | السبب: {reason}")

@bot.command(name='قفل')
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل الروم.")

@bot.command(name='فتح')
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح الروم.")

# تشغيل الويب والبوت
keep_alive()
bot.run(CONFIG['MTUzMjUxNDQ1OTcxNTc2ODQxMA.GiXqxX.E3HbFrnLFq-B5hSBvz8OSC5wIvJWAFMM6wntRE'])
