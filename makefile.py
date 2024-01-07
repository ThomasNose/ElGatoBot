import os

def makedirectory(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path, exist_ok=True)
