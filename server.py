import os
import json
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from grader.grader import Grader
from grader.configurations import Configurations
from rq import get_current_job

from models import Submission

OUTPUT_PATH = "/home/moxis/Documents/Github/OJ/STAOJ/JudgeServer/tmp"

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Every app will be ran in their own submission id folder
class CreateEnvironment(object):
    def __init__(self, submission_id):
        self.work_dir = os.path.join(OUTPUT_PATH, submission_id)
    
    def __enter__(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)

        os.mkdir(self.work_dir)
        return self.work_dir
    
    def __exit__(self, a, b, c):
        shutil.rmtree(self.work_dir)

def evaluate_submission(submission_id, language, code, memory_limit, time_limit, problem_id):
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
            # TODO: Do something for compilation error
            pass
        else:
            result = g.grade_all()

    submission = Submission.query.get(submission_id)
    submission.testcases = json.dumps({"data": result})

    if not any([i["result"] for i in result]):
        submission.result = 0
    else:
        submission.result = max([i["result"] for i in result if i["result"] != 0])
    
    # TODO: perhaps add line to delete the task from the database
    session.commit()