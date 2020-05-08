class LoginError(Exception):
    pass


class APIException(Exception):
    pass


class ClientException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass


class GameNotFoundException(Exception):
    pass


class ParkNotFoundException(Exception):
    pass


class TeamNotFoundException(Exception):
    pass


class PlayerNotFoundException(Exception):
    pass


class PaymentRequiredException(Exception):
    pass
