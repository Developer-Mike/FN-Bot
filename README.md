# How to run
1. Rename template.env to .env
2. Fill out the .env file
3. Install chromedriver.exe from https://chromedriver.chromium.org/downloads
4. (Optional) Put your 512x512 PNG file inside the ads folder
5. Install the dependencies `pip install -r requirements.txt`
6. Run the main.py file

## Raspberry pi
- Download chromedriver with `sudo apt-get install chromium-chromedriver` (Make sure your chromium is updated `sudo apt install chromium-browser`)
- Set the `CHROMEDRIVER_PATH` in the .env file to `/usr/lib/chromium-browser/chromedriver`
- Download pyvirtualdisplay dependencies `sudo apt-get install xvfb xserver-xephyr tigervnc-standalone-server x11-utils gnumeric`
- To run use `nohup python -u main.py & disown`

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
