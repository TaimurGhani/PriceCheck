import requests, json
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from semantics3 import Products
import MySQLdb


app = Flask(__name__)

#Set up a client to talk to the Semantics3 API using your Semantics3 API Credentials
sem3 = Products(
	api_key = "SEM322EF6FCE667BE9ED88826363DE85E0A2",
	api_secret = "NmI4OTU5ZmVjZTVkZDNlODhmYmZmN2Q2ZTkyMmQ2OTY"
)

#Configure the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql9240288:SEzfYffbfL@sql9.freemysqlhosting.net:3306/sql9240288'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class WishList(db.Model):
	#__tablename__ = "wish_list"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	price = db.Column(db.String(10))
	url = db.Column(db.String(1000))

"""
	Takes in a string input and
	return it as a dictionary.
	Used to add to a databse
"""
def stringToDict(s):
	s = s.replace(", \'", ": ").replace("{", "").replace("}", "")
	s = s.split(': ')
	for elem in s:
		print(elem)
		print()
	if (s[1].replace("\"", "")[0] == "\'"):
		s[1] = s[1].replace("\"", "")[1:-1]
	s = {
				"name": s[1].replace("\"", ""),
				"price": s[3].replace("\'", ""),
				"image": s[5][1:-1],
				"url": s[7][1:-1]
	}
	print(s)
	return s

#Home page
@app.route('/', methods=['GET', 'POST'])
def home():
	#default variables
	walmartInfo = {"name": "", "price": "", "image":"../static/sorry.jpg", "url": ""}
	targetInfo = {"name": "", "price": "", "image":"../static/sorry.jpg", "url": ""}
	amazonInfo = {"name": "", "price": "", "image":"../static/sorry.jpg", "url": ""}
	return render_template('home.html', walmartInfo=walmartInfo, targetInfo=targetInfo, amazonInfo=amazonInfo)

#Search and Post the results of items from each store
@app.route('/search', methods=['GET','POST'])
def search():
	#default variables
	walmartInfo = {"name": "", "price": "", "image":"../static/sorry.jpg", "url": ""}
	targetInfo = {"name": "", "price": "", "image":"../static/sorry.jpg", "url": ""}
	amazonInfo = {"name": "", "price": "", "image":"../static/sorry.jpg", "url": ""}
	#when a user inputs data
	if (request.method == 'POST'):
		searchFor = request.form.get('productName')
		sem3.products_field("search", searchFor)
		#Walmart
		sem3.products_field("site", "walmart.com")
		r = sem3.get_products()
		try:
			walmartInfo = {
				"name": r["results"][0]["name"],
				"price": "$"+r["results"][0]["price"],
				"image": r["results"][0]["images"][0],
				"url": r["results"][0]["sitedetails"][0]["url"]
			}
		except Exception:
			pass
		#Target
		sem3.products_field("site", "target.com")
		r = sem3.get_products()
		try:
			targetInfo = {
				"name": r["results"][0]["name"],
				"price": "$"+r["results"][0]["price"],
				"image": r["results"][0]["images"][0],
				"url": r["results"][0]["sitedetails"][0]["url"]
			}
		except Exception:
			pass
		#Amazon
		sem3.products_field("site", "amazon.com")
		r = sem3.get_products()
		try:
			amazonInfo = {
				"name": r["results"][0]["name"],
				"price": "$"+r["results"][0]["price"],
				"image": r["results"][0]["images"][0],
				"url": r["results"][0]["sitedetails"][0]["url"]
			}
		except Exception:
			pass
	#render the home page and return the data for each store
	return render_template('home.html', walmartInfo=walmartInfo, targetInfo=targetInfo, amazonInfo=amazonInfo)

#Add to Wish List
@app.route('/add', methods=['POST'])
def addToWishList():
	walButton = request.form.get('walWish')
	targButton = request.form.get('targWish')
	amButton = request.form.get('amWish')
	if (walButton is not None and walButton != "{'name': '', 'price': '', 'image': '../static/sorry.jpg', 'url': ''}"):
		try:
			walmartInfo = json.loads(walButton.replace("'", "\""))
			print(walmartInfo)
			signature = WishList(name=walmartInfo["name"], price=walmartInfo["price"], url=walmartInfo["url"])
		except Exception:
			walmartInfo = stringToDict(walButton)
			signature = WishList(name=walmartInfo["name"], price=walmartInfo["price"], url=walmartInfo["url"])
		db.session.add(signature)
		db.session.commit()
	if (targButton is not None and targButton != "{'name': '', 'price': '', 'image': '../static/sorry.jpg', 'url': ''}"):
		try:
			targetInfo = json.loads(targButton.replace("'", "\""))
			signature = WishList(name=targetInfo["name"], price=targetInfo["price"], url=targetInfo["url"])
		except Exception:
			targetInfo = stringToDict(targButton)
			signature = WishList(name=targetInfo["name"], price=targetInfo["price"], url=targetInfo["url"])
		db.session.add(signature)
		db.session.commit()
	elif (amButton is not None and amButton != "{'name': '', 'price': '', 'image': '../static/sorry.jpg', 'url': ''}"):
		try:
			targetInfo = json.loads(targButton.replace("'", "\""))
			signature = WishList(name=targetInfo["name"], price=targetInfo["price"], url=targetInfo["url"])
		except Exception:
			amazonInfo = stringToDict(amButton)
			signature = WishList(name=amazonInfo["name"], price=amazonInfo["price"], url=amazonInfo["url"])
		db.session.add(signature)
		db.session.commit()
	return redirect(url_for('home'))

#Go to page that displays wishlist
@app.route('/wishlist')
def wishlist():
	result = WishList.query.all()
	return render_template('wishlist.html', result=result)

#Delete from Wish List
@app.route('/delete/<id>', methods=['GET', 'DELETE'])
def delete(id):
	WishList.query.filter_by(id=id).delete()
	db.session.commit()
	return redirect(url_for('wishlist'))

#Error Handling
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')

@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html')


if __name__ == "__main__":
	app.run (debug=True)


"""
#Using the walmart api to get product info	
url =  'http://api.walmartlabs.com/v1/search?format=json&apiKey=924vvubuzj4xhmvef6spxmfb&query={}'
item = '2016 macbook pro'
r = requests.get(url.format(item)).json()
print(r)
itemInfo = {
	"item" : r["items"][0]["name"],
	#"msrp" : r["items"][0]["msrp"],
	"salePrice" : r["items"][0]["salePrice"],
	"mediumImage": r["items"][0]["mediumImage"]
}
print(itemInfo)
"""

##Connect to database locally
# sshtunnel.SSH_TIMEOUT = 5.0
# sshtunnel.TUNNEL_TIMEOUT = 5.0

# with sshtunnel.SSHTunnelForwarder(
#     ('ssh.pythonanywhere.com'),
#     ssh_username='tg1632', ssh_password='Hello1234World!',
#     remote_bind_address=('tg1632.mysql.pythonanywhere-services.com', 3306)
# ) as tunnel:
#     connection = mysql.connector.connect(
#         user='tg1632', password='fopark123',
#         host='127.0.0.1', port=tunnel.local_bind_port,
#         database='tg1632$db',
#     )
# connection.close()

##Configure the Database
# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="tg1632",
#     password="fopark123",
#     hostname="tg1632.mysql.pythonanywhere-services.com",
#     databasename="tg1632$db",
# )
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False