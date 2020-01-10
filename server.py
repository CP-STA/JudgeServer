import os
import json
import shutil

from sqlalchemy import create_engine
from sqlalchemy.sql import text

from grader.grader import Grader
from grader.config import Configurations, OUTPUT_PATH, DATABASE_URI
from rq import get_current_job

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(DATABASE_URI, echo=True)

"""
    RESULT_SUCCESS = 0
    RESULT_COMPILATION_ERROR = -3
    RESULT_PENDING = -2
    RESULT_WRONG_ANSWER = -1
    RESULT_CPU_TIME_LIMIT_EXCEEDED = 1
    RESULT_REAL_TIME_LIMIT_EXCEEDED = 2
    RESULT_MEMORY_LIMIT_EXCEEDED = 3
    RESULT_RUNTIME_ERROR = 4
    RESULT_SYSTEM_ERROR = 5
"""

""" Creates all the necessary directories to compile and execute the submitted code """
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
        config = Configurations.get_config(language)
        src = os.path.join(path, config["compile"]["src_name"])

        # Saves submitted code to file
        with open(src, "w+") as f:
            f.write(code)

        grader = Grader(src, config, memory_limit, time_limit, problem_id, path, job)
        result = grader.grade_all()

        data = {
            "submission_id": submission_id,
            "progress": f"{grader.max_count}/{grader.max_count}",
            "testcases": json.dumps({"data": result})
        }
            
        if not any([i["result"] for i in result]):
            data["status"] = 0
        else:
            data["status"] = max([i["result"] for i in result if i["result"] != 0])

        with engine.connect() as con:
            query = text("""UPDATE submission SET 
                            testcases = :testcases, status = :status, progress = :progress 
                            WHERE submission.id = :submission_id""")

            # Update the submission with the final result
            con.execute(query, **data)

            # Update contest scores if there exists a registration
            if data["status"] == 0 and registration_id is not None:
                query = text("""UPDATE registration SET 
                                score = score + :points 
                                WHERE registration.id = :registration_id""")

                con.execute(query, **{"points": points, "registration_id": registration_id})


                # Updating the last submission timestamp
                query = text("""UPDATE registration SET 
                                last_submission = (SELECT timestamp FROM submission WHERE submission.id = :submission_id)
                                WHERE registration.id = :registration_id""")
                
                con.execute(query, **{"submission_id": submission_id, "registration_id": registration_id})
