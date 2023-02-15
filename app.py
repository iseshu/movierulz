from flask import *
from flask_cors import CORS
from helper import *
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/')
def home():
	try:
		data = get_mainpage()
	except:
		data = {"status":False}
	return jsonify(data)

@app.route('/search',methods=['GET'])
def search():
	query = request.args.get('query')
	try:
		data = search_movie(query)
	except:
		data = {"status":False}
	return jsonify(data)


@app.route('/get',methods=['GET'])
def get_url():
	url = request.args.get('url')
	try:
		data = get_page(url)
	except:
		data = {"status":False}
	return jsonify(data)

@app.route('/dwnlink',methods=['GET'])
def dwnurl():
	link = request.args.get('url')
	try:
		url = get_dwnlink(link)
		data = {"status":True,"source_link":link,"dwn_link":url}
	except:
		data = {"status":False}
	return jsonify(data)

if __name__ == '__main__':
	app.run()
