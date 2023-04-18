from configparser import ConfigParser
import hashlib
import logging
from flask import Flask, request
from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser
import hmac
from helpers.api_caller_bb import APICallerBB
import helpers.utils as utils


class HMACResource(Resource):
    ''' Resource class with HMAC Authentication supported
    '''
    
    __name__ = 'HMACResource'
    request_parser = RequestParser()
    _logger = logging.getLogger(__name__)

    SECTION="HMAC"
    CONFIG_KEY="CONFIG"

    _config: None
    config_file: None

    def __init__(self, config_file, *args) -> None:
        super().__init__()
        self.config_file = config_file
        config_parser = ConfigParser()
        config_parser.read(config_file)

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
        
        hash_mode  = self._config.type.lower()

        #Need to check if HMAC is needed
        client_signature = None
        if 'X-Hub-Signature' in request.headers:
            client_signature = request.headers['X-Hub-Signature']

        if secret_key is not None and client_signature is not None:
            allowed = hashlib.algorithms_available
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


class APIServer:
    ''' Main class to setup API Server. For each API end-point, call add_resource function.
        Use AuthResource if the end-point supports Basic HTTP Authentication
        Use HMACResource if the end-point supports HMAC secret key authentication
    '''
    app: Flask
    api: Api

    def __init__(self, app_name) -> None:
        self.app = Flask(app_name)
        self.api = Api(self.app)

    def add_hmac_resource(self,resource: HMACResource, route: str, *args):
        self.api.add_resource(resource.__class__, route, resource_class_args=[resource.config_file, *args])

    def start(self, host: str, port: int, **kwargs):
        self.app.run(debug = kwargs.get('debug', False), host = host, port = port)