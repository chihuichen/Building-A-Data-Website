# data source(usa-used-cars-dataset): https://www.kaggle.com/datasets/doaaalsenani/usa-cers-dataset

import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io # input / output
import pandas as pd
import time
from flask import Flask, request, jsonify
import flask

app = Flask(__name__)
df = pd.read_csv("main.csv")

counter = 0
countsA = 0
countsB = 0


@app.route('/')

def home():
    with open("index.html") as f:
        home = f.read()
    version_a = home.replace("{{color}}", "blue").replace("donate.html", "donate.html?from=A")
    version_b = home.replace("{{color}}", "red").replace("donate.html", "donate.html?from=B")
    global counter
    counter += 1
    if counter <= 10:
        if counter % 2 == 0:
            return version_a
        else:
            return version_b
    else:
        if countsA >= countsB:
            return version_a
        else:
            return version_b


 
@app.route('/browse.html')
def browse():
    table = df.to_html(index=False)
    html = "<html><body><h1>Browse</h1>{}</body></html>".format(table)
    return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^\w+\@\w+\.[a-z]{2,3}$", email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        with open("emails.txt", "r") as f: 
            num_subscribed = len(f.readlines())
        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    return jsonify(f"Stop being so careless! Re-enter a valid email address!") # 3



@app.route("/donate.html")
def donate():
    global countsA, countsB
    donate_header = "<html><body><h1>You are a good person:)</h1></body></html>"
    fromAB = request.args.get("from")
    if fromAB == "A":
        countsA += 1
    if fromAB == "B":
        countsB += 1
        
    return donate_header

    
last_time = {}
visitor_ips = []

@app.route("/browse.json")
def browse_json():
    ip_address = request.remote_addr
    current_time = time.time()

    if ip_address in last_time and (current_time - last_time[ip_address]) < 60:
        return flask.Response("<b>go away</b>", status=429, headers={"Retry-After": "60"})

    last_time[ip_address] = current_time
    if ip_address not in visitor_ips:
        visitor_ips.append(ip_address)

    data = df.to_dict(orient="records")
    return jsonify(data)

@app.route("/visitors.json")
def visitors_json():
    return jsonify(visitor_ips)


@app.route("/dashboard_1.svg")
def plot1():
    brand_prices = df.groupby("brand")["price"].mean().reset_index()
    brand_prices1 = brand_prices.sort_values("price", ascending=False)
    brand_prices2 = brand_prices.sort_values("price", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    plot2 = request.args.get("sort")
    if plot2 == "desc":
        ax.bar(brand_prices1["brand"], brand_prices1["price"], color="r")
        ax.set_title("Average Used Car Price by Brand")
        ax.set_xlabel("Car Brand")
        ax.set_ylabel("Average Price ($)")
        plt.xticks(rotation=45, ha='right', fontsize=7)


        f = io.StringIO() 
        fig.savefig(f, format="svg")
        plt.close()
        return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})


    else:
        ax.bar(brand_prices2["brand"], brand_prices2["price"], color="b")
        ax.set_title("Average Used Car Price by Brand")
        ax.set_xlabel("Car Brand")
        ax.set_ylabel("Average Price ($)")
        plt.xticks(rotation=45, ha='right', fontsize=7)


        f = io.StringIO() 
        fig.savefig(f, format="svg")
        plt.close()
    
        return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})


@app.route("/dashboard_2.svg")
def plot2():
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.scatter(df['mileage'], df['price'], alpha=0.5)
    ax.set_xlabel("Mileage Used")
    ax.set_ylabel("Price ($)")
    ax.set_title("Car Price vs. Mileage Used")
    
    f = io.StringIO()
    fig.savefig(f, format="svg")
    plt.close()
    
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.

