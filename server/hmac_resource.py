from configparser import ConfigParser
import hashlib
import logging
from flask_restful.reqparse import RequestParser
import hmac
import helpers.utils as utils
from flask import request
from flask_restful import Resource


class HMACResource(Resource):
    ''' Resource class with HMAC Authentication supported
    '''
    
    __name__ = 'HMACResource'
    request_parser = RequestParser()
    _logger = logging.getLogger(__name__)

    SECTION=""
    CONFIG_KEY="CONFIG"

    _config: None

    def __init__(self, *args) -> None:
        super().__init__()
        config_parser = ConfigParser()
        config_parser.read(args[0][0])

        try:
            if config_parser.has_option(self.SECTION, self.CONFIG_KEY):
                self._config = utils.json_to_object(config_parser.get(self.SECTION, self.CONFIG_KEY))
            else:
                self._logger.fatal(f"CONFIG is NOT found under {self.SECTION} section")
        except:
            self._logger.fatal("Configuration setup failed!")


    def get(self):
        return self.process_get()
    
    def post(self):
        request_data  = request.get_data()
        result = {'status': 401, 'message': 'Authorization failed'}, 401

        secret_key = None
        if self._config.key:
            secret_key = utils.base64_decode(self._config.key, output=None)

        #Need to check if HMAC is needed
        client_signature = None
        if 'X-Hub-Signature' in request.headers:
            client_signature = request.headers['X-Hub-Signature']

        if secret_key is not None and client_signature is not None:
            allowed = hashlib.algorithms_available
            hash_mode  = self._config.type.lower()
            if hash_mode in allowed:
                digest = hmac.new(secret_key, msg=request_data, digestmod=getattr(hashlib, hash_mode)).hexdigest()
                signature = f'{hash_mode}={digest}'

                if signature == client_signature:
                    result = self.process_post()
            else:
                self._logger.error("Invalid hash mode detected. Configured hashing mode is: {} while supported modes are: {}".format(hash_mode, hashlib.algorithms_available))
        elif secret_key is None and client_signature is None:
            result = self.process_post()

        return result

    def process_post(self):
        return {'status': 501, 'message': 'Method not supported'}, 501

    def process_get(self):
        return {'status': 501, 'message': 'Method not supported'}, 501

    def process_put(self):
        return {'status': 501, 'message': 'Method not supported'}, 501

    def process_payload(self):
        return utils.json_to_object(request.get_data(as_text=True))