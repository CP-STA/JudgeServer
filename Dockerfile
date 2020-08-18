FROM ubuntu:18.04

WORKDIR /home/judgeserver
COPY build/java_policy /etc

RUN buildDeps='software-properties-common git libtool cmake python-dev python3-pip python-pip libseccomp-dev' && \
    apt-get update && apt-get install -y python python3 python-pkg-resources python3-pkg-resources gcc g++ $buildDeps

RUN add-apt-repository ppa:openjdk-r/ppa && add-apt-repository ppa:longsleep/golang-backports && apt-get update && apt-get install -y golang-go openjdk-8-jdk

# This is for Postgres
RUN apt install -y libpq-dev

# Installing the sandboxed executor
RUN cd /tmp && git clone -b newnew --depth 1 https://github.com/QingdaoU/Judger && cd Judger && \
    mkdir build && cd build && cmake .. && make && make install && cd ../bindings/Python && python3 setup.py install

RUN apt-get purge -y --auto-remove $buildDeps
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN mkdir tmp

COPY grader grader
COPY testcases testcases
COPY server.py unbuffer.c boot.sh ./
RUN chmod +x boot.sh

RUN gcc -shared -fPIC -o unbuffer.so unbuffer.c
EXPOSE 6379
ENTRYPOINT ["./boot.sh"]



