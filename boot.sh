#!/bin/sh

mkdir -p /judger/run

chown compiler:code /judger/run
chmod 711 /judger/run

rq --version
exec rq worker -u redis://redis:6379 "evaluation-tasks"
