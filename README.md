# InstagramBot

With this script you can easily check any account for unfollowers, users not following back and many more. Check Code Usage section below for more functions.  

## Why?
I wanted to create this bot to improve my skills in Selenium and Python. Apart from that I was just curious.   
Sure there is an official Instagram API but there are some restrictions in using it so I decided to develop my own software. 

## Technologies
* Python - version 3.8.2
* Selenium - version 3.141.59
* ChromeDriver - version 87.0.4280.88

## Prerequisites
For running my script you have to download ChromeDriver from [developers site](https://chromedriver.chromium.org/). It is important to have the same version as your Chrome browser. After downloading just pust chromedriver.exe in a directory with a main.py.

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
* [-u] *username* check unfollowers* of the user. 
* [-nu] *username* check users not following back the user.
* [-un] *username* check which users are not followed back by the user.
* [-lb] *username* check user most active followers (in the last 10 posts).
* [-gf] *username* check ghostfollowers - followers which haven't liked any of the user posts.
* [-nf] gives all these outputs without followers value.
* [-f] follow each record in txt file.
  
For example running script:
```bash
python main.py -nu michal_danielewicz
```
will find users not following me back with followers value each. 
All results are saved to *.txt file in /logs sorted by followers amount.
*unfollowers - people that followed you in the past but decided to unfollow you. To get it working properly you should have scanned your list with InstagramBot one time in the past.  

## Features
List of features ready and TODOs for a future development.

### Ready:
* Remember login credentials - skip login (optional).
* Disable images for a better performance (optional).
* List not-following-back for the user.
* List users not followed by the user.
* Show users follows-number.
* List unfollowers of the user - checks differences between lists from a past and current.
* Followers leaderboard - most active followers of the user.
* Ghost followers - people who did not like any of the user photo.
* Follow people from follow list.

### To-do list:
* Save results to *.csv file.
* Like posts from given user.
* Comment function with given text.

## Status
Project is: _completed_.
In any cases of errors please send me a message! Due to some changes in html code by Instagram Team it is possible that some action will not perform. 

## Contact
Created by [@michaldanielewicz](https://michaldanielewicz.github.io/) - feel free to contact me!

