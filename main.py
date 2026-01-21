from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
import os

# ================== CONFIG ==================
MISE_FIXE = 2000
MISE_ULTRA = 500
MAX_ULTRA_SEMAINE = 2
TOKEN = os.environ.get.8288046195:AAH10NXXR2Nx9NESeFKv1AtFyy-K-h-4NL4

# ================== DONNÉES ==================
daily_bet = {}
loss_streak = {}
ultra_week = {}

# ================== OUTILS ==================
def semaine_actuelle():
    return datetime.date.today().isocalendar()[1]

# ================== COMMANDES ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BET-DISCIPLINE BOT ACTIVÉ\n\n"
        "MODES :\n"
        "• Normal : 1 pari / jour\n"
        "• Ultra : 2 fois / semaine (x50 max)\n\n"
        "Commandes :\n"
        "/parier\n"
        "/ultra\n"
        "/resultat GAGNÉ | PERDU\n"
        "/etat"
    )

async def parier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    today = str(datetime.date.today())

    if loss_streak.get(user, 0) >= 2:
        await update.message.reply_text("⛔ Discipline active : 2 pertes consécutives.")
        return

    if daily_bet.get(user) == today:
        await update.message.reply_text("❌ Tu as déjà parié aujourd’hui.")
        return

    daily_bet[user] = today
    await update.message.reply_text(
        f"✅ PARI NORMAL AUTORISÉ\n"
        f"Mise : {MISE_FIXE} FCFA\n"
        "Reste calme."
    )

async def ultra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    week = semaine_actuelle()
    today = str(datetime.date.today())

    if loss_streak.get(user, 0) >= 2:
        await update.message.reply_text("⛔ Ultra bloqué : trop de pertes.")
        return

    if daily_bet.get(user) == today:
        await update.message.reply_text("❌ Déjà un pari aujourd’hui.")
        return

    count = ultra_week.get((user, week), 0)
    if count >= MAX_ULTRA_SEMAINE:
        await update.message.reply_text("❌ Limite ultra atteinte cette semaine.")
        return

    ultra_week[(user, week)] = count + 1
    daily_bet[user] = today

    await update.message.reply_text(
        f"🔥 ULTRA GROS COUP AUTORISÉ\n\n"
        f"Mise : {MISE_ULTRA} FCFA\n"
        f"Cote max : x50\n\n"
        "⚠️ Fun contrôlé. Pas de rattrapage."
    )

async def resultat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Utilise : /resultat GAGNÉ ou PERDU")
        return

    res = context.args[0].upper()

    if res == "PERDU":
        loss_streak[user] = loss_streak.get(user, 0) + 1
        await update.message.reply_text(
            f"❌ Pari perdu\nPertes consécutives : {loss_streak[user]}"
        )
    elif res == "GAGNÉ":
        loss_streak[user] = 0
        await update.message.reply_text("✅ Pari gagné. Discipline respectée.")
    else:
        await update.message.reply_text("Résultat invalide.")

async def etat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    week = semaine_actuelle()
    ultra_count = ultra_week.get((user, week), 0)

    await update.message.reply_text(
        "📊 ÉTAT DISCIPLINE\n\n"
        f"Pertes consécutives : {loss_streak.get(user, 0)}\n"
        f"Ultra utilisés cette semaine : {ultra_count}/2\n"
        f"Mise normale : {MISE_FIXE} FCFA\n"
        f"Mise ultra : {MISE_ULTRA} FCFA"
    )

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("parier", parier))
    app.add_handler(CommandHandler("ultra", ultra))
    app.add_handler(CommandHandler("resultat", resultat))
    app.add_handler(CommandHandler("etat", etat))
    app.run_polling()

if __name__ == "__main__":
    main()