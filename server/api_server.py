import hashlib
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser
import hmac
from helpers.bb_api_caller import BBAPICaller
import helpers.utils as utils
from models.credential import Credential


class AuthResource(Resource):
    ''' Resource class with HTTP Basic Authentication supported
    '''

    auth = HTTPBasicAuth()
    credential: Credential

    def __init__(self, credential: Credential) -> None:
        super().__init__()
        self.credential = credential

    @auth.login_required
    def get(self):
        pass
    
    @auth.login_required
    def post(self):
        pass

    @auth.verify_password
    def verify_password(self, username, password):
        if username == self.credential.get_username() and password == self.credential.get_password():
            return True
        return False


class HMACResource(Resource):
    ''' Resource class with HMAC Authentication supported
    '''
    
    __name__ = 'HMACResource'
    request_parser = RequestParser()
    credential: Credential
    api_caller: BBAPICaller

    def __init__(self, cred: Credential, api_caller: BBAPICaller) -> None:
        super().__init__()
        self.credential = cred
        self.api_caller = api_caller

    def get(self):
        return self.process_get()
    
    def post(self):
        request_data  = request.get_data()
        response_code = 401

        hash_mode  = self.credential.get_hmac_sha().lower()
        secret_key = self.credential.get_hmac_key()

        allowed = hashlib.algorithms_available
        if hash_mode in allowed:
            digest = hmac.new(secret_key, msg=request_data, digestmod=getattr(hashlib, hash_mode)).hexdigest()
            signature = f'{hash_mode}={digest}'

            if 'X-Hub-Signature' in request.headers:
                client_signature = request.headers['X-Hub-Signature']

                if signature == client_signature:
                    return self.process_post()
        else:
            #TODO: print error
            pass
        
        return {'status': response_code, 'message': 'Authorization failed'}, response_code

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

    def add_hmac_resource(self,resource: HMACResource, route: str):
        self.api.add_resource(resource.__class__, route, resource_class_args=[resource.credential, resource.api_caller])

    def start(self, host: str, port: int):
        self.app.run(debug = True, host = host, port = port)