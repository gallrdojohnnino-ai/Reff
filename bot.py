import os, json, time, random, string
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ================= CONFIG =================
BOT_TOKEN = "7890866670:AAHgKWAQzNlkBubvKN5xnTz0PDE2uHnHOTk"
ADMIN_ID = 8572625619

BOT_NAME = "Kcv Searcher V1.1"
BOT_CREDIT = "🤖 bot Created by : @Diabloshd"

CHANNEL = "@newbutrealchannel"
DISCUSSION = "@oldbutreal"
ANNOUNCE_CHANNEL = "https://t.me/forannbotko"

GCASH_NAME = "J M"
GCASH_NUMBER = "09569518135"
GCASH_NOTE = "Wag Kang Mag Fake Ret At Wag Niyo Din SmS Number Ko"

DB_FILE = "database.txt"
DATA_FILE = "data.json"
KEY_FILE = "keys.json"
SPEED_FILE = "speed.json"
BAN_FILE = "ban.json"

POINTS_REQUIRED = 10

DOMAINS = [
    "100082","authgop","mtacc","garena","roblox","gaslite",
    "mobilelegends","pubg","codashop","facebook","instagram",
    "netflix","tiktok","telegram","freefire","bloodstrike",
    "spotify","discord","steam","origin","epicgames","twitch"
]

# ================= HELPERS =================
def jload(f, d):
    if not os.path.exists(f):
        with open(f, "w") as w:
            json.dump(d, w)
    return json.load(open(f))

def jsave(f, d):
    json.dump(d, open(f, "w"), indent=2)

def gen_key():
    return "KCV-" + "".join(random.choices(string.ascii_uppercase+string.digits, k=12))

def now():
    return datetime.now()

# ================= START / WELCOME =================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    name = update.effective_user.first_name

    data = jload(DATA_FILE, {"users":{}})
    ban = jload(BAN_FILE, [])

    if uid in ban:
        return await update.message.reply_text("🚫 You are banned.")

    ref = ctx.args[0] if ctx.args else None

    if uid not in data["users"]:
        data["users"][uid] = {
            "points": 0,
            "premium": False,
            "referred_by": None,
            "role": "user"
        }

        if ref and ref != uid and ref in data["users"]:
            data["users"][ref]["points"] += 1

            if data["users"][ref]["points"] == 9:
                await ctx.bot.send_message(int(ref),
                    "🔔 Almost there!\n9/10 points — invite 1 more to unlock PREMIUM!")

            if data["users"][ref]["points"] >= POINTS_REQUIRED:
                data["users"][ref]["premium"] = True
                await ctx.bot.send_message(int(ref),
                    "🎉 PREMIUM UNLOCKED via referrals!")

            data["users"][uid]["referred_by"] = ref

    jsave(DATA_FILE, data)

    kb = [
        [InlineKeyboardButton("🆓 FREE ACCESS", callback_data="FREE")],
        [InlineKeyboardButton("💎 PREMIUM ACCESS", callback_data="PREMIUM")]
    ]

    await update.message.reply_text(
f"""📢 WELCOME TO {BOT_NAME}
━━━━━━━━━━━━━━━━━━━
✔ Accurate & fast
✔ Indexed (walang lag)
✔ Real TXT generator
✔ Referral unlock system

👤 User: {name}
🆔 ID: {uid}

Choose your access 👇
""",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= CHOICE =================
async def choice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)

    data = jload(DATA_FILE, {"users":{}})
    u = data["users"][uid]

    if q.data == "FREE":
        await q.edit_message_text(
f"""🆓 FREE ACCESS
━━━━━━━━━━━━━━━━━━━
🔗 Referral link:
https://t.me/{ctx.bot.username}?start={uid}

⭐ Points: {u['points']} / {POINTS_REQUIRED}
🔓 Unlock premium at 10 points

{BOT_CREDIT}
"""
        )

    elif q.data == "PREMIUM":
        if u["premium"]:
            await q.edit_message_text(
f"""💎 PREMIUM ACTIVE
━━━━━━━━━━━━━━━━━━━
⚡ Ultra-fast indexed search
📄 Unlimited TXT export

Use /search <domain>

{BOT_CREDIT}
"""
            )
        else:
            await q.edit_message_text(
f"""💎 PREMIUM ACCESS
━━━━━━━━━━━━━━━━━━━
⭐ Points: {u['points']} / {POINTS_REQUIRED}

💳 GCASH ONLY
👤 {GCASH_NAME}
📞 {GCASH_NUMBER}
📝 {GCASH_NOTE}

📸 Send screenshot after payment
"""
            )

