#!/usr/bin/env python3
# coding: utf-8

import logging
import os 

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger('ocb2.plugins.sticky')

class Sticky:
    def __init__(self, bot):
        self.bot = bot

    def check_submission(self, submission):
        try:
            citation_comment = self.get_citation_comment(submission)
            reply = ''
            # Load up reply template
            with open(DIR_PATH+'/sticky.d/reply', 'r') as f:
                reply = f.read()
            # Replace variables
            reply = reply.replace('{user}', citation_comment.author.name)
            reply = reply.replace('{permalink}', citation_comment.permalink)
            reply = reply.replace('{subreddit}', citation_comment.subreddit.display_name)
            if not self.bot.READ_ONLY:
                submission.reply(reply).mod.distinguish(sticky=True)
            logger.info('Sticky added to {}'.format(submission))
        except Exception:
            logging.exception('Could not create Sticky for {}'.format(submission))

    def get_citation_comment(self, submission):
        logger.debug('Locating citation comment for {}'.format(submission))
        submission.comment_sort = 'old'
        submission.comment_limit = 20
        submission.comments.replace_more(limit=0)
        # Get list of oldest 20 comments. Reddit API sometimes returns them out of order (???) so I am sorting them by created_utc client-side
        comments_list = sorted(submission.comments.list(), key=lambda x: x.created_utc)
        """
        Looping through the oldest 20 comments to find first comment by author (which should be the comment containing data sources), since being the oldest comment does not guarantee that it is the OP's. If we don't find what we want within the 20 oldest comments, we'll assume something is wrong and just return None.
        """
        for comment in comments_list:
            logger.debug('comment {} is by {}. submission is by {}'.format(comment, comment.author, submission.author))
            if comment.author == submission.author:
                return comment
        return None
