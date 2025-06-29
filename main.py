import pyrogram
from pyrogram import Client, filters, idle
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, ChatWriteForbidden, UserNotParticipant
import time
import os
import threading
import json
import asyncio

with open('config.json', 'r') as f: DATA = json.load(f)
def getenv(var): return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN") 
MUST_JOIN = getenv("MUST_JOIN")
api_hash = getenv("HASH") 
api_id = getenv("ID")

bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
ss = getenv("STRING")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

# download status
def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

def subcribe(func):
    def wrapper(_, message: Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
        if not MUST_JOIN:  # Not compulsory
            return
        try:
            try:
                bot.get_chat_member(MUST_JOIN, message.from_user.id)
            except UserNotParticipant:
                if MUST_JOIN.isalpha():
                    yuhu = "https://t.me/" + MUST_JOIN
                else:
                    chat_info = bot.get_chat(MUST_JOIN)
                    yuhu = chat_info.invite_link
                try:
                    message.reply(
                        f"**Hallo {rpk}. Agar Bisa Menggunakan Bot Anda Harus Masuk Ke Channel Terlebih Dahulu!. Silahkan Klik Tombol Di Bawah Untuk Join.**",
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("Join Channel", url=yuhu)]]
                        ),
                    )
                    message.stop_propagation()
                except ChatWriteForbidden:
                    pass
        except ChatAdminRequired:
            message.reply(
                f"Saya bukan admin di chat MUST_JOIN chat : {MUST_JOIN} !"
            )
        return func(_, message)
    return wrapper

# display bot name

# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(message.chat.id, f"{USAGE}")

@bot.on_message(filters.command("restart"))
def restart(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    try:
        bot.send_message(message.chat.id, "✅ restarted...")
        os.system(f"kill -9 {os.getpid()} && python3 main.py")
    except Exception as e:
        bot.send_message(message.chat.id, str(e))

@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

        if acc is None:
            bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            try: acc.join_chat(message.text)
            except Exception as e: 
                bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Chat already Joined**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)

    # getting message
    elif "https://t.me/" in message.text:

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try: toID = int(temp[1].strip())
        except: toID = fromID

        for msgid in range(fromID, toID + 1):

            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                
                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                
                handle_private(message, chatid, msgid)
                # try: handle_private(message, chatid, msgid)
                # except Exception as e: bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
            
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                
                if acc is None:
                    bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                try: handle_private(message, username, msgid)
                except Exception as e: bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # public
            else:
                username = datas[3]

                try: msg  = bot.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    bot.send_message(message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                    return

                try: bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    if acc is None:
                        bot.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                        return
                    try: handle_private(message, username, msgid)
                    except Exception as e: bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # wait time
            time.sleep(3)

# handle private
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
    msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)

    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    dosta = threading.Thread(target=lambda: downstatus(f'{message.id}downstatus.txt', smsg), daemon=True)
    dosta.start()
    file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    os.remove(f'{message.id}downstatus.txt')

    upsta = threading.Thread(target=lambda: upstatus(f'{message.id}upstatus.txt', smsg), daemon=True)
    upsta.start()
    
    if "Document" == msg_type:
        try:
            thumb = acc.download_media(msg.document.thumbs[0].file_id)
        except: thumb = None
        
        bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        if thumb != None: os.remove(thumb)

    elif "Video" == msg_type:
        try: 
            thumb = acc.download_media(msg.video.thumbs[0].file_id)
        except: thumb = None

        bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        if thumb != None: os.remove(thumb)

    elif "Animation" == msg_type:
        bot.send_animation(message.chat.id, file, reply_to_message_id=message.id)
        
    elif "Sticker" == msg_type:
        bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

    elif "Voice" == msg_type:
        bot.send_voice(message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

    elif "Audio" == msg_type:
        try:
            thumb = acc.download_media(msg.audio.thumbs[0].file_id)
        except: thumb = None
            
        bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])   
        if thumb != None: os.remove(thumb)

    elif "Photo" == msg_type:
        bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id)

    os.remove(file)
    if os.path.exists(f'{message.id}upstatus.txt'): os.remove(f'{message.id}upstatus.txt')
    bot.delete_messages(message.chat.id, [smsg.id])

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except: pass

    try:
        msg.video.file_id
        return "Video"
    except: pass

    try:
        msg.animation.file_id
        return "Animation"
    except: pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except: pass

    try:
        msg.voice.file_id
        return "Voice"
    except: pass

    try:
        msg.audio.file_id
        return "Audio"
    except: pass

    try:
        msg.photo.file_id
        return "Photo"
    except: pass

    try:
        msg.text
        return "Text"
    except: pass

USAGE = """
🚀 Halo aku bot save konten silahkan kirim link konten nya, pastikan akun mu join di grup/channel Tersebut.


<b>Media dari Bot</b>

kirim tautan dengan '/b/', nama pengguna bot dan id pesan

https://t.me/b/botusername/4321


<b>Batch Download/Download sekaligus</b>

kirim link postingan publik/pribadi seperti yang dijelaskan di atas dengan format "dari - ke" untuk mengirim banyak pesan seperti di bawah

https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
"""



bot.run()
