from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
	return "FLAG{PLACEHOLDER_FLAG}"

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=__port__)
