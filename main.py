"""Scraper and bot operating on Instagram.

InstagramBot able to check unfollows for a given user
or check users not following back. Also operates simple
task like following people from file or like posts.
"""

import time
import argparse
import os.path
from math import trunc

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import config as cfg
import exceptions

class InstagramBot:
    """
    Main bot class.

    Attributes:
        driver: module derivated from selenium.
        username: account username provided in config.py.
        password: account password provided in config.py.
    """

    def __init__(self, username, password,
                 skip_login, disable_images):
        """Inits InstagramBot setups chrome driver."""
        self.username = username
        self.password = password
        if skip_login:
            self.chrome_options = webdriver.ChromeOptions()
            self.chrome_options.add_argument('--user-data-dir=chrome_options/')
            if disable_images:
                prefs = {'profile.managed_default_content_settings.images': 2}
                self.chrome_options.add_experimental_option('prefs', prefs)
            self.driver = webdriver.Chrome(options=self.chrome_options)
        else:
            self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.get('https://www.instagram.com/accounts/login/')
        if self.driver.current_url != ('https://www.instagram.com/'):
            self._log_in()
        self._change_language()

    def _log_in(self):
        """Log in as username and password given in config.py"""
        # Pass cookies.
        self.driver.find_element_by_xpath\
            ('/html/body/div[2]/div/div/div/div[2]/button[1]').click()
        # Insert login and password.
        self.driver.find_element_by_xpath\
            ('//input[@name=\"username\"]').send_keys(self.username)
        self.driver.find_element_by_xpath\
            ('//input[@name=\"password\"]').send_keys(self.password)
        # Click login.
        self.driver.find_element_by_xpath\
            ('//*[@id="loginForm"]/div/div[3]').click()
        # Pass remember login popoup.
        self.driver.find_element_by_xpath\
            ('//*[@id="react-root"]/section/main/div/div/div/section/div/button').click()
        # Pass notification popup.
        self.driver.find_element_by_xpath\
            ('/html/body/div[4]/div/div/div/div[3]/button[2]').click()

    def _change_language(self):
        """Changes language to english - crucial for some methods."""
        Select(self.driver.find_element_by_xpath\
            ('//*[@id="react-root"]/section/main/section/div[3]/div[3]/nav/ul/li[11]/span/select'))\
            .select_by_visible_text('English')

    def _get_user(self, username):
        """Gets user page."""
        self.driver.get(f'https://www.instagram.com/{username}')
        if "This page isn't available" in self.driver.page_source:
            raise exceptions.NoSuchUserException(username)

    def _is_public(self, username):
        """Checks if userpage is public (or just available)."""
        self._get_user(username)
        return not 'This Account is Private' in self.driver.page_source

    def _get_how_many_followers(self, username):
        """Gets number of followers of user."""
        self._get_user(username)
        how_many_followers = self.driver.find_elements_by_xpath('//span[@class="g47SY "]')[1].text
        if not how_many_followers.isdigit():
            how_many_followers_list = list(how_many_followers)
            for _ in range(0, len(how_many_followers)):
                if how_many_followers_list[_] == 'k':
                    how_many_followers_list[_] = '000'
                elif how_many_followers_list[_] == 'm':
                    how_many_followers_list[_] = '000000'
                elif how_many_followers_list[_] == '.' or how_many_followers_list[_] == ',':
                    how_many_followers_list[_] = ''
            how_many_followers_new = "".join(how_many_followers_list)
            if '.' in how_many_followers:
                how_many_followers_new = how_many_followers_new[:-1]
            how_many_followers = how_many_followers_new
        return int(how_many_followers)

    def _get_how_many_following(self, username):
        """Gets number of user followings."""
        self._get_user(username)
        return int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[2]).text)

    def _get_how_many_posts(self):
        """Gets number of user post."""
        return int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[0]).text)

    def _get_how_many_likes(self):
        """Gets number of likes under post."""
        return int(self.driver.find_element_by_xpath\
            ('/html/body/div[5]/div[2]/div/article/div[3]/section[2]/div/div[2]/button/span').text()) + 1

    def _scroll_popup(self, count_limit, popup_xpath):
        """Scrolls through following/followers pop-up window."""
        pop_up = self.driver.find_element_by_xpath(popup_xpath)
        scroll_height = self.driver.execute_script('return arguments[0].scrollHeight', pop_up)
        window_height = 0
        start_scrolling = time.perf_counter()
        while True:
            self.driver.execute_script('arguments[0].scrollBy(0,arguments[1])', pop_up, scroll_height)
            scroll_height = self.driver.execute_script('return arguments[0].scrollHeight', pop_up)
            if window_height != self.driver.execute_script('return arguments[0].scrollHeight', pop_up):
                window_height = self.driver.execute_script('return arguments[0].scrollHeight', pop_up)
                new_window_height = time.perf_counter()
            if (time.perf_counter() - new_window_height > 5):
                end_scrolling = time.perf_counter()
                break
            scroll_height += scroll_height
        print(f'Scroll ended. It took {trunc(end_scrolling - start_scrolling)} seconds.')
        usernames_list = [(username.text).replace('\nVerified','') for username in self.driver.find_elements_by_xpath('//div[@class="d7ByH"]')]
        return usernames_list

    def get_following(self, username):
        """Gets users followed by given user."""
        number_of_following_on_page = self._get_how_many_following(username)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()
        print('Getting following list...')
        following_list = self._scroll_popup(number_of_following_on_page, '//div[@class="isgrP"]')
        print(f'Number of loaded following users: {len(following_list)}. {number_of_following_on_page - len(following_list)} users missed.')
        return following_list

    def get_followers(self, username, save_to_file=False):
        """Gets users following given user."""
        number_of_followers_on_page = self._get_how_many_followers(username)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()
        print('Getting followers list...')
        followers_list = self._scroll_popup(number_of_followers_on_page, '//div[@class="isgrP"]')
        print(f'Number of loaded followers users: {len(followers_list)}. {number_of_followers_on_page - len(followers_list)} users missed.')
        if save_to_file:
            with open(f'logs/followers_{username}.txt', 'w') as file:
                for user in followers_list:
                    file.write(f'{user}\n')
            print(f'Followers ({number_of_followers_on_page}) have been saved to the file.')
        return followers_list

    #TODO: add option to not get number of followers (parse)
    def get_not_following_back(self, username, get_followers_value=True):
        """Gets user that are followed but are not following back given user."""
        if self._is_public(username):
            following_list = set(self.get_following(username))
            followers_list = set(self.get_followers(username))
            if get_followers_value:
                not_following_back = []
                for user in following_list.difference(followers_list):
                    not_following_back.append([user, self._get_how_many_followers(user)])
                # Sort list by followers number.
                not_following_back.sort(key=lambda user:user[1])
            else:
                not_following_back = [user for user in following_list.difference(followers_list)]
            with open(f'logs/not_following_back_{username}.txt', 'w') as file:
                for user in not_following_back:
                    file.write(f'{user}\n')
            print(f"{username} has {len(not_following_back)} not following back users. That's {trunc(len(not_following_back)/len(following_list)*100)}% of the following list. Results are saved to the file in /logs.")
        else:
            print(f'The user account {username} is private, could not get not-following-back list')

    def get_unfollowers(self, username):
        """Gets users that had followed given user but unfollowed after some time."""
        if self._is_public(username):
            try:
                past_followers_file_dir = (f'logs/followers_{username}.txt')
                with open(past_followers_file_dir, 'r') as file:
                    print(f'Succesfully read {past_followers_file_dir} file created on: {time.ctime(os.path.getmtime(past_followers_file_dir))}')
                    past_followers = {follower.rstrip() for follower in file}
                current_followers = set(self.get_followers(username))
                unfollowers = past_followers.difference(current_followers)
                active_unfollowers = []
                for unfollower in unfollowers:
                    try:
                        self._get_user(unfollower)
                        active_unfollowers.append(unfollower)
                    except exceptions.NoSuchUserException:
                        continue
                print(f'{username} has {len(active_unfollowers)} active unfollower(s): {active_unfollowers}. Users that changed name or deleted acounts: {unfollowers}')
            except OSError:
                answer = ''
                while answer not in ('Y', 'N'):
                    answer = input(f'Past followers for {username} not found. Do you want to create it right now? (Y/N): '.upper())
                if answer == "Y":
                    self.get_followers(username, save_to_file=True)
                else:
                    print('Could not get unfollowers list without previous followers list')
        else:
            raise exceptions.UserAccountPrivateException(username)

    def get_leaderboard(self, username):
        """Get likes from each post on user page and create top-interactions-followers"""
        if self._is_public(username):
            number_of_posts_on_page = self._get_how_many_posts()
            number_of_clicks = 0
            #click latest post
            self.driver.find_element_by_xpath\
                ('//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div').click()
            while True:
                #click likes list
                self.driver.find_element_by_xpath\
                    ('/html/body/div[5]/div[2]/div/article/div[3]/section[2]/div/div[2]/button').click()
                #get number of likes:
                #self._get_how_many_likes()
                #scroll through popup window to the end

                #get every user and get them to the list

                #click next photo arrow button until last post
                self.driver.find_element_by_css_selector\
                    ('a.coreSpriteRightPaginationArrow').click()
                number_of_clicks += 1
                if number_of_clicks == number_of_posts_on_page - 1:
                    print(number_of_clicks)
                    break
            #print or save to the file from top reaction to less

        else:
            raise exceptions.UserAccountPrivateException(username)

    #TODO: ensure print if followed before
    #TODO: find another way to find "follow" button
    def follow_user(self, username):
        """Follows given user."""
        if self._is_public(username):
            try:
                self.driver.find_element_by_xpath\
                    ('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button').click()
                print(f'{username} has been followed.')
                #if followed before print that info here
            except NoSuchElementException:
                try:
                    self.driver.find_element_by_xpath\
                        ('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/div/div/div/span/span[1]/button').click()
                    print('{username} has been followed.')
                except NoSuchElementException:
                    print(f'Could not follow {username}.')
        else:
            try:
                self.driver.find_element_by_xpath\
                    ('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/button').click()
            except NoSuchElementException:
                print(f'Could not follow {username}.')

    def like_latest_post(self, username):
        """Likes latest post of desired user."""
        if self._is_public(username):
            self.driver.find_element_by_xpath\
                ('//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div').click()
            self.driver.find_element_by_xpath\
                ('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button').click()
        else:
            raise exceptions.UserAccountPrivateException(username)

    def comment_latest_post(self, username, message):
        """Comment latest post of desired user with given message."""
        if self._is_public(username):
            self.driver.find_element_by_xpath\
                ('//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div').click()
            self.driver.find_element_by_xpath\
                ('/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form').click()
            self.driver.find_element_by_xpath\
                ("/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea").send_keys(message)
            self.driver.find_element_by_xpath\
                ('/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/button').click()
        else:
            raise exceptions.UserAccountPrivateException(username)

    #TODO: add parsing argument for comment last post
    #TODO: add how many users have been followed at the end
    #TODO: comment with desired message
    def follow_from_file(self, like_latest_post):
        """Follows users given in users_to_follow.txt file."""
        with open('users_to_follow.txt', 'r') as file:
            to_follow_list = file.read().splitlines()
        print(f'Number of records loaded from the file: {len(to_follow_list)}.')
        for username in to_follow_list:
            try:
                self.follow_user(username)
                if self._is_public(username) and like_latest_post:
                    try:
                        self.like_latest_post(username)
                        print('Liked latest post')
                    except NoSuchElementException:
                        print('Could not like latest post of {username}')
            except exceptions.NoSuchUserException:
                print('User {username} does not exist.')
        print('Users have been followed')

my_bot = InstagramBot(cfg.USERNAME, cfg.PASSWORD, cfg.SKIP_LOGIN, cfg.DISABLE_IMAGES)
parser = argparse.ArgumentParser(prog="main.py", description="InstagramBot")
parser.add_argument("username", nargs="?", default=cfg.USERNAME,
                    type=str, help="check desired user")

parser.add_argument("-u", "--unfollowers", action="store_true",
                    help="check unfollowers for the given user")

parser.add_argument("-n", "--notfollowingback", action="store_true",
                    help="check users not following back the given user")

parser.add_argument("-f", "--follow", action="store_true",
                    help="follow users from the file")

parser.add_argument("-l", "--like", action="store_true",
                    help="like latest post (only with -f command)")
#parser.add_argument("-c", "--comment", nargs="?", default=cfg.COMMENT,
#                    help="comment last post with given message (only with -f command)")
args = parser.parse_args()

if args.unfollowers:
    my_bot.get_unfollowers(args.username)

if args.notfollowingback:
    my_bot.get_not_following_back(args.username)

if args.follow:
    my_bot.follow_from_file(args.like)

my_bot.get_not_following_back('mateuszbielawski')

#my_bot.driver.quit()
