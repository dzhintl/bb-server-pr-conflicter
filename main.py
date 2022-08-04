import logging
from helpers.bb_api_caller import BBAPICaller
from server.api_server import APIServer, Credential
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from end_points.check_by_pr import DependencyByPR
from end_points.check_by_commit import DependencyByCommit

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-conf", "--config_file", default="./config.properties", help="Location of the application config file")
parser.add_argument("-p", "--port", default=8080, type=int, help="Port")
parser.add_argument("-log", "--log_file", default=None, type=str, help="Location of the log file. Default is system log")
parser.add_argument("-d", "--debug_level", default="WARNING", type=str, help="Debug Level CRITICAL/ERROR/WARNING/INFO/DEBUG. Default is WARNING")
args = vars(parser.parse_args())

PORT      = args["port"]
CONF_FILE = args["config_file"]
LOG_FILE  = args["log_file"]
LOG_LEVEL = args["debug_level"]

if __name__ == '__main__':
    logging.basicConfig(filename=LOG_FILE, format='%(asctime)s %(levelname)s [%(name)s] %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level = LOG_LEVEL.upper())
    #HMAC Authentication
    hmac_credential = Credential(CONF_FILE, 'HMAC')

    #API Caller
    api_caller = BBAPICaller(CONF_FILE, 'BB-API')
    
    #API Resources
    dependency_by_pr = DependencyByPR(hmac_credential, api_caller)
    dependency_by_commit = DependencyByCommit(hmac_credential, api_caller)
    
    #Setup API Server and end-points
    server = APIServer("BB Branch Checker")
    server.add_hmac_resource(dependency_by_pr, '/check_dependency/by_pr/comment')
    server.add_hmac_resource(dependency_by_commit, '/check_dependency/by_commit/comment')
    server.start('0.0.0.0', PORT, debug=LOG_LEVEL.upper()==logging.getLevelName(logging.DEBUG))
