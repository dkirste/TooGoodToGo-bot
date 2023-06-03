import time
import pickle
import telegram
import asyncio
import threading

from tgtg import TgtgClient


from telegram import __version__ as TG_VER
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

tgtg_users = {}
active_users = []
allowed_users = []
cache = {}
telegram_token = ""

def save_tgtg_users():
    with open('tgtg_users.pkl', 'wb') as f:
        pickle.dump(tgtg_users, f)

def load_tgtg_users():
    with open('tgtg_users.pkl', 'rb') as f:
        return pickle.load(f)

def save_config():
    config = (telegram_token, allowed_users, active_users)
    with open('allowed_users.pkl', 'wb') as f:
        pickle.dump(config, f)

def load_config():
    """Returns (telegram_token, allowed_users, active_users)"""
    with open('allowed_users.pkl', 'rb') as f:
        return pickle.load(f)

def check_auth(user_id):
    if user_id['id'] in allowed_users:
        return True
    else:
        return False

def get_favs(access_token, refresh_token, user_id, cookie):
    client = TgtgClient(access_token=access_token, refresh_token=refresh_token, user_id=user_id,
                        cookie=cookie)

    favorites = client.get_favorites()
    favs = []
    for fav in favorites:
        item_name = fav['item']['name']
        item_id = fav['item']['item_id']
        item_price = fav['item']['price_including_taxes']['minor_units'] / 10 ** fav['item']['price_including_taxes'][
            'decimals']
        item_amount = fav['items_available']
        store_name = fav['store']['store_name']
        store_address = fav['store']['store_location']['address']['address_line']
        store_logo = fav['store']['logo_picture']['current_url']
        favs.append({'item_name': item_name, 'item_id': item_id, 'item_price': item_price, 'item_amount': item_amount,
                     'store_name': store_name, 'store_address': store_address, 'store_logo': store_logo})
    return favs



def get_updates(access_token, refresh_token, user_id, cookie):
    tgtg_updates = []
    favs = get_favs(access_token, refresh_token, user_id, cookie)
    for fav in favs:
        if not user_id in cache:
            cache[user_id] = favs
            if fav['item_amount'] >= 1:
                tgtg_updates.append(fav)
        if not fav in cache[user_id]:
            if fav['item_amount'] >= 1:
                tgtg_updates.append(fav)
    cache[user_id] = favs
    return tgtg_updates

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    print(f"User started the bot: {update.message.from_user}")
    user = update.effective_user
    user_id = update.message.from_user['id']

    if check_auth(update.message.from_user):
        active_users.append(user_id)
        print(f"Active Users: {active_users}")
        await update.message.reply_html(
            f"Hi {user.mention_html()}!\nYou successfully started the bot.")
    else:
        await update.message.reply_html(
            f"You are not authorized!.")
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    print(f"User stopped the bot: {update.message.from_user}")
    user_id = update.message.from_user['id']
    if check_auth(update.message.from_user):
        for i in range(len(active_users)):
            if active_users[i] == user_id:
                active_users.pop(i)
        await update.message.reply_html(
            f"You successfully stopped the bot.")

async def init(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    auth_status = "authorized" if check_auth(update.message.from_user) else "not authorized"
    print(f"User initialised the bot: {update.message.from_user}")
    email=update.message.text.replace("/init ", "")
    print(f"Trying to use: {email}")
    user_id = update.message.from_user['id']
    if check_auth(update.message.from_user):
        await update.message.reply_html(
            f"You will get an email from TooGoodToGo! Please check you mail and open the link on your desktop computer!\nMOBILE PHONES ARE NOT WORKING, SINCE THE APP IS OPENED.")
        client = TgtgClient(email=email, timeout=1)
        credentials = client.get_credentials()
        user_data = {
                'access_token': credentials['access_token'],
                'refresh_token': credentials['refresh_token'],
                'user_id': credentials['user_id'],
                'cookie': credentials['cookie']}
        tgtg_users[int(user_id)] = user_data
        print(f"Added: {user_data}")
        save_tgtg_users()


async def check_for_user(tg_bot, userid):
    access_token = tgtg_users[userid]['access_token']
    refresh_token = tgtg_users[userid]['refresh_token']
    user_id = tgtg_users[userid]['user_id']
    cookie = tgtg_users[userid]['cookie']
    tgtg_updates = get_updates(access_token, refresh_token, user_id, cookie)
    for update in tgtg_updates:
        update_text=f"{update['store_name']}\n<a href='{update['store_logo']}'>&#8205;</a>{update['item_amount']}x {update['item_name']} for {update['item_price']} EUR\n{update['store_address']}\nhttps://share.toogoodtogo.com/item/{update['item_id']}/"+str(time.time())
        await tg_bot.send_message(chat_id=userid, text=update_text, parse_mode='HTML')


async def main(tg_bot):
    while True:
        for userid in active_users:
            print("start check")
            await check_for_user(tg_bot, userid)
            print("end check")
        print(active_users)
        time.sleep(30)

def bot_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    print("Starting thread")
    # load users
    load_pkl = True
    if load_pkl:
        tgtg_users = load_tgtg_users()
        telegram_token, allowed_users, active_users = load_config()
        if input("Do you want to add new users? (y/n)") == "y":
            allowed_users_str = input("New users to add: ").split(",")
            for user_str in allowed_users_str:
                allowed_users.append(int(user_str))
            save_config()
    else:
        telegram_token = input("Enter the telegram token: ")
        allowed_users_str = input("Enter the user IDs in a comma separated list: ").split(",")
        for user_str in allowed_users_str:
            allowed_users.append(int(user_str))
        save_config()




    bot = telegram.Bot(token=telegram_token)

    # Generate loop and start thread
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=bot_loop, args=(loop,), daemon=True)
    t.start()

    # Add task to loop
    task = asyncio.run_coroutine_threadsafe(main(bot), loop)


    application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("init", init))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()





