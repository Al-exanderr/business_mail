import requests
import telebot
import tempfile, zipfile


token = '505217823:AAH02w3sWfB4gFGWR03c8SFzfG_nNY_u_mg'  # токен бота Falcon
chat_id = '-1001416148489'


def send_message(text: str):
    url = "https://api.telegram.org/bot"
    url += token
    method = url + "/sendMessage"

    try:
        r = requests.post(method, data={"chat_id": chat_id, "text": text})
    except Exception as exc:
        print(type(exc), str(exc))
    # if r.status_code != 200:
    #    raise Exception("post_text error")
    #    print('snd tlgrm msg err')


def send_db_to_telegram():
    bot = telebot.TeleBot(token)
    tmp = tempfile.NamedTemporaryFile(delete=True)
    tmp.name = 'db.zip'
    with open(tmp.name, 'w'):
        zipObj = zipfile.ZipFile(tmp.name, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9)
        zipObj.write('db.sqlite3')
        zipObj.close()
    with open(tmp.name,"rb") as file:
        bot.send_document(chat_id,file.read())
