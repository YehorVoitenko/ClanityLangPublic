class FileExceptions(Exception):
    pass


class UserRequestExceptions(Exception):
    pass


class PurchaseRequestExceptions(Exception):
    pass


class NotValidFileContentType(FileExceptions):
    pass


class NotValidColumnSet(FileExceptions):
    pass


class UserNotExists(Exception):
    pass


class NotValidPromocodeRequest(Exception):
    pass
