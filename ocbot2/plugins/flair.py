#!/usr/bin/env python3
# coding: utf-8

import logging

from ocbot2.bot import oc_pattern

logger = logging.getLogger('ocb2.plugins.flair')

class Flair:
    def __init__(self, bot):
        self.bot = bot

    def check_submission(self, submission):
        logger.debug('Checking submission {} for flair'.format(submission))
        logger.debug('Current flair for {}: {}'.format(submission.author, submission.author_flair_text))
        special_flairs = ['mod', 'b', 'contrib', 's', 'practitioner', 'AMAGuest', 'researcher']

        # If there is a special flare, do not continue
        if submission.author_flair_css_class in special_flairs:
            return False

        count = self.count_oc(submission)

        # Check if author already has flair. 
        try:
            current_count = int(str(submission.author_flair_text)[4:])
        except ValueError:
            current_count = 0

        logger.debug('Author: {}: OC Flair: {} | OC Count: {}'.format(submission.author, current_count, count))
        # If new count is > current, set new flair. [this will always be true in a single-threaded environment, but may have race conditions if multithreaded]
        if count > current_count:
            self.set_flair(submission, count)
        else:
            logger.debug('Did not set flair for {}'.format(submission.author))

    def count_oc(self, submission):
        # Searching through current subreddit for other submissions by the author that has the word [oc] in it and counting them. Not sure how accurate reddit's engine is, but am checking against regex to make sure it is accurate.
        count = sum([
                    1
                    for _submission in (self.bot.rc
                        .subreddit(submission.subreddit.display_name)
                        .search(
                            'author:"{}" title:[oc]'.format(submission.author),
                            limit=1000
                        )
                    )
                    if oc_pattern.search(_submission.title)
                ])
        return count

    def set_flair(self, submission, count):
        try:
            logger.info('Flairing /u/{} with OC: {}'.format(submission.author, count))
            if not self.bot.READ_ONLY:
                (self.bot.rc
                    .subreddit(submission.subreddit.display_name)
                    .flair.set(
                        redditor=str(submission.author),
                        text='OC: {}'.format(count),
                        css_class = 'ocmaker'
                    )
                )
        except Exception:
            logger.exception('Error attempting to add flair to /u/{} with OC: {}'.format(submission.author, count))
