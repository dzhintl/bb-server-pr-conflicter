import logging
from server.api_server import APIServer
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from server.end_points.check_affected_changes import AffectedChangesAPI
from server.end_points.check_by_pr_comment import DependencyByPR_Comment
from server.end_points.check_by_commit_comment import DependencyByCommit_Comment
from server.end_points.check_by_request_comment import DependencyByRequest_Comment
from server.end_points.check_by_request import DependencyByRequest

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

    
    #API Resources
    dependency_by_pr_comment        = DependencyByPR_Comment([CONF_FILE])
    dependency_by_commit_comment    = DependencyByCommit_Comment([CONF_FILE])
    dependency_by_request_comment   = DependencyByRequest_Comment([CONF_FILE])
    dependency_by_request           = DependencyByRequest([CONF_FILE])
    affected_changes                = AffectedChangesAPI([CONF_FILE])
    
    #Setup API Server and end-points
    server = APIServer("BB Branch Checker")
    server.add_resource(dependency_by_pr_comment, '/check_dependency/by_pr/comment', [CONF_FILE])
    server.add_resource(dependency_by_commit_comment, '/check_dependency/by_commit/comment', [CONF_FILE])
    server.add_resource(dependency_by_request_comment, '/check_dependency/by_file/comment', [CONF_FILE])
    server.add_resource(dependency_by_request, '/check_dependency/by_file', [CONF_FILE])
    server.add_resource(affected_changes, '/check_affected_changes', [CONF_FILE])
    server.start('0.0.0.0', PORT, debug=LOG_LEVEL.upper()==logging.getLevelName(logging.DEBUG))
