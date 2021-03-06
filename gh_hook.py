import json

from flask import Flask, request
from secure import BOT_TOKEN, PROXY
from telegram import ParseMode
from telegram.ext import Updater
from telegram.utils.helpers import escape

app = Flask(__name__)

bot = Updater(BOT_TOKEN, request_kwargs=PROXY).bot


@app.route('/trigger/<user>/<repo>/<chat_id>', methods=['POST'])
def trigger(user, repo, chat_id):
    if not chat_id.startswith('-100'):
        chat_id = int(f'-100{chat_id}')
    chat_id = int(chat_id)
    data = json.loads(request.data)
    commits = []
    len_now = 0
    for commit in data['commits']:
        commit = f'<a href="{escape(commit["url"])}">{escape(commit["id"][:7])}</a>: <code>{escape(commit["message"])}</code> by {escape(commit["author"]["name"])}'
        len_now += len(commit)
        if len_now > 3900:
            break
        commits.append(commit)
    bot.send_message(chat_id=chat_id,
                     text=f'🔨 {len(data["commits"])} new {"commit" if len(data["commits"]) == 1 else "commits"} '
                          f'to <b>{escape(repo)}:{escape(data["ref"].split("/")[-1])}</b>:\n\n' +
                          "\n".join(commits),
                     parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return 'OK'


app.run(host='0.0.0.0', port=8009)
