import os
import re


def shorten_path(path, maxLength):
    pathLength = 0
    pathLengthMax = maxLength
    shortenedPathList = []

    # split path into list
    splitPathList = path.split(os.path.sep)

    # start from end and iterate through each path element,
    for pathItem in reversed(splitPathList):
        # sum the length of the path so far
        pathLength += len(pathItem)
        # if less than max
        if pathLength <= pathLengthMax:
            # create shorted path
            shortenedPathList.append(pathItem)
        else:
            # no need to go through the loop
            break

    # reverse the shortened path, convert to a string
    shortenedPathList.reverse()
    shortenedPath = os.path.sep.join(shortenedPathList)
    # for shorter path, add ...
    if shortenedPath.startswith(os.path.sep) or re.match('[A-Z]:', shortenedPath):
        return shortenedPath
    else:
        return '..' + os.path.sep + shortenedPath
