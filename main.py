'''
The InstagramBot.
Check unfollows.

'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from math import trunc

#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions
import time
import config as cfg

class InstagramBot:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.get("https://www.instagram.com/accounts/login/")
        self.username = username
        self.password = password
        #pass cookies
        self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/button[1]').click()
        #insert login and password
        self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(username)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(password)
        #click login
        self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]').click()
        #pass rember login popoup
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button').click()
        #pass notification popup
        self.driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]').click()
        #change language
        self._change_language()
        print("Ready.")

    def _change_language(self):
        Select(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/section/div[3]/div[3]/nav/ul/li[11]/span/select')) \
            .select_by_visible_text('English')

    def _get_user(self, username):
        self.driver.get("https://www.instagram.com/{user}".format(user=username))
        
    def _is_public(self, username):
        self._get_user(username)
        return not 'This Account is Private' in self.driver.page_source

    def _scroll_popup(self, count_limit, xpath):
        self.driver.find_element_by_xpath(xpath).click()  
        pop_up = self.driver.find_element_by_xpath('//div[@class="isgrP"]')
        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", pop_up)
        start_task = time.perf_counter()
        print("Scroll started.")
        while True:
            self.driver.execute_script("arguments[0].scrollBy(0,arguments[1])", pop_up, scroll_height)
            scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", pop_up) 
            usernames_count = len(self.driver.find_elements_by_xpath('//div[@class="PZuss"]/li')) 
            end_task = time.perf_counter()
            if usernames_count >= count_limit or (end_task - start_task) > 80 :
                print("Scroll ended. It took {timer} seconds. Usernames count: {count}." \
                    .format(timer = end_task-start_task, count = usernames_count))
                break
            else:
                scroll_height  += scroll_height 
                continue
        usernames_list = [username.text for username in self.driver.find_elements_by_xpath('//div[@class="d7ByH"]')]
        return usernames_list

    def get_following(self, username = None):
        if username is None:
            self._get_user(self.username)
        else:
            self._get_user(username)
        number_of_following_on_page = int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[2]).text)  
        following_list = self._scroll_popup(number_of_following_on_page, '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a')
        print("Number of loaded following users: {}.".format(len(following_list)))
        self.driver.back()
        return following_list        

    def get_followers(self, username = None, save_to_file = False):
        if username is None:
            self._get_user(self.username)
        else:
            self._get_user(username)
        number_of_followers_on_page = int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[1]).text)
        followers_list = self._scroll_popup(number_of_followers_on_page, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')
        print("Number of loaded followers users: {}.".format(len(followers_list)))
        self.driver.back()
        if save_to_file:
            with open('logs/followers_{user}.txt'.format(user=username), 'w') as file:
                for user in followers_list:
                    file.write('{}\n'.format(user))
            print("Followers have been saved to the file.")
        return followers_list

    def get_not_following_back(self, username):
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
            return ("The user account {} is private, could not get not-following-back list".format(username))

    def get_unfollowers(self, username):
        if self._is_public(username):
            try:
                past_followers_file_dir = ('logs/followers_{user}.txt'.format(user=username))
                with open(past_followers_file_dir, 'r') as file:
                    print('Succesfully read {} file'.format(past_followers_file_dir))
                    past_followers = set([follower.rstrip() for follower in file])
                current_followers = set(self.get_followers(username))
                unfollowers = past_followers.difference(current_followers)
                print("{user} has {number} unfollowers: {users}".format(user=username, number=len(unfollowers), users = unfollowers))
            except OSError:
                print("There is no saved copy of followers list for this user. Do you want to create one right now? (Y/N)")
                self.get_followers(username, save_to_file = True)
        else:
            return ("The user account {} is private, could not get not-following-back list".format(username))

    def follow_user(self, username):
        self._get_user(username)
        self.driver.find_element_by_xpath('//*[contains(text(), "Follow")]').click()

    def like_latest(self, username):
        self._get_user(username) 
        if self._is_public(username):
            self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/article/div/div/div[1]/div[1]').click()
            self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button').click()
        else:
            print("The {user} user is private, can't like latest post.".format(user=username))

    def follow_from_file(self):
        with open('users_to_follow.txt', 'r') as users_to_follow:
            to_follow_list = [username for username in users_to_follow.read().splitlines()]
        print("Users-List from the file have been loaded. Number of records loaded: {}.".format(len(to_follow_list))) 
        for username in to_follow_list:
            self.follow_user(username)
            print("The {user} has been followed".format(user=username))
            

print("InstagramBot. ver. 1.0")
my_bot = InstagramBot(cfg.USERNAME,cfg.PASSWORD)
my_bot.get_unfollowers("michal_danielewicz")



