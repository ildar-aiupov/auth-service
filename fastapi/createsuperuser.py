import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models.user import User
from core.config import settings
from db.postgres import Base


def main(
    login: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
):
    dsn = f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    engine = create_engine(dsn, echo=False, future=True)

    # создаем запись суперпользователя, если указанный логин не занят
    with Session(engine) as session:
        queryset = session.execute(select(User).filter(User.login == login)).first()
        if not queryset:
            user = User(
                login=login,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_superuser = True
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Superuser with login '{login}' created succesfully.")
        else:
            print(
                f"Could not create superuser with login '{login}'. This login is already occupied."
            )


if __name__ == "__main__":
    typer.run(main)
