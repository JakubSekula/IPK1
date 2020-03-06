#!/usr/bin/python                                                                                                                                             

import socket               # Import socket module
import threading
import re
import sys

argument = sys.argv[1]

port = argument[ 0:5 ]
host = argument[ 5: ]
host = int( host )

def return_header( result, error_code ):
 if( error_code == 0 ):
  code = "HTTP/1.1 200 OK \r\n\r\n"
 elif( error_code == 1 ):
  code = "HTTP/1.1 400 Bad Request \r\n\r\n"
 elif( error_code == 2 ):
  code = "HTTP/1.1 405 Method Not Allowed \r\n\r\n"
 code = str.encode( code )
 result = code + result
 return result

def create_message( result, actionType, adress ):
 result = str.encode( result )
 adress = str.encode( adress )
 actionType = str.encode(actionType)
 result = adress + b':' + actionType + b'=' + result
 return result

def post_method( message, error_code, method ):
 if ( not( method == "/dns-query" ) ):
  error_code = 1
  return ( error_code, b'' )
 
 body = re.split("(\r\n\r\n)|(\n\n)", message, maxsplit=1)[3]
 radky = body  
 hotov = "";
 for line in radky.splitlines():
  line = re.sub( '(\s)*', '', line )
  if( re.search( '^(\s)*$', line ) ):
   error_code = 1;
   return ( error_code, b'' )
  hotov = hotov + "\n" + line
 radky = hotov
 radky = radky.split()
 result = b""
 for request in  radky:
  if ( re.search( '^(((w){3}.)|(())(\w)+(\.))+[a-zA-Z]+(\:)(A)$', request ) ):
   request = request.split(":")
   adress = request[ 0 ]
   actionType = request[ 1 ]
   try:
    ip = socket.gethostbyname( adress )
    result1 = create_message( ip, actionType, adress )
    result = result + result1 + b"\n"
   except:
    error_code = 1
  elif( re.search( '^((\d)*((\.)|(\:)))*PTR$', request ) ):
   request = request.split(":")
   adress = request[ 0 ]
   actionType = request[ 1 ]
   domain = socket.gethostbyaddr( adress )[ 0 ]
   result1 = create_message( domain, actionType, adress )
   result = result + result1 + b"\n"
  else:
   error_code = 1
 error_code = 0
 return ( error_code, result )

def get_method( message, error_code, method ):
 if( not( re.search( '/resolve', method ) ) ):
  error_code = 1
  return( error_code, b'' ) 
 result = b''
 try:
  adress = re.search( 'name=((\s)*(\S)*)[a-zA-Z]*\&', message ).group( 1 )
 except:
  error_code = 1
  return (error_code, b'')
 try:
  actionType = re.search( 'type=(\S){0,3}' ,message ).group(0)
 except:
  error_code = 1
  return( error_code, b'' )
 actionType = actionType.split("=")
 actionType = actionType[ 1 ]

 #if( actionType == "PTR" and re.search( '^((w){3}.)|()((\w)*(\.){0,1})*$', adress ) ):
 if( actionType == "PTR" and re.search( '^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', adress ) ):
  if( re.search( '^((w){3}.)|()((\w)*(\.){0,1}[a-zA-Z])+$', adress ) ):
   error_code = 1
   return ( error_code, result )
  
  #osetrit
  result = socket.gethostbyaddr( adress )[ 0 ]
  result = create_message( result, actionType, adress )
  return ( error_code, result + b"\n" )
 elif ( actionType == "A" and re.search( '^((w){3}.)|()((\w)*(\.){0,1}[a-zA-Z])+$', adress ) ):
  try:
   result = socket.gethostbyname( adress )
   result = create_message( result, actionType, adress )
   result = result + b'\n'
  except:
   error_code = 1
  return ( error_code, result )
 else:
  error_code = 1;
  return( error_code, b'' )

def parse( message, error_code ):
 message = message.decode()
 method = message.split()[1]
 first_word = message.split()[0]
 if ( first_word == "GET" ):
  error_code, result = get_method( message, error_code, method )
  return ( error_code, result )
 elif( first_word == "POST" ):
  error_code, result = post_method( message, error_code, method )
  return ( error_code, result )
 else:
  error_code = 2;
  return (  error_code, b'' )

def on_new_client(clientsocket,addr):
    error_code = 0;
    while True:
        data = clientsocket.recv(1024)
        error_code, result = parse( data, error_code )
        result = return_header( result, error_code )
        clientsocket.sendall( result )
        break
    clientsocket.close()

s = socket.socket()
HOST = '127.0.0.1'
PORT = host

s.bind((HOST, PORT))
s.listen(5)

while True:
   c, addr = s.accept()
   x = threading.Thread(target=on_new_client,args=(c,addr))
   x.start()
s.close()