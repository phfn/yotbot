import re
import string
import random


def get_valid_filename(s):
    """
    stolen at django utils text, but spaces allowed
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("EINKAUFEN! - Minecraft [Deutsch/HD]")
    'EINKAUFEN - Minecraft DeutschHD'
    """
    return re.sub(r'(?u)[^-\w\s.]', '', s)

def get_random_string(length=5):
    ret = ""
    for i in range(length):
        ret = ret + random.choice(string.ascii_letters)
    return ret