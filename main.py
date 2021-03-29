"""Scraping script  operating on Instagram.

Check unfollows.
Check non-following back users.
Check users not followed back.
Save to the file with followers number. (optional)
Also operates simple task like following
people from file or like posts.
"""

import time
import argparse
import os.path
from math import trunc
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config as cfg
import exceptions


class InstagramBot:
    """
    Main bot class.

    Attributes:
        driver: module derivated from Selenium, operates Google Chrome.
        username: account username provided in config.py.
        password: account password provided in config.py.
    """

    def __init__(self, username, password,
                 skip_login, disable_images):
        """Inits InstagramBot and setups driver."""
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
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.implicitly_wait(10)
        self.driver.get('https://www.instagram.com/accounts/login/')
        if self.driver.current_url != ('https://www.instagram.com/'):
            self._log_in()
        self._change_language()

    def _log_in(self):
        """Log in as username and password given in config.py."""
        # Pass cookies.
        self.driver.find_element_by_xpath(
            '/html/body/div[2]/div/div/div/div[2]/button[1]').click()
        # Insert login and password.
        self.driver.find_element_by_xpath(
            '//input[@name=\"username\"]').send_keys(self.username)
        self.driver.find_element_by_xpath(
            '//input[@name=\"password\"]').send_keys(self.password)
        # Click login.
        self.driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div/div[3]').click()
        # Pass remember login popoup.
    #    self.driver.find_element_by_xpath(
    #        '//*[@id="react-root"]/section/main/div/div/div/section/div/button').click()
        # Pass notification popup.
    #    self.driver.find_element_by_xpath(
    #        '/html/body/div[4]/div/div/div/div[3]/button[2]').click()


    def _change_language(self):
        """Changes language to english - crucial for some methods."""
        Select(self.driver.find_element_by_xpath
               ('//*[@id="react-root"]/section/main/section/div[3]/div[3]/nav/ul/li[11]/span/select'))\
            .select_by_visible_text('English')

    def _get_user(self, username):
        """Gets user page."""
        self.driver.get(f'https://www.instagram.com/{username}')
        if "this page isn't available" in self.driver.page_source:
            raise exceptions.NoSuchUserException(username)

    def _is_public(self, username):
        """Checks if userpage is public (or just available)."""
        self._get_user(username)
        return not 'This Account is Private' in self.driver.page_source

    def _get_how_many_followers(self, username):
        """Gets number of followers of user."""
        self._get_user(username)
        how_many_followers = self.driver.find_elements_by_xpath(
            '//span[@class="g47SY "]')[1].text
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

    def _scroll_likes(self):
        """Gets number of likes under post."""
        # Click likes list.
        self.driver.find_element_by_xpath(
            '/html/body/div[5]/div[2]/div/article/div[3]/section[2]/div/div/button').click()        
        pop_up = self.wait.until(
            EC.presence_of_element_located((By.XPATH, 
                '/html/body/div[5]/div[2]/div/article/div[3]/section[2]/div/div/button')))

        def get_current_scroll_height():
            return self.driver.execute_script(
                'return arguments[0].scrollHeight', pop_up)

        def scroll_into(element):
            self.driver.execute_script(
                'arguments[0].scrollIntoView()', element)

        users_that_liked_post = []
        window_height_changed = time.perf_counter()
        while True:
            scroll_height = get_current_scroll_height()
            for element in self.driver.find_elements_by_xpath('//a[@class="FPmhX notranslate MBL3Z"]'):
                users_that_liked_post.append(element.text)
                last_element = element
            scroll_into(last_element)
            time.sleep(1)
            if scroll_height != get_current_scroll_height():
                window_height_changed = time.perf_counter()
            if time.perf_counter() - window_height_changed > 3:
                break
        # Close likes list.
        self.driver.find_element_by_xpath(
            '/html/body/div[6]/div/div/div[1]/div/div[2]/button').click()
        return list(set(users_that_liked_post))

    def _scroll_popup(self):
        """Scrolls through following/followers pop-up window."""
        pop_up = self.driver.find_element_by_xpath('//div[@class="isgrP"]')

        def get_current_scroll_height():
            return self.driver.execute_script('return arguments[0].scrollHeight', pop_up)

        def scroll_down(height_to_scroll):
            self.driver.execute_script('arguments[0].scrollBy(0,arguments[1])',
                                       pop_up, height_to_scroll)

        window_height = 0
        start_scrolling = time.perf_counter()
        while True:
            scroll_down(get_current_scroll_height())
            if window_height != get_current_scroll_height():
                window_height = get_current_scroll_height()
                window_height_change = time.perf_counter()
            if time.perf_counter() - window_height_change > 3:
                end_scrolling = time.perf_counter()
                break
        print(f'Scroll ended. It took {trunc(end_scrolling - start_scrolling)} seconds.')
        usernames_list = [(username.text).replace('\nVerified', '')
                          for username in self.driver.find_elements_by_xpath('//div[@class="d7ByH"]')]
        return usernames_list

    def _get_non_following_back(self, username, first_list, second_list, get_followers_value):
        """Gets non-following back. It's just a difference between first and second list."""
        if self._is_public(username):
            if get_followers_value == True:
                not_following_back = []
                print("Getting number of followers for each non-following user...")
                for user in first_list.difference(second_list):
                    not_following_back.append(
                        [user, self._get_how_many_followers(user)])
                not_following_back.sort(key=lambda user: user[1])
            else:
                not_following_back = list(first_list.difference(second_list))
        else:
            raise exceptions.UserAccountPrivateException(username)
        return not_following_back

    def get_following(self, username):
        """Gets users followed by given user."""
        number_of_following_on_page = self._get_how_many_following(username)
        self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()
        print('Getting following list...')
        following_list = self._scroll_popup()
        print(f'Number of loaded following users: {len(following_list)}. '
              f'{number_of_following_on_page - len(following_list)} users missed.')
        return following_list

    def get_followers(self, username, save_to_file=False):
        """Gets users following given user."""
        number_of_followers_on_page = self._get_how_many_followers(username)
        self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()
        print('Getting followers list...')
        followers_list = self._scroll_popup()
        print(f'Number of loaded followers users: {len(followers_list)}. ' +
              f'{number_of_followers_on_page - len(followers_list)} users missed.')
        if save_to_file:
            with open(f'logs/followers_{username}.txt', 'w') as file:
                for user in followers_list:
                    file.write(f'{user}\n')
            print(
                f'Followers ({number_of_followers_on_page}) have been saved to the file.')
        return followers_list

    def get_not_following_back_users(self, username, get_followers_value=True):
        """Gets users that are followed but are not following back given user."""
        following_list = set(self.get_following(username))
        followers_list = set(self.get_followers(username))
        not_following_back = self._get_non_following_back(username, following_list,
                                                          followers_list, get_followers_value)
        with open(f'logs/not_following_back_{username}.txt', 'w') as file:
            for user in not_following_back:
                file.write(f'{user}\n')
        print(f"{username} has {len(not_following_back)} not following back users. "
              f"That's {trunc(len(not_following_back)/len(following_list)*100)}% of the list. "
              "Results are saved to the file in /logs.")

    def get_user_not_following_back(self, username, get_followers_value=True):
        """Gets users that are not followed back by user."""
        following_list = set(self.get_following(username))
        followers_list = set(self.get_followers(username))
        not_following_back = self._get_non_following_back(username, followers_list,
                                                          following_list, get_followers_value)
        with open(f'logs/{username}_not_following_back.txt', 'w') as file:
            for user in not_following_back:
                file.write(f'{user}\n')
        print(f"{username} is not following back {len(not_following_back)} users. "
              f"That's {trunc(len(not_following_back)/len(followers_list)*100)}% of the list. "
              "Results are saved to the file in /logs.")

    def get_unfollowers(self, username, get_followers_value=True):
        """Gets users that had followed user but unfollowed after some time."""
        if self._is_public(username):
            try:
                past_followers_dir = (f'logs/followers_{username}.txt')
                with open(past_followers_dir, 'r') as file:
                    past_followers = {follower.rstrip() for follower in file}
                print(f'Succesfully read {past_followers_dir} '
                      f'last modified on: {time.ctime(os.path.getmtime(past_followers_dir))}')
                current_followers = set(self.get_followers(username))
                unfollowers = past_followers.difference(current_followers)
                active_unfollowers = []
                deleted_users = []
                for unfollower in unfollowers:
                    try:
                        self._get_user(unfollower)
                        if get_followers_value:
                            active_unfollowers.append(
                                [unfollower, self._get_how_many_followers(unfollower)])
                        else:
                            active_unfollowers.append(unfollower)
                    except exceptions.NoSuchUserException:
                        deleted_users.append(unfollower)
                active_unfollowers.sort(key=lambda user: user[1])
                with open(f'logs/unfollowers_{username}.txt', 'w') as file:
                    for user in active_unfollowers:
                        file.write(f'{user}\n')
                print(f'{username} has {len(active_unfollowers)} active unfollower(s). '
                      'Results saved to the file in /logs. '
                      f'User(s) that could not be found: {deleted_users}')
            except OSError:
                answer = ''
                while answer not in ('Y', 'N'):
                    answer = input(f'Past followers for {username} not found. '
                                   f'Do you want to create it right now? (Y/N): '.upper())
                if answer == "Y":
                    self.get_followers(username, save_to_file=True)
                else:
                    print(
                        'Could not get unfollowers list without previous followers list')
        else:
            raise exceptions.UserAccountPrivateException(username)

    def get_leaderboard(self, username, number_of_posts=10, count_occurences=True):
        """Gets likes from each post on user page and create top-interactions-followers board."""
        if self._is_public(username):
            number_of_posts_on_page = self._get_how_many_posts()
            if number_of_posts > number_of_posts_on_page or number_of_posts == 0:
                number_of_posts = number_of_posts_on_page
            number_of_clicks = 0
            skipped_posts = 0
            users_list = []
            # Click latest post.
            self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div').click()
            while True:
                try:
                    users_list += self._scroll_likes()
                except NoSuchElementException:
                    skipped_posts += 1
                if number_of_clicks == number_of_posts-1:
                    break
                self.driver.find_element_by_css_selector(
                    'a.coreSpriteRightPaginationArrow').click()
                number_of_clicks += 1
            print(f'Fetched posts: {number_of_posts-skipped_posts}. Skipped: {skipped_posts}.')
            if count_occurences:
                counted_occurences_users = [
                    [user, users_list.count(user)] for user in set(users_list)]
                # Sort list from most likes.
                counted_occurences_users.sort(key=lambda user: user[1])
                with open(f'logs/leaderboard_{username}.txt', 'w') as file:
                    for user in counted_occurences_users:
                        file.write(f'{user}\n')
                print(f'{username} has total number: {len(users_list)} of likes '
                    f'in {len(number_of_posts)} posts. '
                    'Results saved to the file in /logs. '
                    f'The most active user: {counted_occurences_users[-1][0]}, '
                    f'with total: {counted_occurences_users[-1][1]} likes.')
            else:
                return users_list
        else:
            raise exceptions.UserAccountPrivateException(username)

    def get_ghostfollowers(self, username):
        """Gets ghostfollowers - followers that do not liked any post."""
        if self._is_public(username):
            interactive_users = set(self.get_leaderboard(username, 0, False))
            followers = set(self.get_followers(username))
            ghostfollowers_list = followers.difference(interactive_users)
            with open(f'logs/ghostfollowers_{username}.txt', 'w') as file:
                for user in ghostfollowers_list:
                    file.write(f'{user}\n')
            print(f'{username} has total number: {len(ghostfollowers_list)} of ghostfollowers. '
                'Results saved to the file in /logs.')
        else:
            raise exceptions.UserAccountPrivateException(username)

    # TODO: ensure print if followed before
    # TODO: find another way to find "follow" button
    def follow_user(self, username):
        '''Follows given user.'''
        if self._is_public(username):
            try:
                self.driver.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button').click()
                print(f'{username} has been followed.')
                # if followed before print that info here
            except NoSuchElementException:
                try:
                    self.driver.find_element_by_xpath(
                        '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/div/div/div/span/span[1]/button').click()
                    print('{username} has been followed.')
                except NoSuchElementException:
                    print(f'Could not follow {username}.')
        else:
            try:
                self.driver.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/button').click()
            except NoSuchElementException:
                print(f'Could not follow {username}.')

    def like_latest_post(self, username):
        """Likes latest post of desired user."""
        if self._is_public(username):
            self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div').click()
            self.driver.find_element_by_xpath(
                '/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button').click()
        else:
            raise exceptions.UserAccountPrivateException(username)

    def comment_latest_post(self, username, message):
        """Comment latest post of desired user with given message."""
        if self._is_public(username):
            self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div').click()
            self.driver.find_element_by_xpath(
                '/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form').click()
            self.driver.find_element_by_xpath(
                "/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea").send_keys(message)
            self.driver.find_element_by_xpath(
                '/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/button').click()
        else:
            raise exceptions.UserAccountPrivateException(username)

    # TODO: add how many users have been followed at the end
    # TODO: comment with desired message
    def follow_from_file(self, like_latest_post):
        """Follows users given in users_to_follow.txt file."""
        with open('users_to_follow.txt', 'r') as file:
            to_follow_list = file.read().splitlines()
        print(
            f'Number of records loaded from the file: {len(to_follow_list)}.')
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


