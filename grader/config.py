# coding=utf-8
from __future__ import unicode_literals

import os
import pwd
import grp

RESULT_COMPILATION_ERROR = -3

DATABASE_URI = "sqlite:////home/moxis/Documents/Github/OJ/STAOJ/MainServer/app.db"

TESTCASE_PATH = "/home/moxis/Documents/Github/OJ/STAOJ/JudgeServer/testcases"
OUTPUT_PATH = "/home/moxis/Documents/Github/OJ/STAOJ/JudgeServer/tmp"

# RUN_USER_UID = pwd.getpwnam("code").pw_uid
# RUN_GROUP_GID = grp.getgrnam("code").gr_gid

# COMPILER_USER_UID = pwd.getpwnam("compiler").pw_uid
# COMPILER_GROUP_GID = grp.getgrnam("compiler").gr_gid

default_env = ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
default_memory = 256 * 1024 * 1024
default_cpu_time = 3000
default_real_time = 5000

""" Code compilation configurations for different languages """
class Configurations:
    configurations = {
        "python3": {
            "compile": {
                "src_name": "solution.py",
                "exe_name": "__pycache__/solution.cpython-37.pyc",
                "max_cpu_time": default_cpu_time,
                "max_real_time": default_real_time,
                "max_memory": default_memory,
                "compile_command": "/usr/bin/python3 -m py_compile {src_path}",
            },
            "run": {
                "command": "/usr/bin/python3 {exe_path}",
                "seccomp_rule": "general",
                "env": ["PYTHONIOENCODING=UTF-8"] + default_env
            }
        },
        "python2": {
            "compile": {
                "src_name": "solution.py",
                "exe_name": "solution.pyc",
                "max_cpu_time": default_cpu_time,
                "max_real_time": default_real_time,
                "max_memory": default_memory,
                "compile_command": "/usr/bin/python -m py_compile {src_path}",
            },
            "run": {
                "command": "/usr/bin/python {exe_path}",
                "seccomp_rule": "general",
                "env": default_env
            }
        },
        "java": {
            "name": "java",
            "compile": {
                "src_name": "Main.java",
                "exe_name": "Main",
                "max_cpu_time": default_cpu_time,
                "max_real_time": default_real_time,
                "max_memory": -1,
                "compile_command": "/usr/bin/javac {src_path} -d {exe_dir} -encoding UTF8"
            },
            "run": {
                "command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k -Djava.security.manager -Dfile.encoding=UTF-8 -Djava.security.policy==/etc/java_policy -Djava.awt.headless=true Main",
                "seccomp_rule": None,
                "env": default_env,
                "memory_limit_check_only": 1
            }
        },
        "cpp": {
            "compile": {
                "src_name": "main.cpp",
                "exe_name": "main",
                "max_cpu_time": default_cpu_time,
                "max_real_time": default_real_time,
                "max_memory": default_memory,
                "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}",
            },
            "run": {
                "command": "{exe_path}",
                "seccomp_rule": "c_cpp",
                "env": default_env
            }
        },
        "c": {
            "compile": {
                "src_name": "main.c",
                "exe_name": "main",
                "max_cpu_time": default_cpu_time,
                "max_real_time": default_real_time,
                "max_memory": default_memory,
                "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c99 {src_path} -lm -o {exe_path}",
            },
            "run": {
                "command": "{exe_path}",
                "seccomp_rule": "c_cpp",
                "env": default_env
            }
        }
    }

    @classmethod
    def get_config(cls, language):
        return cls.configurations.get(language)