ERROR = "error"
ERROR_DESC = "error_description"

INVALID_REQUEST = "invalid_request"
INVALID_REQUEST_DESC = "Invalid request"
# The request is missing a required parameter, includes an
# invalid parameter value, includes a parameter more than
# once, or is otherwise malformed.
UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"
UNSUPPORTED_GRANT_TYPE_DESC = "Unsupported grant type."


UNAUTHORIZED_CLIENT = "unauthorized_client"
UNAUTHORIZED_CLIENT_DESC = "Unauthorized client"
# The client is not authorized to request an authorization
#                code using this method.

ACCESS_DENIED = "access_denied"
ACCESS_DENIED_DESC = "Access denied"
# The resource owner or authorization server denied the
# request.

UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
UNSUPPORTED_RESPONSE_TYPE_DESC = "Unsupported response type"
# The authorization server does not support obtaining an
# authorization code using this method.

INVALID_SCOPE = "invalid_scope"
INVALID_SCOPE_DESC = "Invalid scope"

# The requested scope is invalid, unknown, or malformed.

SERVER_ERROR = "server_error"
SERVER_ERROR_DESC = "Server error"
# The authorization server encountered an unexpected
# condition that prevented it from fulfilling the request.
# (This error code is needed because a 500 Internal Server
# Error HTTP status code cannot be returned to the client
# via an HTTP redirect.)

TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
TEMPORARILY_UNAVAILABLE_DESC = "Temporarily unavailable"
# The authorization server is currently unable to handle
# the request due to a temporary overloading or maintenance
# of the server.  (This error code is needed because a 503
# Service Unavailable HTTP status code cannot be returned
# to the client via an HTTP redirect.)
INVALID_TOKEN = 'invalid_token_error'
INVALID_TOKEN_DESC = 'Invalid token error'

# When access token expire
INVALID_RESPONSE_TYPE_DESC = 'Invalid response_type'
INVALID_USER_DESC = 'Invalid user'

AUTHORIZATION_REQUIRED = 'Authorization required'

#when response is successful
VALID_CLIENT = 'valid_client'
SUCCESS = 'successful'