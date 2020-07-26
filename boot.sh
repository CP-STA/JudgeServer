#!/bin/sh
rq worker -u redis://redis-server:6379/0 "evaluation-tasks"