# POE Forum Post To Discord

A script that scan for new posts in Path of Exile forum thread and post it to discord. Because who camps in forums to check for new posts?

Only monitor ONE thread per program.


## Sample Output

![sample output](/readme/sample.png)

[Forum Thread](https://www.pathofexile.com/forum/view-thread/3187997/page/8)


## How to Use

1. Git pull this repo
1. `pip install -r requirement.txt`
1. Rename `.env.example` to `.env`, and set the environment variables accordingly:
    - `DISCORD_WEBHOOK_ID` & `DISCORD_WEBHOOK_HASH` (https://discord.com/api/webhooks/<DISCORD_WEBHOOK_ID>/<DISCORD_WEBHOOK_HASH>)
    - `FORUM_THREAD_ID` the forum thread you'd like to monitor (https://www.pathofexile.com/forum/view-thread/<FORUM_THREAD_ID>)
    - `PAGE` (Optional) Which page to start process. If not indicated, it will start from the first page
    - `POST_ID` (Optional) The last processed post id. If not indicated, it will send all posts in the page to Discord
1. Execute `python main.py`
1. Profit!

In addition you can setup a cron job to run this script periodically, once a day or once an hour (Please don't spam POE site too often)
