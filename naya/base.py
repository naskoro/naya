from werkzeug import Response as BaseResponse, Request as BaseRequest


class Response(BaseResponse):
    default_mimetype = 'text/html'


class Request(BaseRequest):
    pass
