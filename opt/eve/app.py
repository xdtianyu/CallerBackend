from eve import Eve
from eve.auth import HMACAuth
from flask import current_app as app
from hashlib import sha1
import hmac

from config import config


class HMACAuth(HMACAuth):
    def check_auth(self, userid, hmac_hash, headers, data, allowed_roles,
                   resource, method):
        # use Eve's own db driver; no additional connections/resources are
        # used
        accounts = app.data.driver.db['accounts']
        user = accounts.find_one({'userid': userid})
        if user:
            secret_key = user['secret_key']
        # in this implementation we only hash request data, ignoring the
        # headers.
        return user and \
            hmac.new(str(secret_key).encode(), data, sha1).hexdigest() == \
                hmac_hash


app = Eve(settings=config, auth=HMACAuth)
#app = Eve(settings=config)
app.run()