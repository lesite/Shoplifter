class LuhnCheckFail(Exception):
    pass


class GatewayTimeOut(Exception):
    pass


class EarlyAuthFail(Exception):
    pass


class AuthorizationAmountTooHigh(Exception):
    """
    TODO:
    Try to automatically deal with?.. 
    """
    pass


class RequestError(Exception):
    pass


class GatewayError(Exception):
    pass


class TransactionDeclined(Exception):
    pass


class CSCFail(Exception):
    pass
