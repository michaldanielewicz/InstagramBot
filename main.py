'''
The InstagramBot.
Check unfollows.

'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

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

        self._change_language()

    def _change_language(self):
        Select(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/section/div[3]/div[3]/nav/ul/li[11]/span/select')).select_by_visible_text('English')

    def _get_user(self, username):
        self.driver.get("https://www.instagram.com/{user}".format(user=username))

    def _load_users_to_follow(self):
        with open('users_to_follow.txt', 'r') as users_to_follow:
            to_follow_list = [username for username in users_to_follow.read().splitlines()]
        print("Users-List from the file have been loaded. Number of records loaded: {}.".format(len(to_follow_list))) 
        return to_follow_list

    def _scroll(self, count_limit, xpath='//div[@class="isgrP"]'):
        pop_up = self.driver.find_element_by_xpath(xpath)
        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", pop_up)
        while True:
            self.driver.execute_script("arguments[0].scrollBy(0,arguments[1])", pop_up, scroll_height)
            usernames_count = len(self.driver.find_elements_by_xpath('//div[@class="PZuss"]/li')) 
            if usernames_count >= count_limit:
                break
            else:
                time.sleep(0.1)
                scroll_height  += scroll_height 
        usernames_list = [username.text for username in self.driver.find_elements_by_xpath('//div[@class="d7ByH"]')]
        return usernames_list

    def is_public(self, username):
        self._get_user(username)
        return not 'This Account is Private' in self.driver.page_source

    def get_followers(self, username = None):
        if username is None:
            self._get_user(self.username)
        else:
            self._get_user(username)
        number_of_followers = int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[1]).text)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()     
        followers_list = self._scroll(number_of_followers)
        print("Number of loaded followers users: {}.".format(len(followers_list)))
        self.driver.back()
        return followers_list

    def get_following(self, username = None):
        if username is None:
            self._get_user(self.username)
        else:
            self._get_user(username)
        number_of_following = int(((self.driver.find_elements_by_xpath('//span[@class="g47SY "]'))[2]).text)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()     
        following_list = self._scroll(number_of_following)
        print("Number of loaded following users: {}.".format(len(following_list)))
        self.driver.back()
        return following_list        

    def get_not_following_back(self, username):
        if self.is_public(username):
            following_list = set(self.get_following(username))
            followers_list = set(self.get_followers(username))
            not_following_back = following_list.difference(followers_list)
            print("You have {} users not following you back".format(len(not_following_back)))
            return not_following_back
        else:
            return ("The user account {} is private, could not get not-following-back list".format(username))

    def get_unfollowers(self, username):
        pass
        #check who unfollows the user 
        #in order to do this it has to be compared some list from the past (for example one day) to current follows list
        #time interval needed

    def follow_user(self, username):
        self._get_user(username)
        self.driver.find_element_by_xpath('//*[contains(text(), "Follow")]').click()

    def like_latest(self, username):
        self._get_user(username) 
        if self.is_public(username):
            self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/article/div/div/div[1]/div[1]').click()
            self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button').click()
        else:
            print("The {user} user is private, can't like latest post.".format(user=username))

    def follow_from_file(self):
        for username in self._load_users_to_follow():
            self.follow_user(username)
            print("The {user} has been followed".format(user=username))
            

print("InstagramBot. ver. 1.0")
my_bot = InstagramBot(cfg.USERNAME,cfg.PASSWORD)
print(my_bot.get_not_following_back("michal_danielewicz"))



