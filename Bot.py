from iqoptionapi.stable_api import IQ_Option
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import time
import asyncio

# --- Configurações da IQ Option ---
email = 'robsonrsn88@gmail.com'
senha = 'Balta13082007@'
iqoption = IQ_Option(email, senha)
iqoption.connect()

# Verifica conexão com a IQ Option
if iqoption.check_connect():
    print("✅ Conectado com sucesso à IQ Option (Conta Demo).")
else:
    print("❌ Erro ao conectar à IQ Option.")

# --- Configurações do Telegram ---
TELEGRAM_BOT_TOKEN = '7734455409:AAEJGYpNGnYp6kZxav31rNKUy5TzYd6AyJQ'
bot_ativo = True

# Criação do teclado com botões
def menu_principal():
    teclado = [
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("🚀 Operar", callback_data='operar')],
        [InlineKeyboardButton("⏸️ Pausar", callback_data='pausar')],
        [InlineKeyboardButton("▶️ Retomar", callback_data='retomar')]
    ]
    return InlineKeyboardMarkup(teclado)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('🤖 Bot de Trading Iniciado!', reply_markup=menu_principal())

# Função para tratar botões
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_ativo
    query = update.callback_query
    await query.answer()

    if query.data == 'status':
        status_msg = "✅ ATIVO!" if bot_ativo else "⏸️ PAUSADO."
        await query.edit_message_text(status_msg, reply_markup=menu_principal())

    elif query.data == 'pausar':
        bot_ativo = False
        await query.edit_message_text("⏸️ Bot PAUSADO.", reply_markup=menu_principal())

    elif query.data == 'retomar':
        bot_ativo = True
        await query.edit_message_text("▶️ Bot RETOMADO.", reply_markup=menu_principal())

    elif query.data == 'operar':
        if not bot_ativo:
            await query.edit_message_text("⏸️ O bot está PAUSADO.", reply_markup=menu_principal())
            return
        await realizar_operacao(query)

# Operação na IQ Option
async def realizar_operacao(query):
    par_moeda = "EURUSD"
    valor = 1
    direcao = "call"
    tempo_expiracao = 1

    await query.edit_message_text("🚀 Abrindo operação...", reply_markup=menu_principal())

    try:
        status, id_operacao = iqoption.buy(valor, par_moeda, direcao, tempo_expiracao)
        if status:
            await query.edit_message_text(f"✅ Operação aberta! ID: {id_operacao}", reply_markup=menu_principal())
        else:
            await query.edit_message_text("❌ Falha ao abrir operação.", reply_markup=menu_principal())
            return

        # Verificar resultado da operação
        while True:
            status, lucro = iqoption.check_win_v3(id_operacao)
            if status:
                if lucro > 0:
                    await query.edit_message_text(f"💰 LUCRO: ${lucro}", reply_markup=menu_principal())
                else:
                    await query.edit_message_text(f"❌ PREJUÍZO: ${lucro}", reply_markup=menu_principal())
                break
            time.sleep(1)

    except Exception as e:
        await query.edit_message_text(f"⚠️ Erro: {e}", reply_markup=menu_principal())

# Inicialização do Bot
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Bot rodando no Railway!")
    await app.run_polling()

# Executar o bot
import asyncio
asyncio.run(main())
