class LoginError(Exception):
    pass


class APIException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass

class GameNotFoundException(Exception):
    pass


class PlayerNotFoundException(Exception):
    pass


class PaymentRequiredException(Exception):
    pass
