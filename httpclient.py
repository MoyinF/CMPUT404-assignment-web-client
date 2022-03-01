#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self,url):
        return (urllib.parse.urlparse(url).hostname, urllib.parse.urlparse(url).port)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        response = data.split("\r\n\r\n")
        response = response.split("\r\n")
        headers = ""
        if len(response) > 1:
            headers = response[1:]
        return headers

    def get_body(self, data):
        body = ""
        splits = data.split("\r\n\r\n")
        if len(splits) > 1:
            body = splits[1]
        return body

    def sendall(self, data, socket):
        socket.sendall(data.encode('utf-8'))

    def close(self, socket):
        socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url_host = urllib.parse.urlparse(url).netloc
        url_path = urllib.parse.urlparse(url).path
        if len(url_path)>1 and url_path[0] == "/":
            url_path = url_path[1:]
        get_request = "GET /" + url_path + " HTTP/1.0\r\n"
        get_request += "Host: " + url_host + "\r\n"
        get_request += "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0\r\n"
        get_request += "Accept: */*\r\n"
        get_request += "Connection: close\r\n"
        get_request += "\r\n"

        (host, port) = self.get_host_port(url)
        if port is None:
            port = 80
        self.socket = self.connect(host, port)

        self.sendall(get_request, self.socket)
        print("get request is: \n", get_request)
        response = self.recvall(self.socket)
        self.close(self.socket)
        print("response is: \n", response)
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url_host = urllib.parse.urlparse(url).netloc
        url_path = urllib.parse.urlparse(url).path
        arg_line = ""
        if args:
            for key in args.keys():
                arg_line += key+"="+args[key]+"&"
            arg_line = arg_line[:-1]
        if url_path[0] == "/" and len(url_path)>1:
            url_path = url_path[1:]
        post_request = "POST /" + url_path + " HTTP/1.0\r\n"
        post_request += "Host: " + url_host + "\r\n"
        post_request += "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0\r\n"
        post_request += "Accept: */*\r\n"
        post_request += "Content-Type: application/x-www-form-urlencoded\r\n"
        if args:
            post_request += "Content-Length: " + str(len(arg_line)) + "\r\n"
        else:
            post_request += "Content-Length: 0\r\n"
        post_request += "Connection: close\r\n"
        post_request += "\r\n"
        if args:
            post_request += arg_line + "\r\n"

        (host, port) = self.get_host_port(url)
        if port is None:
            port = 80
        self.socket = self.connect(host, port)

        self.sendall(post_request, self.socket)
        print("post request is: \n", post_request)
        response = self.recvall(self.socket)
        self.close(self.socket)
        print("response is: \n", response)
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
