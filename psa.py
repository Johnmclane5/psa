import time
import requests 
import re
import cloudscraper 
import concurrent.futures
from bs4  import BeautifulSoup
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Telegram bot token
TOKEN = '5820612315:AAFP2y6cv5b0GOC9i9D6-1Ef0m_rAgGIyoY'



client = cloudscraper.create_scraper(allow_brotli=False)


def try2link_bypass(url):
    url = url[:-1] if url[-1] == '/' else url
    params = (('d', int(time.time()) + (60 * 4)),)
    r = client.get(url, params=params, headers={'Referer': 'https://newforex.online/'})
    soup = BeautifulSoup(r.text, 'html.parser')
    inputs = soup.find(id="go-link").find_all(name="input")
    data = {input.get('name'): input.get('value') for input in inputs}
    time.sleep(7)
    headers = {'Host': 'try2link.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://try2link.com',
               'Referer': url}
    bypassed_url = client.post('https://try2link.com/links/go', headers=headers, data=data)
    return bypassed_url.json()["url"]


def try2link_scrape(url):
    h = {
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    res = client.get(url, cookies={}, headers=h)
    url = 'https://try2link.com/' + re.findall('try2link\.com\/(.*?) ', res.text)[0]
    return try2link_bypass(url)


def psa_bypasser(psa_url):
    r = client.get(psa_url)
    soup = BeautifulSoup(r.text, "html.parser").find_all(
        class_="dropshadowboxes-drop-shadow dropshadowboxes-rounded-corners dropshadowboxes-inside-and-outside-shadow dropshadowboxes-lifted-both dropshadowboxes-effect-default")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for link in soup:
            try:
                exit_gate = link.a.get("href")
                executor.submit(try2link_scrape, exit_gate)
            except:
                pass


def generate_bypassed_link(url):
    if 'psa_bypasser(' in url:
        url = url.replace('psa_bypasser("', '').replace('")', '')
        psa_bypasser(url)
        return "Bypassing PSA links..."
    else:
        return "Invalid command."


def start(update, context):
    """Send a welcome message when the /start command is issued."""
    update.message.reply_text('Welcome to the Link Bypasser Bot!')


def bypass_link(update, context):
    """Extract the URL from the message and reply with a bypassed link."""
    message = update.message.text
    bypassed_link = generate_bypassed_link(message)
    update.message.reply_text(bypassed_link)


def main() -> None:
    # Create the Updater and pass in the bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Define the command handlers
    dp.add_handler(CommandHandler("start", start))

    # Define the message handler
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), bypass_link))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
