# InstagramBot
> I want to create a bot that will automate some actions like follow users, like posts, check unfollows and not-following-back lists. \
> It does not use official Instagram API.

## General info
I wanted to create this bot to improve my skills in Selenium and Python. Apart from that I was just curious who unfollowed my from my friends. \
Unfortunately most apps and sites that are available online require you to give them your main account password. With this bot you can use any 
account (or yours, it isn't pushed outside) and check any user. 

## Technologies
* Python - version 3.8.2
* Selenium - version 3.141.59
* ChromeDriver - version 87.0.4280.88

## Prerequisites
For running my script you have to download ChromeDriver from [developers site](https://chromedriver.chromium.org/).  

## Config
Before first use it is necessary to edit **config.py**.  
Enter your main user account details or newly created. Notice that if you would like to check private account you have to get permissions for following user.
```bash
# Enter account username:
USERNAME = "    " 
# Enter account password:
PASSWORD = "    "
```
And you are ready to run **main.py**.

## Code usage
* [-u] *username* unfollowers for a given user.
* [-nu] *username* check users not following back given user.
* [-un] *username* check which users are not followed back by user.
* [-nf] gives ouput without followers value.
* [-lb] *username* check user most active followers (in last 10 posts).
* [-f] follow each record in txt file.
  
For example running script:
```bash
python main.py -nu michal_danielewicz
```
will find users not following me back with followers value each. :) 

## Features
List of features ready and TODOs for future development.

### Ready:
* Remember login credentials - skip login (optional).
* Disable images for a better performance (optional).
* List not-following-back for given user.
* List users not followed by given user.
* Show users follows number and save results to the file (optional).
* List unfollowers for given user. (Checks for differences between followers list from the past and current.)
* Followers leaderboard (most active followers).
* Follow people from follow list.

### To-do list:
* Ghost followers (people who did not like any of your photo).
* Like posts from given user.
* Comment function with given text.

## Status
Project is: _in progress_.

## Contact
Created by [@michaldanielewicz](https://michaldanielewicz.github.io/) - feel free to contact me!

