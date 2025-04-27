class NotAFileException (Exception):
    def __str__(self):
        return "Not a file path"