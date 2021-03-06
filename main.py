import praw
import os
import configparser
from datetime import timedelta, datetime
import logging
LOG_FORMAT = "%(levelname)s | %(asctime)s : %(message)s"
logging.basicConfig(filename="flair-bot.log", level=logging.DEBUG, format=LOG_FORMAT)

logger = logging.getLogger()
config = configparser.ConfigParser()
config.read('auth.ini')  # All my usernames and passwords for the api

reddit = praw.Reddit(client_id=config.get('auth', 'reddit_client_id'),
                     client_secret=config.get('auth', 'reddit_client_secret'),
                     password=config.get('auth', 'reddit_password'),
                     user_agent="Flair your posts script made by u/J_C___",
                     username=config.get('auth', 'reddit_username'))
bot_message = "\r\r^(I am a script. If I did something wrong, ) [^(let me know)](/message/compose/?to=J_C___&subject=Flair_post_bot)"
logger.info("Posting as: " + str(reddit.user.me()))
SUBREDDIT = config.get('auth', 'reddit_subreddit')
LIMIT = int(config.get('auth', 'reddit_limit'))

# If the posts_replied text file dosn't exist, create it and initialize the empty list.
if not os.path.isfile("posts_replied.txt"):
    posts_replied = []
# If the file does exist import the contents into a list
else:
    with open("posts_replied.txt", "r") as f:
       posts_replied = f.read()
       posts_replied = posts_replied.split("\n")
       posts_replied = list(filter(None, posts_replied))

rule_1 = "\r\r>**All posts must be assigned a flair**. If you don't flair your post, it will be removed. You can flair on mobile by posting it in your title, such as [Theory] Toffee is Star's brother. [Here is a list of flair options](https://www.reddit.com/r/StarVStheForcesofEvil/wiki/flairs). If your post is removed by the flair bot, **do NOT repost it**: [message the mods](https://www.reddit.com/message/compose?to=%2Fr%2FStarVStheForcesofEvil&subject=&message=) and we'll approve it. Unflaired posts are subject to removal without warning at any time."
def reply_bot():
    subreddit = reddit.subreddit(SUBREDDIT)
    new_posts = subreddit.new(limit=LIMIT)
    for submission in new_posts:
        if (submission.link_flair_text is None) and (datetime.utcnow() - datetime.fromtimestamp(submission.created_utc) >= timedelta(minutes=15)) and submission.id not in posts_replied:
            submission.reply("Hey there u/" + submission.author.name + "! Your post has been removed in accordance with rule #1 of this subreddit." + rule_1 + bot_message)
            submission.mod.remove()
            logger.info('Submission removed:' + str(submission.id))
            posts_replied.append(submission.id)
            update_files(posts_replied)


def update_files(posts_replied):
    with open("posts_replied.txt", "w") as f:
        for x in posts_replied:
            f.write(x + "\n")
    logger.info("Progress File Successfully Updated!")


try:
    logger.info("------Starting: Flair Your Post Bot------")
    while True:
        reply_bot()
except KeyboardInterrupt:
    update_files(posts_replied)
    logger.warning('Script interrupted')
