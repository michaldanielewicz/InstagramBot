"""Scraper and bot opearating on Instagram.

InstagramBot able to check unfollows for a given user
or check users not following back. Also operates simple
task like following people from file or like posts.
"""

from math import trunc
import time
import argparse

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions

import config as cfg

class InstagramBot:
    """
    Main bot class.

    Attributes:
        driver: module derivated from selenium.
        username: account username provided in config.py.
        password: account password provided in config.py.
    """

    def __init__(self, username, password, skip_login):
        """Inits InstagramBot with driver setup."""
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.username = username
        self.password = password
        if not skip_login:
            self.driver.get("https://www.instagram.com/accounts/login/")
            #pass cookies
            self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/button[1]').click()
            #insert login and password
            self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(self.username)
            self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(self.password)
            #click login
            self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]').click()
            #pass rember login popoup
            self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button').click()
            #pass notification popup
            self.driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]').click()
            #change language
            self._change_language()
        else:
            self.driver.get("https://www.instagram.com")

    def _change_language(self):
        """Changes language to english."""
        Select(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/section/div[3]/div[3]/nav/ul/li[11]/span/select')) \
            .select_by_visible_text('English')

    #TODO: check if user exists, if not raise error
    def _get_user(self, username):
        """Gets desired user site."""
        self.driver.get("https://www.instagram.com/{}".format(username))

    def _is_public(self, username):
        """Checks if userpage is public."""
        self._get_user(username)
        return not 'This Account is Private' in self.driver.page_source

    def _scroll_popup(self, count_limit, xpath):
        """Scrolls through following/followers pop-up window."""
        self.driver.find_element_by_xpath(xpath).click()
        pop_up = self.driver.find_element_by_xpath('//div[@class="isgrP"]')
        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", pop_up)
        start_task = time.perf_counter()
        while True:
            self.driver.execute_script("arguments[0].scrollBy(0,arguments[1])", pop_up, scroll_height)
            scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", pop_up)
            usernames_count = len(self.driver.find_elements_by_xpath('//div[@class="PZuss"]/li'))
            end_task = time.perf_counter()
            if usernames_count >= count_limit or end_task - start_task > 80 :
                print("Scroll ended. It took {timer} seconds. Usernames counted: {count}." \
                    .format(timer = end_task-start_task, count = usernames_count))
                break
            scroll_height += scroll_height
        usernames_list = [username.text for username in self.driver.find_elements_by_xpath('//div[@class="d7ByH"]')]
        return usernames_list

    def get_following(self, username=None):
        """Gets users followed by given user."""
        if username is None:
            self._get_user(self.username)
        else:
            self._get_user(username)
        number_of_following_on_page = int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[2]).text)
        following_list = self._scroll_popup(number_of_following_on_page, '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a')
        print("Number of loaded following users: {len_following_list}. {number_on_page} users missed." \
            .format(len_following_list = len(following_list), number_on_page = number_of_following_on_page - len(following_list)))
        self.driver.back()
        return following_list

    def get_followers(self, username=None, save_to_file=False):
        """Gets users following given user."""
        if username is None:
            self._get_user(self.username)
        else:
            self._get_user(username)
        number_of_followers_on_page = int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[1]).text)
        followers_list = self._scroll_popup(number_of_followers_on_page, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')
        print("Number of loaded followers users: {len_followers_list}. {number_on_page} users missed.". \
            format(len_followers_list = len(followers_list), number_on_page = number_of_followers_on_page - len(followers_list)))
        if save_to_file:
            with open('logs/followers_{user}.txt'.format(user=username), 'w') as file:
                for user in followers_list:
                    file.write('{}\n'.format(user))
            print("Followers have been saved to the file.")
        self.driver.back()
        return followers_list

    def get_not_following_back(self, username):
        """Gets user that are followed but are not following back given user."""
        if self._is_public(username):
            following_list = set(self.get_following(username))
            followers_list = set(self.get_followers(username))
            not_following_back = following_list.difference(followers_list)
            with open('logs/not_following_back_{}.txt'.format(username), 'w') as file:
                for user in not_following_back:
                    file.write('{}\n'.format(user.replace('\nVerified','')))
            print("{user} has {number} not following back users. That's {percent}% of the following list. Results saved to a file." \
                .format(user=username, number=len(not_following_back), percent=trunc(len(not_following_back)/len(following_list)*100)))
        else:
            print("The user account {} is private, could not get not-following-back list".format(username))

    #TODO: add module that will check if unfollower has a deleted account, add posibility to save file (oserror)
    def get_unfollowers(self, username):
        """Gets users that had followed given user but unfollowed after some time."""
        if self._is_public(username):
            try:
                past_followers_file_dir = ('logs/followers_{user}.txt'.format(user=username))
                with open(past_followers_file_dir, 'r') as file:
                    print('Succesfully read {} file'.format(past_followers_file_dir))
                    #past_followers = set([follower.rstrip() for follower in file])
                    past_followers = {follower.rstrip() for follower in file}
                current_followers = set(self.get_followers(username))
                unfollowers = past_followers.difference(current_followers)
                print("{user} has {number} unfollowers: {users}".format(user=username, number=len(unfollowers), users = unfollowers))
            except OSError:
                print("There is no saved copy of followers list for this user. Do you want to create one right now? (Y/N)")
                self.get_followers(username, save_to_file=True)
        else:
            print("The user account {} is private, could not get not-following-back list".format(username))

    #TODO: change xpath, check is it working with private accounts, make it quicker if followed before
    def follow_user(self, username):
        """Follows given user."""
        self._get_user(username)
        try:
            self.driver.find_element_by_xpath('//*[contains(text(), "Follow")]').click()
            print("{} has been followed.".format(username))
        except:
            print("{} had been followed before. Skip.".format(username))

    def like_latest(self, username):
        """Likes latest post of desired user."""
        self._get_user(username)
        if self._is_public(username):
            self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/article/div/div/div[1]/div[1]').click()
            self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button').click()
        else:
            print("The {user} user is private, can't like latest post.".format(user=username))

    def follow_from_file(self):
        """Follows users given in users_to_follow.txt file."""
        with open('users_to_follow.txt', 'r') as file:
            #to_follow_list = [username for username in file.read().splitlines()]
            to_follow_list = file.read().splitlines()
        print("Users list from the file have been loaded. Number of records loaded: {}.".format(len(to_follow_list)))
        for username in to_follow_list:
            self.follow_user(username)
        print("Users have been followed.")

parser = argparse.ArgumentParser(description="check who unfollowed you or are not following you back")
parser.add_argument("-u", "--unfollowers", type=str, help="check unfollowers of the given username")
parser.add_argument("-n", "--notfollowingback", type=str, help="check users not following back the given username")
parser.add_argument("-f", "--followusers", action="store_true", help="follow users from the file")
args = parser.parse_args()

if args.unfollowers:
    check_user = args.unfollowers
    my_bot = InstagramBot(cfg.USERNAME, cfg.PASSWORD, cfg.SKIP_LOGIN)
    my_bot.get_unfollowers(check_user)

if args.notfollowingback:
    check_user = args.notfollowingback
    my_bot = InstagramBot(cfg.USERNAME, cfg.PASSWORD, cfg.SKIP_LOGIN)
    my_bot.get_not_following_back(check_user)

if args.followusers:
    my_bot = InstagramBot(cfg.USERNAME, cfg.PASSWORD, cfg.SKIP_LOGIN)
    my_bot.follow_from_file()

#add optional argument - user, if no user given assume username given as account given in configS
