"""This program tracks the price of a product on Amazon and saves the price and date to an SQLite database and a .txt
file. It sends me an email notification whenever the price drops, as well as a weekly price update each Sunday."""


import ezgmail, datetime, sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from statistics import mode

driver = webdriver.Chrome()

url = "https://www.amazon.com/Logitech-Wireless-Computer-Mouse-Side/dp/B003NR57BY/ref=sr_1_3?crid=2ZVHP8I4C0FMN&dchild=1&keywords=computer+mouse+wireless+logitech&qid=1587835514&sprefix=computer+mouse%2Caps%2C203&sr=8-3"
# url could easily be an input
driver.get(url)
getPrice = driver.find_element_by_id("priceblock_ourprice")
rawPrice = getPrice.text
strPrice = rawPrice[1:]
newPrice = float(strPrice)


# write price to a txt file
def write_to_text():
    priceList = open("PriceList.txt", "a")
    priceList.write(f"{datetime.date.today()} - ${strPrice}\n")
    priceList.close()


# write price to SQLite DB
def add_to_db():
    dateAndPrice = (str(datetime.date.today()), strPrice)
    conn = sqlite3.connect("amazon_mouse_prices.db")
    c = conn.cursor()
    c.executemany("INSERT INTO prices VALUES (?,?)", (dateAndPrice,))
    conn.commit()
    conn.close()


write_to_text()
add_to_db()

# compare price to last price in txt file; if new price >= old price, pass; if new price < old price, send myself email
with open('PriceList.txt', 'r') as f:
    for line in f:
        secondLastLine = f.readlines()[-2]  # this yields the second to last line in the file, which is the last price
        date, price = secondLastLine.split(" - ")
        tempPrice = price.strip(r"$\n")
        oldPrice = float(tempPrice)
        print(oldPrice)
        if newPrice >= oldPrice:
            pass
        else:
            print(f"Price Update: {newPrice} is less than {oldPrice}")
            ezgmail.send("spencer.a.rodgers@gmail.com", "Price Update",
                         f"The price of the product at {url} has dropped from ${oldPrice} to ${newPrice}.")
f.close()


# find the highest the price has been, the lowest, and the mode
prices = []

with open('PriceList.txt', 'r') as f:
    for line in f:
        date, price = line.split(" - ")
        realPrice = price.strip(r"$\n")
        prices.append(float(realPrice))

maxPrice = max(prices)
minPrice = min(prices)
modePrice = mode(prices)

# plot the prices over time
conn = sqlite3.connect("amazon_mouse_prices.db")

sql_query = pd.read_sql_query("SELECT date, price FROM prices", conn)
df = pd.DataFrame(sql_query, columns=['date', 'price'])

plt.figure(figsize=(8, 5))
plt.title("Price of Wireless Logitech Mouse Over Time (USD)", fontdict={'fontname': 'Arial', 'fontweight': 'bold', 'fontsize': 20})
plt.xlabel("Date (YYYY-MM-DD)", fontdict={'fontsize': 14})
plt.ylabel("Price ($)", fontdict={'fontsize': 14})

plt.plot(sql_query.date, sql_query.price, "bo-", label="Prices")
plt.grid(color='#34abeb', linestyle='--', linewidth=1)
plt.xticks(sql_query.date[::5])
plt.legend()
plt.savefig(f"mouse_price_plot {datetime.date.today()}.png")

conn.close()

# each week, send myself txt file and plot as price report, whether or not any price drops occur
today = datetime.datetime.today().weekday()
if today != 6:
    pass
else:
    ezgmail.send("spencer.a.rodgers@gmail.com", "Weekly Price Report",
                 f"Attached is the weekly price report of the product at {url}."
                 f"\n\nThe highest the price has been is ${maxPrice}, the lowest it has been is ${minPrice}, and the most common price is ${modePrice}.",
                 ["PriceList.txt", f"mouse_price_plot {datetime.date.today()}.png"])
