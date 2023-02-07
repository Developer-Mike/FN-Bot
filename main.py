import time, schedule

from shop.shop import ShopModule
from leaks.leaks import LeaksModule
from vbucks.vbucks import VBucksModule

modules = [ShopModule(), LeaksModule(), VBucksModule()]
for module in modules:
    module.register(schedule)
    print("Initialized module: " + module.__class__.__name__)
    
schedule.run_all()

while True:
    schedule.run_pending()
    time.sleep(10)