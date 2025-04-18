"""
SQLAlchemy's Session object is not thread-safe.

Here is example of what would happend in case you decide to use Session in
several threads at the same time.
"""

from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import Session, DeclarativeBase
import threading
import time
from pathlib import Path


# Schema
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)


# Setup database
engine = create_engine("sqlite:///test.db")
Base.metadata.create_all(engine)

# Create a single session to be shared across threads
shared_session = Session(engine)


def add_user(user_id):
    try:
        # All threads will use the same session
        user = User(id=user_id, name=f"User_{user_id}")
        shared_session.add(user)

        # Simulate some processing time to increase chance of race condition
        time.sleep(0.1)

        shared_session.commit()
        print(f"Thread {user_id} committed successfully")
    except Exception as e:
        print(f"Thread {user_id} failed: {str(e)}")


# Create and start multiple threads
threads = []
for i in range(5):
    t = threading.Thread(target=add_user, args=(i,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

# Verify results - this should be in a new session
with Session(engine) as session:
    users = session.execute(select(User)).all()
    print(f"Total users in database: {len(users)}")
    # You'll likely see fewer users than threads due to conflicts

# Remove created database
engine.dispose()
Path("test.db").unlink()
