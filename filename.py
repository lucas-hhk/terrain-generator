import os
import re
import numpy as np

#https://www.w3schools.com/python/python_regex.asp
#https://docs.python.org/3/library/re.html#search-vs-match


def next_filename(base_name, extension):

    files = os.listdir("Saved")

    pattern = re.compile(rf"{base_name}(\d+){extension}")

    numbers = [int(pattern.match(f).group(1)) for f in files if pattern.match(f)]
    #uses list comprehension, [(addthis to list) loop through directory, if pattern.match(f) == true]
    # (base_name)1.gif fits the regex in pattern, such as map1.gif or island5.png

    if numbers:
        next = np.max(numbers) + 1  #find the highest numbered file currently in Saved, add 1 for next
    else:
        next = 1    #if none exist yet

    filename = f"{base_name}{next}{extension}"
    return filename



