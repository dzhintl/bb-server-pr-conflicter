from helpers.bb_api_caller import BBAPICaller
from server.api_server import APIServer, Credential
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from end_points.check_by_pr import DependencyByPR
from end_points.check_by_commit import DependencyByCommit

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-conf", "--config_file", help="Location of the application config file")
parser.add_argument("-p", "--port", default=8080, type=int, help="Port")
args = vars(parser.parse_args())

PORT      = args["port"]
CONF_FILE = args["config_file"]

if __name__ == '__main__':    
    #HMAC Authentication
    hmac_credential = Credential(CONF_FILE, 'HMAC')

    #API Caller
    api_caller = BBAPICaller(CONF_FILE, 'BB-API')
    
    #API Resources
    dependency_by_pr = DependencyByPR(hmac_credential, api_caller)
    dependency_by_commit = DependencyByCommit(hmac_credential, api_caller)
    
    #Setup API Server and end-points
    server = APIServer("BB Branch Checker")
    server.add_hmac_resource(dependency_by_pr, '/check_dependency/by_pr')
    server.add_hmac_resource(dependency_by_commit, '/check_dependency/by_commit')
    server.start('0.0.0.0', PORT)
