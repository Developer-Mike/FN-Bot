# How to run
1. Rename template.env to .env
2. Fill out the .env file
4. (Optional) Put your 512x512 PNG file inside the ads folder
5. Install the dependencies `pip install -r requirements.txt`
6. Run the main.py file

## Run in background in Linux
`nohup python -u main.py & disown`

## Twitter without API
1. Install chromedriver.exe from https://chromedriver.chromium.org/downloads
#### On Raspberry pi
- Download chromedriver with `sudo apt-get install chromium-chromedriver` (Make sure your chromium is updated `sudo apt install chromium-browser`)
- Set the `CHROMEDRIVER_PATH` in the .env file to `/usr/lib/chromium-browser/chromedriver`
- Download pyvirtualdisplay dependencies `sudo apt-get install xvfb xserver-xephyr tigervnc-standalone-server x11-utils gnumeric`

## Example results
### Shop
![Shop](https://raw.githubusercontent.com/Developer-Mike/FN-Bot/main/example_results/shop.jpg)
### Leaks
![Leaks](https://raw.githubusercontent.com/Developer-Mike/FN-Bot/main/example_results/leaks.jpg)
### V-Bucks
```
New V-Bucks Missions for STW are available!

Canny Valley: 60

#Fortnite
```
