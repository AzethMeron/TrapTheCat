
import pickle
import zlib

def save(obj, filename):
    dump = pickle.dumps(obj)
    dump = zlib.compress(dump)
    with open(filename, "wb") as f:
        f.write(dump)

def load(filename):
    with open(filename, "rb") as f:
        dump = f.read()
        dump = zlib.decompress(dump)
        return pickle.loads(dump)