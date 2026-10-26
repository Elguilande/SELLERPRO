import os
from telethon import TelegramClient, events

# --- Suas Credenciais do Telegram ---
API_ID = 34534392
API_HASH = 'c44894644c4a3bc887bb43b8b807cbb3'
SUA_DM_ID = 8498052187
BOT_TOKEN = '8968223957:AAGz9NCnCiwuSXO-6-JycODSRdgMp9UgkoY'

# Inicializa o cliente do Bot com arquivo de sessão local
bot = TelegramClient('bot_gestor', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dicionário dinâmico para monitorar múltiplos usuários em múltiplos grupos
membros_aguardando = {}

# --- PASSO 1: Detetar novo membro em qualquer grupo ---
@bot.on(events.ChatAction)
async def boas_vindas(event):
    if event.user_joined or event.user_added:
        # Obtém os detalhes do grupo onde o evento ocorreu
        chat = await event.get_chat()
        nome_grupo = chat.title
        
        for user in event.users:
            # Salva o utilizador e a origem do grupo no dicionário
            membros_aguardando[user.id] = {
                "grupo_id": event.chat_id,
                "grupo_nome": nome_grupo
            }
            
            # Mensagem automática de boas-vindas com instruções
            mensagem_instrucao = (
                f"Olá, {user.first_name}! 👋\n\n"
                f"Bem-vindo ao **{nome_grupo}**.\n"
                "Para concluir o seu acesso, por favor **envie aqui no grupo os prints de confirmação e o pacote**."
            )
            await event.reply(mensagem_instrucao)

# --- PASSO 2: Capturar mídias enviados pelos novos membros e alertar a sua DM ---
@bot.on(events.NewMessage)
async def monitorar_resposta(event):
    remetente_id = event.sender_id
    
    # Verifica se a mensagem pertence a alguém aguardando envio
    if remetente_id in membros_aguardando:
        # Verifica se o membro enviou o print (foto) ou pacote (documento/arquivo)
        if event.photo or event.document:
            user = await event.get_sender()
            nome_usuario = user.first_name if user.first_name else "Membro"
            username = f"@{user.username}" if user.username else "Sem username"
            
            # Recupera as informações do grupo de onde o utilizador veio
            info_grupo = membros_aguardando[remetente_id]
            
            # Constrói o alerta detalhado para a sua DM
            alerta_texto = (
                f"🚨 **Novo comprovativo recebido!**\n\n"
                f"👥 **Grupo:** {info_grupo['grupo_nome']}\n"
                f"👤 **Nome:** {nome_usuario}\n"
                f"🆔 **User:** {username}\n"
                f"🔢 **ID do Usuário:** {remetente_id}"
            )
            
            # Envia o alerta de texto para a sua DM
            await bot.send_message(SUA_DM_ID, alerta_texto)
            
            # Encaminha a foto/arquivo original diretamente para a sua DM
            await bot.forward_messages(SUA_DM_ID, event.message)
            
            # Remove o membro do monitoramento para não duplicar alertas futuros no mesmo envio
            membros_aguardando.pop(remetente_id, None)
            
            # Confirmação visual no grupo para o usuário saber que foi recebido
            await event.reply("Obrigado! Os seus dados foram recebidos e enviados para análise. 👍")

print("⚡ Bot iniciado com sucesso!")
print("📌 Monitorando múltiplos grupos e configurado para enviar alertas na sua DM.")
bot.run_until_disconnected()
