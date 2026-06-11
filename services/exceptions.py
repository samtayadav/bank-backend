class AccountNotFoundError(Exception):
    pass


class TransferNotFoundError(Exception):
    pass


class InvalidTransferError(Exception):
    pass


class InsufficientBalanceError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass
