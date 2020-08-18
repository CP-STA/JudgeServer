#!/bin/sh
rq --version
exec rq worker -u redis://redis:6379 "evaluation-tasks"