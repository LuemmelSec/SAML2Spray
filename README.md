# SAML2Spray
Python Script for SAML2 Authentication Passwordspraying

In a recent pentest I came accross the need to passwordspray a SAML2 authentication.
As I couldn't find a ready to go solution, nor was able to do it with burp, I created my own little script to do the job for me.

Following you'll find a short explaination of the workflow, which in short is:
- User want's to access a service on site A
- site A redirects to the identity provider on site B
- User authenticates to site B which gives a SAML-Response with which the user can now access site A

In order for the script to run, we need to fetch some things beforehand. Burp or something alike can come in handy here.

Initial request to the Service Provider:

>GET / HTTP/1.1  
>Host: mysite.service  
>User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0  
>...
