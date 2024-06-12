FROM alpine:latest

# 安装必要的软件包
RUN apk update && \
    apk add --no-cache curl bash

# 下载并安装MosDNS
RUN curl -Lo /usr/local/bin/mosdns https://github.com/IrineSistiana/mosdns/releases/latest/download/mosdns-linux-amd64 && \
    chmod +x /usr/local/bin/mosdns

# 创建配置目录
RUN mkdir -p /etc/mosdns

# 复制配置文件
COPY config.yaml /etc/mosdns/config.yaml

# 暴露DNS端口
EXPOSE 53/tcp
EXPOSE 53/udp

# 启动MosDNS
CMD ["mosdns", "-c", "/etc/mosdns/config.yaml"]
