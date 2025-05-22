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


class NotValidUserLimit(UserRequestExceptions):
    pass
