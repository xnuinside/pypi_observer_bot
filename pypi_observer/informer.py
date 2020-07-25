import telebot
import os
import requests
from random import choice
from datetime import datetime, timedelta
from time import sleep
from google.cloud import bigquery

chat_id = 0  # put here your chat id with bot

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../path/to/your/key"

client = bigquery.Client()


def bq_get_unique_packages_downloaded_for_yesterday():
    query_job = client.query(
        f"SELECT count(distinct(file.project)) as packages_number FROM "
        f"`the-psf.pypi.downloads{(datetime.now().date() - timedelta(days=1)).isoformat().replace('-', '')}`;")

    results = query_job.result()
    results = [row for row in results]
    return results[-1].packages_number


def bq_get_random_packages_downloaded_for_yesterday():
    query_job = client.query(
        f"SELECT distinct(file.project) as package_name FROM "
        f"`the-psf.pypi.downloads{(datetime.now().date() - timedelta(days=1)).isoformat().replace('-', '')}` "
        f"WHERE RAND() < 10/164656895;")

    results = query_job.result()
    results = [row.package_name for row in results]
    return results


def request_package_info_from_pypi(package_name):
    result = requests.get(f"https://pypi.org/pypi/{package_name}/json").json()
    info = result["info"]
    output = f'<i>{datetime.now().date()} Random Package from PyPi\n</i>' \
             f'<b>Package name:</b> {package_name}\n' \
             f'<b>Short description:</b> {info["summary"]}\n' \
             f'<b>Latest version:</b> {info["version"]}\n' \
             f'<b>Release date:</b> {result["releases"][info["version"]][0]["upload_time"].split("T")[0]}\n' \
             f'<b>Author:</b> {info["author"]}\n' \
             f'<b>Homepage:</b> {info["project_urls"]["Homepage"]}\n' \
             f'<b>Python versions:</b> {info["requires_python"]}'
    return output


bot = telebot.TeleBot("put_your_bot_token_here", parse_mode=None)

bot.send_message(chat_id=chat_id,
                 text=f"Total unique packages from PyPi, that was downloaded yesterday: "
                      f"{bq_get_unique_packages_downloaded_for_yesterday()}")

date_ = datetime.now().date()

while True:
    if date_ <= datetime.now().date():
        for i in range(5):
            if i == 4:
                date_ = datetime.now() + timedelta(days=1)

            bot.send_message(chat_id=chat_id,
                             text=request_package_info_from_pypi(
                                 choice(bq_get_random_packages_downloaded_for_yesterday())),
                             parse_mode="html")
            sleep(3)
            if i == 4:
                date_ = datetime.now().date() + timedelta(days=1)
