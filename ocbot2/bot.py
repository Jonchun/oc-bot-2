#!/usr/bin/env python3
# coding: utf-8

import logging
import pickle
import re
import time

import praw

from ocbot2.taskqueue import TaskQueue

logger = logging.getLogger('ocb2.bot')

# Case insensitive regex pattern to match [OC]
oc_pattern = re.compile(r'\[oc\]', re.I)

class Bot:
    """ The Bot class handles most of the general logic and operations of the OCbot.
    """
    def __init__(self,  workers=5, subreddits=[], **kwargs):
        """
        Construct a new Bot        

        Args:
            workers (int): How many workers to use when running bot.
            subreddits (list of str): List of subreddits to run the bot in.
        """
        self.READ_ONLY = kwargs.get('READ_ONLY', False)
        self.queue = TaskQueue(num_workers=workers)
        self.subreddits = subreddits

        try:
            # reddit client
            self.rc = praw.Reddit(
                        username=kwargs.get('username'),
                        password=kwargs.get('password'),
                        client_id=kwargs.get('client_id'),
                        client_secret=kwargs.get('client_secret'),
                        user_agent='OC-Bot-2'
                    )
        except Exception as e:
            raise Exception('Unable to connect to Reddit')

        self.reddit_name = self.rc.user.me().name

        self.register_plugins()
        self.load_db()

    def register_plugins(self):
        # intentionally importing plugins here to avoid possible circular dependencies
        from ocbot2.plugins.flair import Flair
        from ocbot2.plugins.sticky import Sticky
        from ocbot2.plugins.haiku import Haiku

        self.flair = Flair(self)
        logger.debug('Loaded Flair')

        self.sticky = Sticky(self)
        logger.debug('Loaded Sticky')

        self.haiku = Haiku(self)
        logger.debug('Loaded Haiku')

    def load_db(self):
        db = set()
        try:
            with open('records.pickle', 'rb') as f:
                db = pickle.load(f)
                logger.info('Loaded previous db from file')
        except Exception as e:
            logger.error('Unable to load previous records file. Starting from scratch.')
        self.db = db

    def save_db(self):
        with open('records.pickle', 'wb') as f:
            pickle.dump(self.db, f, protocol=pickle.HIGHEST_PROTOCOL)

        logger.info('Saved current db to file')

    def run(self):
        # We are going to loop through each subreddit where the bot is enabled and grab the hot 100.
        logger.info('Now active with {} workers...'.format(self.queue.num_workers))
        while True:
            for subreddit in self.subreddits:
                # Iterate through all new submissions
                submissions = self.rc.subreddit(subreddit).hot(limit=100)
                for submission in submissions:
                    self.queue.add_task(self.check_submission, submission)

                # Iterate through all new comments
                comments = self.rc.subreddit(subreddit).comments(limit=100)
                for comment in comments:
                    self.queue.add_task(self.check_comment, comment)

            logger.debug('Queued all tasks. Sleeping for 5 seconds')
            time.sleep(5)

    def check_submission(self, submission):
        # Don't parse if we already checked
        if str(submission) in self.db:
            logger.debug('Skipping {} [Submission]. Already in DB'.format(submission))
            return False

        # Don't continue if it is not approved. (Not sure how it would get in Hot, but just in case...). Ignore this setting if bot is in READ_ONLY mode, since it might be running as a non-mod user.
        if submission.approved_by is None and not self.READ_ONLY:
            logger.debug('Skipping {} [Submission]. Submission is Not Approved.'.format(submission))
            return False

        # We want to parse a submission to see if it is OC. 
        if oc_pattern.search(submission.title):
            self.queue.add_task(self.flair.check_submission, submission)
            self.queue.add_task(self.sticky.check_submission, submission)

        self.db.add(str(submission))
        logger.debug('Added {} [Submission] to db'.format(submission))


    def check_comment(self, comment):
        # Don't parse if we already checked
        if str(comment) in self.db:
            logger.debug('Skipping {} [Comment]. Already in DB'.format(comment))
            return False

        self.queue.add_task(self.haiku.check_comment, comment)

        self.db.add(str(comment))
        logger.debug('Added {} [Comment] to db'.format(comment))
