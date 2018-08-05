# oc-bot-2

## Introduction
This is my rewrite of https://github.com/zonination/oc-bot/. I thought it would be a fun project to clean up, and hopefully this takes off. I took about 3-4 hours to whip this up, so it's not perfect, and its not fully tested. However, I tried to be a bit cleaner with the code than the original, and is hopefully much more extensible and easy to grow.

**Meet OC-Bot-2**
* Gender: Male
* Workplace: "The Cloud"
* Birthday: 2018-08-05
* Relationship: Currently trying to steal oc-bot
* Address: 127.0.0.2

## How-To-Use
1. Install requirements (praw and python-dotenv). You can do this via pip or pipenv+pipfile.
2. Clone the repo `git clone https://github.com/jonchun/oc-bot-2.git`
3. Go inside repo `cd oc-bot-2`
4. Copy `.env.example` to `.env` and fill out the bot credentials
5. Run the bot as a module `python3 -m ocbot2`, or run `python3 ocbot2/__main__.py`

## Primary Operation
**IF:**
* Post has the text `[OC]` in the title AND
* The post is approved by a mod AND
* The user's flair is NOT a reserved flair AND
* The post has NOT been logged before

**THEN:**
* Make a sticky linking to the first submitter's comment on the post AND
* Log the post it made a sticky on

### Secondary operations
* The bot replies to comments made on the sticky with a randomly-generated haiku.

