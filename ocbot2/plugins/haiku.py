#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import random

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger('ocb2.plugins.haiku')

class Haiku:
    def __init__(self, bot):
        self.bot = bot
        with open(DIR_PATH+'/haiku.d/line1', 'r') as f:
            self.line1 = [line.rstrip() for line in f]
        with open(DIR_PATH+'/haiku.d/line2', 'r') as f:
            self.line2 = [line.rstrip() for line in f]
        with open(DIR_PATH+'/haiku.d/line3', 'r') as f:
            self.line3 = [line.rstrip() for line in f]

    def generate(self):
        haiku = '\t{}\n\t{}\n\t{}'.format(random.choice(self.line1), random.choice(self.line2), random.choice(self.line3))
        return haiku

    def reply(self, comment):
        if not self.bot.READ_ONLY:
            comment.reply(self.generate())
        logger.info('Replied to /u/{} with haiku'.format(comment.author))

    def check_comment(self, comment):
        # We want to parse a comment to see if it is a response to OC-Bot-2. We do this by checking to make sure the author of the comment parent is the same as the bot's user. Also need to make sure that the Bot does not reply to itself and cause an infinite loop, so the comment itself should not be by the bot.
        if (str(comment.parent().author) == self.bot.reddit_name) and (str(comment.author) != self.bot.reddit_name):
            self.reply(comment)
