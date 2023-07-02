import telebot
import time
import requests
import re
import cloudscraper
import concurrent.futures
from bs4 import BeautifulSoup

# Replace '6372197549:AAE5dlIJwNw37_JISdtYmCrBfW9vSFila2s' with your actual Telegram Bot API token
bot = telebot.TeleBot('6372197549:AAE5dlIJwNw37_JISdtYmCrBfW9vSFila2s')

@bot.message_handler(commands=['start'])
def send_instructions(message):
    instructions = "Send me a movie URL and I will bypass the PSA links for you."
    bot.reply_to(message, instructions)

@bot.message_handler(func=lambda message: True)
def bypass_psa_links(message):
    url = message.text
    try:
        bypassed_links = psa_bypasser(url)
        bot.reply_to(message, bypassed_links)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.reply_to(message, error_message)

def try2link_bypass(url):
    client = cloudscraper.create_scraper(allow_brotli=False)
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
    client = cloudscraper.create_scraper(allow_brotli=False)
    h = {
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    res = client.get(url, cookies={}, headers=h)
    matches = re.findall(r'try2link\.com/(.*?)\s', res.text)
    if matches:
        try2link_url = 'https://try2link.com/' + matches[0]
        return try2link_bypass(try2link_url)
    else:
        raise Exception("Unable to find try2link URL in the response.")

def psa_bypasser(psa_url):
    client = cloudscraper.create_scraper(allow_brotli=False)
    r = client.get(psa_url)
    soup = BeautifulSoup(r.text, "html.parser").find_all(
        class_="dropshadowboxes-drop-shadow dropshadowboxes-rounded-corners dropshadowboxes-inside-and-outside-shadow dropshadowboxes-lifted-both dropshadowboxes-effect-default")

    bypassed_links = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for link in soup:
            try:
                exit_gate = link.a.get("href")
                bypassed_link = try2link_scrape(exit_gate)
                bypassed_links.append(bypassed_link)
            except Exception as e:
                error_message = f"An error occurred while bypassing a link: {str(e)}"
                print("Wrok In Progress..")

    return '\n'.join(bypassed_links)

bot.polling()
