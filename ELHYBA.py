from mody import Mody
from kvsqlite.sync import Client
import string, random
from telebot import TeleBot as tb
from telebot.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
token = Mody.ELHYBA
bot = tb(token, num_threads=30, skip_pending=True)
db = Client("-.-")

@bot.channel_post_handler(content_types=["text"])
def process(message):
    
    if message.text == "انهاء":
        db.delete(f"r_{message.chat.id}")
        bot.reply_to(message, "تمت")
        return
    if message.text == "روليت":
        db.delete(f"r_{message.chat.id}")
        keys = mk().add(btn("بدء اللعبة", callback_data=f"start-{message.author_signature}"))
        bot.reply_to(message, "اهلا بيك ببوت الروليت", reply_markup=keys)
        return
        
@bot.callback_query_handler(func=lambda m:True)
def cals(call):
    cid, mid, fid, data= call.message.chat.id, call.message.id, call.from_user.id, call.data
    if data.startswith("start-"):
        id = data.split("-")[1]
        if call.from_user.first_name != id:
            return
        if db.get(f"r_{cid}"):
            bot.reply_to(message, "في روليت شغالة!!")
            return
        code = "".join(random.choice("Source_Ze") for i in range(6))
        keys = mk(row_width=1)
        btn1, btn2 = btn("انضمام للعبة", callback_data=f"join_{cid}"), btn("بدأ الاستبعاد", callback_data=f"kick_{cid}")
        keys.add(btn1, btn2)
        x = bot.edit_message_text(chat_id=cid, message_id=mid, text="بدأت لعبة الروليت\n", reply_markup=keys)
        db.set(f"r_{cid}", dict(is_start=False, code=code, chat_id=cid, users=[{"name":call.from_user.first_name, "id":fid}], owner=fid, mid=x.message_id))
        return
    if data.startswith("kick"):
        myb = data.split("_")[1]
        if db.exists(f"r_{int(myb)}"):
            d = db.get(f"r_{int(myb)}")
            if int(d["owner"]) == fid:
                if len(d["users"]) == 1:
                    d = db.get(f"r_{myb}")
                    p = d["users"][-1]
                    x = "انتهت الروليت !! وعدنا فائز!\n"
                    x+= f"الفائز: {p['name']}\n"
                    x+= "\nحظ اوفر للي ماتوفقوا :( "
                    bot.edit_message_text(chat_id=int(myb), message_id=d["mid"], text=x)
                    db.delete(f"r_{int(myb)}")
                    return
                x0= random.choice(d["users"])
                if x0:
                    d["users"].remove(x0)
                    if len(d["users"]) == 1:
                        d = db.get(f"r_{myb}")
                        p = d["users"][-1]
                        x = "انتهت الروليت !! وعدنا فائز!\n"
                        x+= f"الفائز: {p['name']}\n"
                        x+= "\nحظ اوفر للي ماتوفقوا :( "
                        bot.edit_message_text(chat_id=int(myb), message_id=d["mid"], text=x)
                        db.delete(f"r_{int(myb)}")
                        return
                    db.set(f"r_{int(myb)}", d)
                    x = "لعبة الروليت قد بدأت !\nاخر شخص يبقى راح يفوز!\n\nالاعبين:\n"
                    for i, y in enumerate(d["users"], 1):
                        name = y["name"]
                        x+=f"{i}. {name} .\n"
                    x+=f"\nتم استبعاد: {x0['name']} .\n"
                    keys = mk(row_width=1)
                    btn1, btn2 = btn("انضمام للعبة", callback_data=f"join_{cid}"), btn("بدأ الاستبعاد", callback_data=f"kick_{cid}")
                    keys.add(btn1, btn2)
                    bot.edit_message_text(chat_id=cid, message_id=d["mid"], text=x, reply_markup=keys)
                    return
            else:
                bot.answer_callback_query(call.id, "الزر خاص للمالك الذي بدأ اللعبة!", show_alert=True)
                
    if data.startswith("join"):
        myb = data.split("_")[1]
        if db.exists(f"r_{int(myb)}"):
            d = db.get(f"r_{int(myb)}")
            if len(d["users"]) == 5:
                d.update({"is_start":True})
                db.set(f"r_{int(myb)}", d)
                bot.answer_callback_query(call.id, "تعال باجر!", show_alert=True)
                return
            if d.get("is_start"):
                return
            for y in d["users"]:
                if fid == y["id"]:
                    bot.answer_callback_query(call.id, f"انت موجود باللعبة!", show_alert=True)
                    return
            d["users"].append(dict(name=call.from_user.first_name, id=fid))
            db.set(f"r_{int(myb)}", d)
            bot.answer_callback_query(call.id, f"تم اضافتك للعبة!", show_alert=True)
            x = "لعبة الروليت قد بدأت !\nاخر شخص يبقى راح يفوز!\n\nالاعبين:\n"
            for i, y in enumerate(d["users"], 1):
                name = y["name"]
                x+=f"{i}. {name} .\n"
            keys = mk(row_width=1)
            btn1, btn2 = btn("انضمام للعبة", callback_data=f"join_{cid}"), btn("بدأ الاستبعاد", callback_data=f"kick_{cid}")
            keys.add(btn1, btn2)
            bot.edit_message_text(chat_id=int(myb), message_id=d["mid"], text=x, reply_markup=keys)
            return
        
bot.infinity_polling()
            
