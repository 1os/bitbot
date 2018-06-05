#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import urlparse, cgi

PORT_NUMBER = 8080

# This class will handles any incoming request from
# the browser

snap_dir = os.environ.get("SNAP")
snap_alt_dir = os.path.abspath(snap_dir + "/../current/")
snap_common_dir = os.environ.get("SNAP_COMMON")
snap_user_common_dir = os.environ.get("SNAP_USER_COMMON")


class myHandler(BaseHTTPRequestHandler):

    def do_POST(self):
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				postvars = urlparse.parse_multipart(self.rfile, pdict)
			elif ctype == 'application/x-www-form-urlencoded':
				length = int(self.headers.getheader('content-length'))
				postvars = urlparse.parse_qs(self.rfile.read(length),
					keep_blank_values=1)
			else:
				postvars = {}

		except Exception:
			postvars = {}

		if self.path == "/save":
			f = open(snap_common_dir + os.sep + "sphinx.cfg", "w")
			config = postvars.get("config")[0].replace("$SNAP_USER_COMMON",
				snap_user_common_dir).replace("$SNAP_COMMON",
				snap_common_dir).replace("$SNAP",
				snap_dir)
			f.write(config)
			f.close()
			self.send_response(200)
		elif self.path == "/load":
			f = open(snap_common_dir + os.sep + "sphinx.cfg")
			self.send_response(200)
			self.send_header('Content-type', "plain/text")
			self.end_headers()
			self.wfile.write(f.read().replace(snap_user_common_dir, 
				"$SNAP_USER_COMMON").replace(snap_common_dir, 
				"$SNAP_COMMON").replace(snap_dir, 
				"$SNAP").replace(snap_alt_dir, 
				"$SNAP"))
			f.close()
		elif self.path == "/setAuth":
			f = open(snap_common_dir + os.sep + "token.cfg", "w")
			f.write(postvars.get("token")[0] + "\n" + postvars[0].get("name")[0])
			f.close()
			self.send_response(200)
		elif self.path == "/auth":
			f = open(snap_common_dir + os.sep + "token.cfg")
			self.send_response(200)
			self.send_header('Content-type', "plain/text")
			self.end_headers()
			self.wfile.write(f.read().split("\n")[1])
			f.close()
		elif self.path == "/dict":
			f = open(snap_common_dir + os.sep + "dict.dic", "w")
			f.write(postvars.get("dict")[0])
			f.close()
			self.send_response(200)
		else:
			self.send_response(400)

    def do_GET(self):
		if self.path == "/":
			self.path = "/index.html"

		try:
			# Check the file extension required and
			# set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype = 'text/html'
				sendReply = True
			elif self.path.endswith(".jpg"):
				mimetype = 'image/jpg'
				sendReply = True
			elif self.path.endswith(".gif"):
				mimetype = 'image/gif'
				sendReply = True
			elif self.path.endswith(".js"):
				mimetype = 'application/javascript'
				sendReply = True
			elif self.path.endswith(".css"):
				mimetype = 'text/css'
				sendReply = True				
			else:
				self.send_response(400)

			if sendReply == True:
				# Open the static file requested and send it
				f = open(snap_dir + os.sep + "www" + os.sep + self.path)
				self.send_response(200)
				self.send_header('Content-type', mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ', PORT_NUMBER

    # Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