# TODO: add parsing argument for comment last post
# TODO: add argument for number of checked post for leaderboard
parser = argparse.ArgumentParser(prog='main.py', description='InstagramBot')
parser.add_argument("username", nargs="?", default=cfg.USERNAME,
                    type=str, help="the target user")
parser.add_argument("-u", "--unfollowers", action="store_true",
                    help="check unfollowers of the user")
parser.add_argument("-nu", "--notfollowingbackusers", action="store_true",
                    help="check users not following back the user")
parser.add_argument("-un", "--usernotfollowingback", action="store_true",
                    help="check who is the user not following back")
parser.add_argument("-nf", "--nofollowersvalue", action="store_false",
                    help="do not check followers value")
parser.add_argument("-lb", "--leaderboard", action="store_true",
                    help="check the most active followers")
parser.add_argument("-gf", "--ghostfollowers", action="store_true",
                    help="check ghostfollowers")

parser.add_argument("-f", "--follow", action="store_true",
                    help="follow users from the file")
parser.add_argument("-l", "--like", action="store_true",
                    help="like latest post (only with -f command)")
# parser.add_argument("-c", "--comment", nargs="?", default=cfg.COMMENT,
#                    help="comment last post with given message (only with -f command)")
args = parser.parse_args()
my_bot = InstagramBot(cfg.USERNAME, cfg.PASSWORD,
                      cfg.SKIP_LOGIN, cfg.DISABLE_IMAGES)

if args.unfollowers:
    my_bot.get_unfollowers(args.username, args.nofollowersvalue)

if args.notfollowingbackusers:
    my_bot.get_not_following_back_users(args.username, args.nofollowersvalue)

if args.usernotfollowingback:
    my_bot.get_user_not_following_back(args.username, args.nofollowersvalue)

if args.leaderboard:
    my_bot.get_leaderboard(args.username)

if args.ghostfollowers:
    my_bot.get_ghostfollowers(args.username)

if args.follow:
    my_bot.follow_from_file(args.like)

my_bot.driver.quit()
