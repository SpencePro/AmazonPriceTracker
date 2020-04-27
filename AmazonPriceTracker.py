"""This program tracks the price of a product on Amazon. Use selenium to get the price; then turn it into a number and
write it to a txt file. Each time the program is run, compare the new price to the last price in the sheet, and if it is
bigger, pass; if it is smaller, send an email to myself with the title Price Update, body of the email being the link to
the product and the new price. Each Sunday, send myself the txt file containing the prices as a weekly price report"""


import ezgmail, datetime
from selenium import webdriver

driver = webdriver.Chrome()

url = "https://www.amazon.com/Logitech-Wireless-Computer-Mouse-Side/dp/B003NR57BY/ref=sr_1_3?crid=2ZVHP8I4C0FMN&dchild=1&keywords=computer+mouse+wireless+logitech&qid=1587835514&sprefix=computer+mouse%2Caps%2C203&sr=8-3"
# url could easily be an input
driver.get(url)
getPrice = driver.find_element_by_id("priceblock_ourprice")
rawPrice = getPrice.text
strPrice = rawPrice[1:]
newPrice = float(strPrice)

# write price to a txt file
priceList = open("PriceList.txt", "a")
priceList.write(strPrice + "\n")
priceList.close()

# compare price to last price in txt file; if new price >= old price, pass; if new price < old price, send myself email
with open('PriceList.txt', 'r') as f:
    for line in f:
        secondLastLine = f.readlines()[-2]  # this yields the second to last line in the file, which is the last price
        oldPrice = float(secondLastLine)
        print(oldPrice)
        if newPrice >= oldPrice:
            pass
        else:
            print(f"Price Update: {newPrice} is less than {oldPrice}")
            ezgmail.send("spencer.a.rodgers@gmail.com", "Price Update", f"The price of the product at {url} has dropped from ${oldPrice} to ${newPrice}.")
f.close()

# each week, send myself txt file as price report, whether or not any price drops occur
today = datetime.datetime.today().weekday()
if today != 6:
    pass
else:
    ezgmail.send("spencer.a.rodgers@gmail.com", "Weekly Price Log", f"Attached is the weekly price log of the product at {url}.", ["PriceList.txt"])
