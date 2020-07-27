#!/bin/sh
rq --version
exec rq worker -u redis://redis-server:6379 "evaluation-tasks"