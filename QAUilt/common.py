import base64
import hmac
from hashlib import sha256
import logging

logging.basicConfig(format='%(asctime)s : %(message)s',
                    filename='new.log',
                    filemode='a',
                    level=logging.INFO)

def get_sign(data, key):
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    sign = base64.b64encode(hmac.new(key, message, digestmod=sha256).digest())
    sign = str(sign, 'utf-8')
    return sign

def log_info(context):
    print(context)
    logging.info(context)

def log_debug(context):
    logging.debug(context)