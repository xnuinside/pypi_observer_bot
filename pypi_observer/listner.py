import telebot
from google.cloud import bigquery
from datetime import datetime, timedelta
import os

bot = telebot.TeleBot("put_your_bot_token_here", parse_mode=None)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../path/to/your/key"
client = bigquery.Client()


def bq_get_downloads_stats_for_package(package_name, date_):
    query_job = client.query(
        f"SELECT count(timestamp) as downloads FROM `the-psf.pypi.downloads{date_}` "
        f"WHERE file.project=\'{package_name}\'")
    results = query_job.result()
    result = [row for row in results][-1]
    return result.downloads


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=['stats'])
def send_package_stats(message):
    package_name = message.text.split()[1].replace('_', '-')
    output = f"Stats for package {package_name} (numbers of downloads): \n"
    for i in range(4):
        date_ = (datetime.now().date() - timedelta(days=i+1)).isoformat()
        formatted_date_ = date_.replace('-', '')
        downloads = bq_get_downloads_stats_for_package(package_name, formatted_date_)
        output += f"<b>{date_}</b>: {downloads}\n"
    bot.reply_to(message, output, parse_mode="html")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()
