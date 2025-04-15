import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.types import DirectMessage

USERNAME = "lynx_chod_hu"
PASSWORD = "babytingting"

ROAST_MESSAGES = [
    "bhai tu rehne de, tera IQ room temperature se bhi kam hai.",
    "jitni baar tu bolta hai, utni baar embarrassment hoti hai Indian education system ko.",
    "tera logic dekh ke calculator bhi suicide kar le.",
    "chal na, tujhme aur Google translate me zyada fark nahi.",
    "tu chup kar, warna tera browser history sabke saamne daal dunga.",
    "tera reply padke lagta hai ki evolution ne break le liya tha.",
    "teri soch ka GPS signal lost dikha raha hai.",
    "tu rehne de bhai, tere jaise logon ko autocorrect bhi ignore karta hai.",
    "tu zyada bolta hai, aur samajh kamta hai.",
    "beta tu abhi training wheels pe chal raha hai, formula 1 ke sapne mat dekh.",
    "bhaisahab, teri soch ko Google bhi dhoondh ke laane ki koshish kar raha hai.",
    "agar teri soch ka ek percentage bhi sahi hota, toh world ka scene alag hota.",
    "tu apni soch se zyada apni bandook ki safai karta hai.",
    "jitni der me tu sochta hai, usme hum 10 kaam kar lete hain.",
    "tere IQ level ko dekh ke, maine apni battery ko recharge karna band kar diya.",
    "tu chhupa ke baat karna seekh, warna baat baat pe challenge dene lagta hai.",
    "tere har sentence mein ek naya level of embarrassment hota hai.",
    "tera sarcasm humne meme mein daal diya hai.",
    "tu jab bolta hai, toh lagta hai speaker kharaab ho gaya hai.",
    "tu apne liye beizzati ka naya tareeka dhoondhta rehta hai.",
    "tera dimag internet ke outdated version ki tarah lagta hai.",
    "tere dimaag mein permanent buffer chal raha hai.",
    "mujhe lagta hai tu chatbot se zyada useless ho.",
    "tu shaadi ke liye nahi, apne doston ke beech beizzat hone ke liye bana hai.",
    "tera humour dictionary se nikal ke meme ka part ban gaya hai.",
    "tumhare jokes ko sun ke apne speakers bhi sharminda ho jaate hain.",
    "agar comedy competition hota, toh tu bhi entry ke liye waitlist pe hota.",
    "terin soch se zyada kehna wala tumhara ghar ka AC hai.",
    "tujhe apni apni zindagi ke decisions ko review karna chahiye.",
    "agar tu chess khelta toh 'losing' ko apni special move bana leta.",
    "tu khud ki tareef mein do line likh, usse jyada seekh bhi nahi milegi.",
    "apni soch ka low quality version poore duniya ko dekhata hai.",
    "tu ek self-made genius hai, jo apne brain ko khud se bhi banata hai.",
    "tu jese sochne wale logh ka naam record book mein likhna chahiye.",
    "aajkal ke samaj mein, hum logo ka status 'zero' dikhata hai.",
    "tu apne aap ko puri duniya ke sabse padhaiwaala insaan samajhta hai.",
    "tere sarcasm ki wajah se main bhi samajh gaya hoon ki beizzati ka level kitna zyada ho sakta hai.",
    "tu kis baat ka master hai? Apni neend mein toh tu bhi master hai.",
    "tujhe apni soch ko dynamic banana chahiye, static toh sirf internet pe hota hai.",
    "terii soch khud apne aap ko doubt karne mein time laga deti hai.",
    "tere jokes ko sun ke sab ke sab apne phone mein re-enable karte hain.",
    "tu sochta hai ki aapke paas wisdom hai, par reality check hai.",
    "apni soch ka low quality version poore duniya ko dekhata hai.",
    "tu ek self-made genius hai, jo apne brain ko khud se bhi banata hai.",
    "tu apni zindagi ke decisions ko review karna chahiye.",
    "agar tu chess khelta toh 'losing' ko apni special move bana leta.",
    "tu khud ki tareef mein do line likh, usse jyada seekh bhi nahi milegi.",
    "apni soch ka low quality version poore duniya ko dekhata hai.",
    "tu ek self-made genius hai, jo apne brain ko khud se bhi banata hai.",
    "tu jese sochne wale logh ka naam record book mein likhna chahiye.",
    "aajkal ke samaj mein, hum logo ka status 'zero' dikhata hai.",
    "tu apne aap ko puri duniya ke sabse padhaiwaala insaan samajhta hai.",
    "tere sarcasm ki wajah se main bhi samajh gaya hoon ki beizzati ka level kitna zyada ho sakta hai.",
    "tu kis baat ka master hai? Apni neend mein toh tu bhi master hai.",
    "tujhe apni soch ko dynamic banana chahiye, static toh sirf internet pe hota hai.",
    "terii soch khud apne aap ko doubt karne mein time laga deti hai.",
    "tere jokes ko sun ke sab ke sab apne phone mein re-enable karte hain.",
    "tu sochta hai ki aapke paas wisdom hai, par reality check hai.",
    "apni soch ka low quality version poore duniya ko dekhata hai.",
    "tu ek self-made genius hai, jo apne brain ko khud se bhi banata hai.",
    "tu apni zindagi ke decisions ko review karna chahiye.",
    "agar tu chess khelta toh 'losing' ko apni special move bana leta.",
    "tu khud ki tareef mein do line likh, usse jyada seekh bhi nahi milegi.",
    "apni soch ka low quality version poore duniya ko dekhata hai.",
    "tu ek self-made genius hai, jo apne brain ko khud se bhi banata hai.",
    "tu apni zindagi ke decisions ko review karna chahiye.",
    "agar tu chess khelta toh 'losing' ko apni special move bana leta.",
    "tu khud ki tareef mein do line likh, usse jyada seekh bhi nahi milegi.",
]

def login():
    cl = Client()
    cl.delay_range = [1, 3]
    try:
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()  # helps set user_id
        print(f"[LOGIN SUCCESS] Logged in as {USERNAME}")
    except Exception as e:
        print(f"[LOGIN FAILED] {e}")
        exit()
    return cl

def get_recent_messages(cl):
    try:
        return cl.direct_threads()
    except LoginRequired:
        print("[DEBUG] Session expired. Re-logging...")
        cl.login(USERNAME, PASSWORD)
        return cl.direct_threads()
    except Exception as e:
        print(f"[ERROR getting threads] {e}")
        return []

def reply_to_group_messages(cl):
    print("[BOT ACTIVE] Forced reply mode (no reply_to)...")
    my_user_id = cl.user_id  # fetch after login to avoid replying to self

    while True:
        threads = get_recent_messages(cl)
        for thread in threads:
            if not thread.is_group:
                continue

            try:
                updated_thread = cl.direct_thread(thread.id)  # ensure fresh messages
                last_msg: DirectMessage = updated_thread.messages[0]

                if last_msg.user_id == my_user_id:
                    continue  # skip own messages

                user_info = cl.user_info(last_msg.user_id)
                roast = random.choice(ROAST_MESSAGES)
                reply = f"@{user_info.username} {roast}"

                cl.direct_send(
                    text=reply,
                    thread_ids=[thread.id]
                )
                print(f"[REPLIED] To @{user_info.username}: {roast}")

            except Exception as e:
                print(f"[ERROR sending reply] {e}")
        time.sleep(5)

def main():
    cl = login()
    reply_to_group_messages(cl)

if __name__ == "__main__":
    main()
