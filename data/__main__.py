from . import init_db, load_data, verify
if __name__ == "__main__":
    init_db()
    load_data()
    verify()
