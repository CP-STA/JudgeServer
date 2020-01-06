import os
import json
import shutil

from sqlalchemy import create_engine
from sqlalchemy.sql import text
# from sqlalchemy.orm import sessionmaker

from grader.grader import Grader
from grader.configurations import Configurations
from rq import get_current_job

OUTPUT_PATH = "/home/moxis/Documents/Github/OJ/STAOJ/JudgeServer/tmp"

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:////home/moxis/Documents/Github/OJ/STAOJ/MainServer/app.db', echo=True)

class CreateEnvironment(object):
    def __init__(self, submission_id):
        self.work_dir = os.path.join(OUTPUT_PATH, str(submission_id))
    
    def __enter__(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)

        os.mkdir(self.work_dir)
        return self.work_dir
    
    def __exit__(self, a, b, c):
        shutil.rmtree(self.work_dir)

def evaluate_submission(submission_id, language, code, memory_limit, time_limit, problem_id, registration_id, points):
    job = get_current_job()

    with CreateEnvironment(str(submission_id)) as path:
        # NOTE: Need to handle cases if config is null <rare but can happen>

        config = Configurations.get_config(language)
        src = os.path.join(path, config["compile"]["src_name"])

        with open(src, "w+") as f:
            f.write(code)

        try:
            g = Grader(src, config, memory_limit, time_limit, problem_id, path, job)
        except Exception:
            result = [{"result": 6}]

            data = {
                "submission_id": submission_id,
                "progress": "0/0",
                "testcases": ""
            }
        else:
            result = g.grade_all()

            data = {
                "submission_id": submission_id,
                "progress": f"{g.max_count}/{g.max_count}",
                "testcases": json.dumps({"data": result})
            }

        if not(any([i["result"] for i in result])):
            data["status"] = 0
        else:
            data["status"] = max([i["result"] for i in result if i["result"] != 0])

        query = text("UPDATE submission SET testcases = :testcases, status = :status, progress = :progress WHERE submission.id = :submission_id")

        with engine.connect() as con:
            con.execute(query, **data)

            if data["status"] == 0 and registration_id is not None:
                query = text("UPDATE submission SET score = score + :points WHERE registration.id = :registration_id")
                con.execute(query, **{"points": points, "registration_id": registration_id})
