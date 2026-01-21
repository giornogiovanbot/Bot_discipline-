from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
app = ApplicationBuilder().token(8288046195:AAFOlPFymRNJCyxgL5hE6XC4WdBiNitEYDQ).build()
app.run_polling()
# ========= CONFIG =========
TOKEN = "8288046195:AAFOlPFymRNJCyxgL5hE6XC4WdBiNitEYDQ"

MISE_FIXE = 2000
MISE_ULTRA = 500
MAX_ULTRA_SEMAINE = 2

# ========= STOCKAGE =========
daily_bet = {}
loss_streak = {}
ultra_week = {}
analysis_score = {}

# ========= OUTILS =========
def semaine_actuelle():
    return datetime.date.today().isocalendar()[1]

def score_fiabilite(forme, buts, h2h, cartons, corners, winrate):
    score = (
        forme * 0.30 +
        buts * 0.25 +
        h2h * 0.15 +
        cartons * 0.10 +
        corners * 0.10 +
        winrate * 0.10
    )
    return round(score, 1)

# ========= COMMANDES =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BET-DISCIPLINE PRO BOT ACTIVÉ\n\n"
        "RÈGLES :\n"
        "• Analyse obligatoire\n"
        "• 1 pari / jour\n"
        "• Ultra x50 : 2×/semaine\n"
        "• 2 pertes = blocage\n\n"
        "Commandes :\n"
        "/analyse\n"
        "/parier\n"
        "/ultra\n"
        "/resultat GAGNÉ | PERDU\n"
        "/etat"
    )

# ========= ANALYSE =========
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 ANALYSE MATCH\n\n"
        "Réponds avec CES 6 NOTES (0 à 100) séparées par des espaces :\n\n"
        "1️⃣ Forme (5 derniers matchs)\n"
        "2️⃣ Buts marqués/encaissés\n"
        "3️⃣ Confrontations directes (H2H)\n"
        "4️⃣ Discipline (cartons)\n"
        "5️⃣ Corners\n"
        "6️⃣ % de victoires\n\n"
        "Exemple :\n"
        "75 70 60 65 68 72"
    )

async def analyse_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    try:
        data = list(map(int, context.args))
        if len(data) != 6:
            raise ValueError
    except:
        await update.message.reply_text("❌ Format invalide. 6 nombres requis.")
        return

    score = score_fiabilite(
        forme=data[0],
        buts=data[1],
        h2h=data[2],
        cartons=data[3],
        corners=data[4],
        winrate=data[5]
    )

    analysis_score[user] = score

    if score < 60:
        decision = "❌ PARI REFUSÉ"
    elif score < 70:
        decision = "⚠️ PRUDENCE EXTRÊME"
    else:
        decision = "✅ PARI AUTORISÉ"

    await update.message.reply_text(
        f"📊 SCORE DE FIABILITÉ : {score}/100\n\n{decision}"
    )

# ========= PARI NORMAL =========
async def parier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    today = str(datetime.date.today())

    if analysis_score.get(user, 0) < 70:
        await update.message.reply_text("⛔ Analyse insuffisante. Pari interdit.")
        return

    if loss_streak.get(user, 0) >= 2:
        await update.message.reply_text("⛔ 2 pertes consécutives. Pause obligatoire.")
        return

    if daily_bet.get(user) == today:
        await update.message.reply_text("❌ Déjà parié aujourd’hui.")
        return

    daily_bet[user] = today
    await update.message.reply_text(
        f"✅ PARI NORMAL AUTORISÉ\n"
        f"Mise : {MISE_FIXE} FCFA"
    )

# ========= ULTRA =========
async def ultra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    week = semaine_actuelle()
    today = str(datetime.date.today())

    if analysis_score.get(user, 0) < 70:
        await update.message.reply_text("⛔ Analyse insuffisante pour un ultra.")
        return

    if loss_streak.get(user, 0) >= 2:
        await update.message.reply_text("⛔ Trop de pertes. Ultra bloqué.")
        return

    if daily_bet.get(user) == today:
        await update.message.reply_text("❌ Déjà un pari aujourd’hui.")
        return

    count = ultra_week.get((user, week), 0)
    if count >= MAX_ULTRA_SEMAINE:
        await update.message.reply_text("❌ Limite ultra hebdomadaire atteinte.")
        return

    ultra_week[(user, week)] = count + 1
    daily_bet[user] = today

    await update.message.reply_text(
        f"🔥 ULTRA GROS COUP AUTORISÉ\n\n"
        f"Mise : {MISE_ULTRA} FCFA\n"
        f"Cote max : x50\n\n"
        "⚠️ Fun contrôlé, pas de rattrapage."
    )

# ========= RÉSULTAT =========
async def resultat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Utilise : /resultat GAGNÉ | PERDU")
        return

    res = context.args[0].upper()

    if res == "PERDU":
        loss_streak[user] = loss_streak.get(user, 0) + 1
        await update.message.reply_text(
            f"❌ Pari perdu\nPertes consécutives : {loss_streak[user]}"
        )
    elif res == "GAGNÉ":
        loss_streak[user] = 0
        await update.message.reply_text("✅ Pari gagné. Discipline maintenue.")
    else:
        await update.message.reply_text("Résultat invalide.")

# ========= ÉTAT =========
async def etat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    week = semaine_actuelle()
    ultra_used = ultra_week.get((user, week), 0)

    await update.message.reply_text(
        "📊 ÉTAT DISCIPLINE\n\n"
        f"Score analyse : {analysis_score.get(user,0)}/100\n"
        f"Pertes consécutives : {loss_streak.get(user,0)}\n"
        f"Ultra utilisés : {ultra_used}/2\n"
        f"Mise normale : {MISE_FIXE} FCFA\n"
        f"Mise ultra : {MISE_ULTRA} FCFA"
    )

# ========= LANCEMENT =========
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyse", analyse))
app.add_handler(CommandHandler("note", analyse_result))
app.add_handler(CommandHandler("parier", parier))
app.add_handler(CommandHandler("ultra", ultra))
app.add_handler(CommandHandler("resultat", resultat))
app.add_handler(CommandHandler("etat", etat))

app.run_polling()
