from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///data.db")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)

Base.metadata.create_all(engine)