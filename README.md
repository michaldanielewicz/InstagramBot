# InstagramBot
> I want to create a bot that will automate some actions like follow users, like posts, check unfollows and not-following-back lists. \
> I don't use official Instagram API.

## General info
I wanted to create this bot to improve my skills in Selenium and Python. Apart from that I was just curious who unfollowed my from my friends. \
Unfortunately most apps and sites that are available online require you to give them your main account password. With this bot you can use any 
account (or yours, it isn't pushed outside) and check any user. 

## Technologies
* Python - version 3.8.2
* Selenium - version 3.141.59
* ChromeDriver - version 87.0.4280.88

## Setup
Download ChromeDriver from [developers site](https://chromedriver.chromium.org/).\
You have to edit config.py and enter you accounts details. It can be newly created account just for bot-related purposes or you main account. If you use your real account details your account can be private to check unfollows. In another case you have to change it for a moment for bot be able to check unfollows. :) Watch out for anormal activity that Instagram can trace.\
Change desired username in my_bot.get_not_following_back and run main.py.

## Features
List of features ready and TODOs for future development. \ \
Ready:
* List not-following-back for given user and save results to the file.
* List unfollowers for given user. (Check for differences between followers list from the past and current.)
* Follow people from follow list.

To-do list:
* Like posts from given user.
* Auto-like feature. 
* Auto-follow feature.
* Check users you are not following, but they are following you.
* Give arguments in cmd shell.
* Decide to like post or not based on some factors (like sex, number of likes etc.).
* Modify scrolling list to be more efficient and error-proof.
* Add some random timing delays to not get caught using automated software.
* Save cookies for later use. (Skip login).

## Status
Project is: _in progress_.

## Contact
Created by [@michaldanielewicz](https://michaldanielewicz.github.io/) - feel free to contact me!

