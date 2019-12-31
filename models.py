from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()

class Submission(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    problem_id = Column(Integer, ForeignKey("problem.id"))

    timestamp = Column(DateTime, default=datetime.utcnow)
    code = Column(String(5000))
    language = Column(String(16))

    status = Column(Integer, default= -2)
    testcases = Column(Text)

    task = relationship("Task", backref=backref("submission", uselist=False), lazy="dynamic")
    progress = Column(String(32), default="0/0")