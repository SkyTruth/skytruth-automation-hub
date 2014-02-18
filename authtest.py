# smoketest

import apiclient.discovery
import optparse
import sys, os
import httplib2

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials


USAGE = """%prog SERVER_URL PEM_FILE
Run a simple authentication on a production server.

SERVER_URL    Url of the server to test against  
                e.g. https://automation-hub.appspot.com
PEM_FILE      file name of the PEM file containing the private key (see HowTo-Authenticate.txt)
                e.g. privatekey.pem
AUTH_EMAIL    email address of the service account that matches the PEM key file   
                e.g. 314157906781-5k944tnd2e4hvcf0nrc4dl93kgdaqnam@developer.gserviceaccount.com             
"""


def main(server_url, pem_file, auth_email):
    # Load the key in PEM format that you downloaded from the Google API
    # Console when you created your Service account.
    f = file(pem_file, 'rb')
    key = f.read()
    f.close()
    
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with the Credentials. Note that the first parameter, service_account_name,
    # is the Email address created for the Service account. It must be the email
    # address associated with the key that was created.

    credentials = SignedJwtAssertionCredentials(
        auth_email,
        key,
        scope='https://www.googleapis.com/auth/userinfo.email')
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct a service object via the discovery service.
    service = apiclient.discovery.build("test", "v1.0", http=http,
            discoveryServiceUrl=(server_url + 
                "/_ah/api/discovery/v1/apis/{api}/{apiVersion}/rest"))
                                 
    print "Testing %s .." % server_url
    response = service.test(body=dict(message='This is a test')).execute()
    print response
#    print "Test %s" % response['status']
    print "Done"


if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) != 3:
        print 'Error: Exactly 3 arguments required.'
        parser.print_help()
        sys.exit(1)
    SERVER_URL = args[0]
    PEM_FILE = args[1]
    AUTH_EMAIL = args[2]
    main(SERVER_URL, PEM_FILE, AUTH_EMAIL)
