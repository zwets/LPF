import os

def findTemplateNumber(name, database):
    if os.path.exists(database + ".name"):
        with open(database + ".name") as f:
            t = 1
            for line in f:
                if line.rstrip() == name:
                    return t
                else:
                    t += 1