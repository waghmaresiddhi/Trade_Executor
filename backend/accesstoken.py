import json
from fyers_apiv3 import fyersModel
import webbrowser

"""
In order to get started with Fyers API we would like you to do the following things first.
1. Checkout our API docs :   https://myapi.fyers.in/docsv3
2. Create an APP using our API dashboard :   https://myapi.fyers.in/dashboard/

Once you have created an APP you can start using the below SDK 
"""

#### Generate an authcode and then make a request to generate an accessToken (Login Flow)

"""
1. Input parameters
"""
redirect_uri = "https://siddhi-waghmare.web.app/"  # Replace with your registered Redirect URI
client_id = "EATQHRLAFP-100"                   # Replace with your FYERS Client ID (App ID)
secret_key = "FQ8KDG9VGH"           # Always "authorization_code"
grant_type = "authorization_code"                  ## The grant_type always has to be "authorization_code"
response_type = "code"                             ## The response_type always has to be "code"
state = "sample"                                    ##  The state field here acts as a session manager. you will be sent with the state field after successfull generation of auth_code 


### Connect to the sessionModel object here with the required input parameters
appSession = fyersModel.SessionModel(client_id = client_id, redirect_uri = redirect_uri,response_type=response_type,state=state,secret_key=secret_key,grant_type=grant_type)

# ## Make  a request to generate_authcode object this will return a login url which you need to open in your browser from where you can get the generated auth_code 
generateTokenUrl = appSession.generate_authcode()

"""There are two method to get the Login url if  you are not automating the login flow
1. Just by printing the variable name 
2. There is a library named as webbrowser which will then open the url for you without the hasel of copy pasting
both the methods are mentioned below"""
print((generateTokenUrl))  
webbrowser.open(generateTokenUrl,new=1)

"""
run the code firstly upto this after you generate the auth_code comment the above code and start executing the below code """
##########################################################################################################################

### After succesfull login the user can copy the generated auth_code over here and make the request to generate the accessToken 
auth_code = input("Paste the auth_code generated from the first request")
appSession.set_token(auth_code)
response = appSession.generate_token()

## There can be two cases over here you can successfully get the acccessToken over the request or you might get some error over here. so to avoid that have this in try except block
try:
    access_token = response["access_token"]
    print("Response JSON:")
    print(json.dumps(response, indent=4))  # Pretty-print the JSON response
    print("\nAccess Token:")
    print(access_token)
except Exception as e:
    print(e,response)  ## This will help you in debugging then and there itself like what was the error and also you would be able to see the value you got in response variable. instead of getting key_error for unsuccessfull response.

