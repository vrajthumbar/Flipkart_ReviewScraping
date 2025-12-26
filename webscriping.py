import os
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pymongo

app = Flask(__name__)
    
@app.route("/", methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            DRIVER_PATH = r"D:\python\chromedriver.exe"
            chrome_options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(options=chrome_options)
            searchString = request.form['content'].replace(" ", "")
            url = f"https://www.flipkart.com/search?q=" + searchString
            driver.get(url)
            page_source = driver.page_source
            flipkart_html = bs(page_source, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            driver.quit()
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'no name'
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'
                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                      print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            client = pymongo.MongoClient("mongodb+srv://webscriping:webscriping@cluster0.uqxl37k.mongodb.net/?retryWrites=true&w=majority")
            db = client['pwskil']
            coll_webscriping = db["webscriping"]
            coll_webscriping.insert_many(reviews)
            return render_template('result.html', reviews=reviews[0:(len(reviews) - 1)])

        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
       return render_template('index.html')
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
