import os
import _judger
import hashlib
import subprocess

from grader.config import TESTCASE_PATH, OUTPUT_PATH, RESULT_COMPILATION_ERROR

# TODO: ID and also need to give the user ID permission to read and modify the submission environment

"""Class responsible for sandboxed compilation and execution of submitted code."""
class Grader(object):
    def __init__(self, src, config, max_memory, max_runtime, problem_id, work_dir, job):

        # Setting up all relevant directories.
        self.src = os.path.join(work_dir, src)
        self.work_dir = work_dir
        self.testcase_dir = os.path.join(TESTCASE_PATH, str(problem_id))

        # Configurations
        self.config = config
        self.max_memory = max_memory
        self.max_runtime = max_runtime

        # Compile the code and save the path to executable.
        self.exe_path = self._compile()

        # This is to keep track of progress while the judge is running.
        self.job = job
        self.count = 0
        self.max_count = 0

    def _update_meta(self):
        self.job.meta["progress"] = f"{self.count}/{self.max_count}"
        self.job.save_meta()

    def _compile(self):
        config = self.config["compile"]
        exe_path = os.path.join(self.work_dir, config["exe_name"])
        log_path = os.path.join(self.work_dir, "compiler.log")
        
        # Setting up the compilation command
        command = config["compile_command"].format(src_path=self.src, exe_dir=self.work_dir, exe_path=exe_path).split(" ")

        # Compile the source code
        result = _judger.run(max_cpu_time = config["max_cpu_time"],
                             max_real_time = config["max_real_time"],
                             max_memory = config["max_memory"],
                             max_stack = 128 * 1024 ** 2,
                             max_output_size = 1024 ** 2,
                             max_process_number = _judger.UNLIMITED,

                             exe_path = command[0],
                             input_path = self.src,
                             output_path=log_path,
                             error_path=log_path,

                             args=command[1::],
                             env=["PATH=" + os.getenv("PATH")],
                             log_path="judger.log",
                             seccomp_rule_name=None,

                             # TODO: Be sure to setup correct user ID since executing code on root is very dangerous
                             uid=0,
                             gid=0)
        
        os.remove(log_path)
        if result["result"] == _judger.RESULT_SUCCESS:
            return exe_path
        else:
            return None # Implies compilation error

    def grade_all(self):
        if self.exe_path is None:
            return [{"result": RESULT_COMPILATION_ERROR}]

        ret = []
        testcases = next(os.walk(self.testcase_dir))[1]

        # Save progress into redis queue
        self.max_count = len(testcases)
        self._update_meta()

        for test in testcases:
            ret.append(self._grade(test))
        
        return ret

    def _grade(self, testcase_id):
        config = self.config["run"]
        command = config["command"].format(exe_path=self.exe_path, exe_dir=self.work_dir).split(" ")

        input_path = os.path.join(self.testcase_dir, f"{testcase_id}/in.txt")
        output_path = os.path.join(self.work_dir, f"{testcase_id}.txt")

        result = _judger.run(max_cpu_time = self.max_runtime,
                             max_real_time = self.max_runtime * 2,
                             max_memory = self.max_memory,
                             max_stack = 128 * 1024 ** 2,
                             max_output_size = 16 * 1024 ** 2,
                             max_process_number = _judger.UNLIMITED,
                             exe_path = command[0],
                             args = command[1::],
                             env = ["PATH=" + os.environ.get("PATH", "")] + config.get("env", []),
                             log_path = "judger.log",
                             seccomp_rule_name = config["seccomp_rule"],
 
                             # TODO: Again ID
                             uid = 0,
                             gid = 0,
 
                             memory_limit_check_only = config.get("memory_limit_check_only", 0),
                             input_path = input_path,
                             output_path = output_path,
                             error_path = output_path)
        
        result["id"] = testcase_id
        if result["result"] == _judger.RESULT_SUCCESS:
            if os.path.exists(output_path):
                valid = self._check_diff(testcase_id, output_path)

                if not valid:
                    result["result"] = _judger.RESULT_WRONG_ANSWER
            else:
                result["result"] = _judger.RESULT_WRONG_ANSWER
        
        self.count += 1
        self._update_meta()

        return result

    def _check_diff(self, testcase_id, output_path):
        expected_output = os.path.join(self.testcase_dir, f"{testcase_id}/out.txt")

        # Ignore blank lines and trailing whitespace
        ret = subprocess.call(f"diff -a -Z -B {output_path} {expected_output}", shell=True)

        return not bool(ret)