# ================= DOMAINS =================
async def domains(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.args:
        arg = ctx.args[0].lower()
        if arg == "top":
            await update.message.reply_text(
                "🏆 TOP 5 BIGGEST DOMAINS\n━━━━━━━━━━━━━━━━━━━\n" +
                "\n".join(DOMAINS[:5])
            )
        elif arg in DOMAINS:
            await update.message.reply_text(f"✔ Domain available: {arg}")
        else:
            await update.message.reply_text("❌ Domain not indexed")
    else:
        await update.message.reply_text(
            "📊 AVAILABLE DOMAINS\n━━━━━━━━━━━━━━━━━━━\n" +
            "\n".join(DOMAINS)
        )

# ================= SEARCH =================
async def search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = jload(DATA_FILE, {"users":{}})

    if not data["users"].get(uid,{}).get("premium"):
        return await update.message.reply_text("🔐 Premium required.")

    if not ctx.args:
        return await update.message.reply_text("Usage: /search facebook")

    domain = ctx.args[0].lower()
    if domain not in DOMAINS:
        return await update.message.reply_text("❌ Domain not indexed")

    if not os.path.exists(DB_FILE):
        return await update.message.reply_text("❌ database.txt missing")

    start_t = time.time()
    results = []

    with open(DB_FILE, errors="ignore") as f:
        for line in f:
            if domain in line.lower():
                results.append(line.strip())

    if not results:
        return await update.message.reply_text("❌ No results found")

    took = time.time() - start_t
    out = f"Kcv_{uid}.txt"

    with open(out, "w") as w:
        w.write(f"# UID:{uid}\n")
        w.write("\n".join(results))

    speed = jload(SPEED_FILE,{})
    speed[uid] = took
    jsave(SPEED_FILE,speed)

    await update.message.reply_document(
        document=open(out,"rb"),
        caption=f"⚡ Generated in {took:.2f}s\n{BOT_CREDIT}"
    )
    os.remove(out)

# ================= LEADERBOARD =================
async def leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = jload(DATA_FILE, {"users":{}})
    top = sorted(
        data["users"].items(),
        key=lambda x: x[1]["points"],
        reverse=True
    )[:5]

    text = "📊 REFERRAL LEADERBOARD\n━━━━━━━━━━━━━━━━━━━\n"
    for i,(uid,u) in enumerate(top,1):
        text += f"{i}. {uid} — {u['points']} pts\n"

    await update.message.reply_text(text)

# ================= KEY SYSTEM =================
async def genkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = jload(DATA_FILE, {"users":{}})

    if uid not in data["users"] or data["users"][uid]["role"] not in ("admin","reseller"):
        return

    days = int(ctx.args[0])
    key = gen_key()
    keys = jload(KEY_FILE,{})
    keys[key] = {"days":days,"used":False}
    jsave(KEY_FILE,keys)

    await update.message.reply_text(f"🔐 KEY GENERATED:\n{key}\n⏳ {days} days")

async def redeem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    key = ctx.args[0]

    keys = jload(KEY_FILE,{})
    data = jload(DATA_FILE, {"users":{}})

    if key not in keys or keys[key]["used"]:
        return await update.message.reply_text("❌ Invalid key")

    data["users"][uid]["premium"] = True
    keys[key]["used"] = True

    jsave(KEY_FILE,keys)
    jsave(DATA_FILE,data)

    await update.message.reply_text("✅ PREMIUM ACTIVATED via KEY")

# ================= DAILY ANNOUNCER =================
async def daily_announcer(app):
    while True:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, errors="ignore") as f:
                lines = sum(1 for _ in f)
            await app.bot.send_message(
                ANNOUNCE_CHANNEL,
f"""📢 NEW ROWS INSERTED!
━━━━━━━━━━━━━━━━━━━
📊 Lines: {lines}
🌐 Unique Domains: {len(DOMAINS)}
📅 Added: {now().date()}
💠 Status: Ready to search!
📤 Export available.
"""
            )

        data = jload(DATA_FILE, {"users":{}})
        if data["users"]:
            top = max(data["users"].items(), key=lambda x: x[1]["points"])
            await app.bot.send_message(
                ANNOUNCE_CHANNEL,
                f"🏆 DAILY TOP REFERRER\nUser: {top[0]}\nPoints: {top[1]['points']}"
            )

        time.sleep(86400)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choice))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("domains", domains))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(MessageHandler(filters.PHOTO,
        lambda u,c: u.message.reply_text("📸 Screenshot received. Waiting for admin.")))

    app.create_task(daily_announcer(app))

    print("✅ Kcv Searcher V1.1 running…")
    app.run_polling()

if __name__ == "__main__":
    main()