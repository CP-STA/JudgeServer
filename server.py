import os
import json
import shutil

from flask import Flask, request, Response
from grader.grader import Grader
import grader.configurations as configurations

app = Flask(__name__)
OUTPUT_PATH = "/home/moxis/Documents/Github/OJ/STAOJ/JudgeServer/tmp"

lang_config = {
    "py3": configurations.py3_lang_config,
    "py2": configurations.py2_lang_config,
    "java": configurations.java_lang_config,
    "cpp": configurations.cpp_lang_config,
    "c": configurations.c_lang_config
}

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

"""
submission_id
language
max_memory
max_runtime
problem_id
"""
@app.route("/api/evaluate", methods=["POST"])
def evaluate_submission():
    data = request.json

    with CreateEnvironment(data["submission_id"]) as path:
        config = lang_config[data["language"]]
        src = os.path.join(path, config["compile"]["src_name"])

        with open(src, "w+") as f:
            f.write(data["code"])

        try:
            g = Grader(src, config, data["max_memory"], data["max_runtime"], data["problem_id"], path)
        except Exception:
            return Response(json.dumps({"data": "Compilation Error"}), mimetype='application/json')
        else:
            result = g.grade_all()

    
    return Response(json.dumps({"data": result}), mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=False)