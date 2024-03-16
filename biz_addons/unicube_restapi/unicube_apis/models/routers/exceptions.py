from .handlerespon import make_response

class RequestException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.response = {}

    pass

class RequiredAuth(RequestException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.response = make_response(
            error_code='E_USER_AUTH',
            status=0,
            msg='Auth is required'
        )

    pass