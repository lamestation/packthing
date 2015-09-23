class Builder(object):
    def __init__(self, path, version):
        self.path = path 
        self.VERSION = version

        self.files = {}
        self.files['bin'] = []
        self.files['lib'] = []
        self.files['share'] = []
