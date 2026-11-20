from todolist.config import DB_PATH
from todolist.database import TaskDatabase
from todolist.ui.app import TodoApp


def main() -> None:
    database = TaskDatabase(DB_PATH)
    app = TodoApp(database)
    app.mainloop()


if __name__ == "__main__":
    main()
