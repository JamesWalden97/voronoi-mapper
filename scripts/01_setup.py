import os


def main():
    req_dirs = "./_data/_plots"

    os.makedirs(req_dirs, exist_ok=True)


if __name__ == "__main__":
    main()
