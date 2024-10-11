#!/bin/bash

# 启动 guacd 容器
docker run --name guacd \
    --network huk_net \
    -p 4822:4822  \
    --platform linux/amd64 \
    -d guacamole/guacd
    docker run  --platform linux/amd64 --name guacd -d -p 4822:4822 dushixiang/guacd:1.5.5 -f -L debug
    docker run --name guacd    --network huk_net     -p 4822:4822      --platform linux/amd64     -d guacamole/guacd     /opt/guacamole/sbin/guacd -b 0.0.0.0 -L debug -f


# 启动 guacamole 容器
docker run --name guacamole \
    -u root \
    --link guacd \
    --link mysql \
    --privileged \
    --platform linux/amd64 \
    -e GUACD_HOSTNAME=guacd \
    -e MYSQL_HOSTNAME=mysql \
    -e MYSQL_DATABASE=guacamole \
    -e MYSQL_USER=root \
    -e MYSQL_PASSWORD=1234567xx \
    -e "EXTENSIONS=auth-quickconnect"   \
    -d -p 8081:8080 \
    --network huk_net \
    guacamole/guacamole