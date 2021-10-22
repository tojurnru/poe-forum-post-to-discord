import os
import re
import requests
import json

from bs4 import BeautifulSoup
from datetime import datetime, timezone
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
from time import sleep



#
# get environment variables
#

load_dotenv()

DISCORD_WEBHOOK_ID = os.getenv('DISCORD_WEBHOOK_ID')
DISCORD_WEBHOOK_HASH = os.getenv('DISCORD_WEBHOOK_HASH')
FORUM_THREAD_ID = os.getenv('FORUM_THREAD_ID')
PAGE = os.getenv('PAGE') # optional
POST_ID = os.getenv('POST_ID') # optional

if DISCORD_WEBHOOK_ID is None or DISCORD_WEBHOOK_HASH is None or FORUM_THREAD_ID is None:
    env_vars = [DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_HASH, FORUM_THREAD_ID]
    raise Exception(f'one or more env vars empty: {env_vars}')



#
# constants
#

POE_URL = 'https://www.pathofexile.com'
POE_FORUM_URL = 'https://www.pathofexile.com/forum/view-thread/'
WEBHOOK_URL = f'https://discord.com/api/webhooks/{DISCORD_WEBHOOK_ID}/{DISCORD_WEBHOOK_HASH}'
HTTP_HEADERS = { 'User-Agent': 'tojurnru:poe-forum-scraper-bot' }



#
# functions
#

def get_page_content(page):
    url = f'{POE_FORUM_URL}{FORUM_THREAD_ID}/page/{page}'
    response = requests.get(url, headers = HTTP_HEADERS)
    status_code = response.status_code

    if status_code != 200:
        raise Exception(f'HTTP Response {status_code}: {response.reason} (URL {url})')

    return BeautifulSoup(response.content, 'html.parser')


def get_last_page_index(soup):
    pagination = soup.select('.topBar .pagination')

    if len(pagination) == 0:
        return 1

    links = pagination[0].find_all('a')
    last_page = links[len(links) - 2].get_text().strip()
    return int(last_page)


def is_new_post(post_id, last_post_id):
    post_id = int(post_id[1:])
    last_post_id = int(last_post_id[1:])
    return post_id > last_post_id


def process_page(soup, current_page, last_post_id):
    contents = soup.select('.content-container .content')
    post_infos = soup.select('.post_info')

    for idx, content in enumerate(contents):
        post_info = post_infos[idx]

        # check if it's new post, skip otherwise
        post_id = post_info.select('.post_anchor')[0]['id']

        if not is_new_post(post_id, last_post_id):
            continue

        # get user data
        date = post_info.select('.post_date')[0].get_text() # initial format: Oct 16, 2021, 6:48:05 PM
        date_utc = datetime.strptime(date, '%b %d, %Y, %I:%M:%S %p').astimezone(timezone.utc)
        str_date_utc = datetime.strftime(date_utc, '%Y-%m-%d %H:%M:%S UTC')

        a = post_info.select('.post_by_account a')[0]
        username = a.get_text()
        user_url = f'{POE_URL}{a["href"]}'

        post_url = f'{POE_FORUM_URL}{FORUM_THREAD_ID}/page/{current_page}#{post_id}'

        # avatar_url = post_info.select('.avatar img')[0]['src']

        # get post content
        text = ' '.join(line.strip() for line in content.get_text().split('\n'))
        if (len(text) > 1000):
            text = text[:1000] + '... (more)'

        message = '~~**                                                                                                                     **~~\n'
        message += f'**Date**: {str_date_utc}\n'
        message += f'**Post**: <{post_url}>\n'
        message += f'**User**: `{username}` ||<{user_url}>||\n'
        message += f'**Message**:\n{text}\n'
        # message += f'**Avatar**: {avatar_url}\n'

        # print(f'    {message}')
        print(f'  send new message to discord #{post_id}')
        webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
        webhook.execute()
        sleep(1)

        last_post_id = post_id

    return last_post_id




#
# 1. get page and last_post_id:
#    ENV_VAR > file > default value
#

current_page = PAGE
last_post_id = POST_ID

if current_page is None or last_post_id is None:
    try:
        f = open('config.json', 'r')
        config = json.loads(f.read())
        f.close()

        # only use config file if same thread id
        if FORUM_THREAD_ID == config['forum_thread_id']:
            current_page = current_page or config['page']
            last_post_id = last_post_id or config['post_id']
        else:
            print('Forum thread id changed. use default value')

    except Exception as ex:
        print(f'Error reading config.json, getting default value ({ex})')

current_page = current_page or 1
last_post_id = last_post_id or 'p0'

current_page = int(current_page)

print(f'[start] page: {current_page}, last post id: {last_post_id}')


#
# 2. process page loop
#

current_soup = get_page_content(current_page)

last_page_index = get_last_page_index(current_soup)

while True:
    last_post_id = process_page(current_soup, current_page, last_post_id)

    if current_page >= last_page_index:
        break

    current_page += 1
    sleep(5) # sleep timer before next request
    current_soup = get_page_content(current_page)

    print(f'page: {current_page}, last post id: {last_post_id}')


#
# 3. save config into file
#

print(f'[end] page: {current_page}, last post id: {last_post_id}')

config = {
    'forum_thread_id': FORUM_THREAD_ID,
    'page': current_page,
    'post_id': last_post_id
}
f = open('config.json', 'w+')
f.write(json.dumps(config))
f.close()
