import ujson

def read_config(path):
    with open(path, "r") as f:
        conf = ujson.load(f)  
    return conf

def main():
    conf = read_config("config.json")
    print(conf)

if __name__ == "__main__":
    main()