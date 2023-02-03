import time, schedule

from shop.shop import ShopModule

modules = [ShopModule()]
for module in modules:
    module.register(schedule)
    print("Initialized module: " + module.__class__.__name__)

while True:
    schedule.run_pending()
    time.sleep(10)