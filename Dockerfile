FROM alpine:latest

# 安装必要的软件
RUN apk update && apk add --no-cache mosdns

# 复制配置文件
COPY config.yaml /etc/mosdns/config.yaml

# 暴露DNS端口
EXPOSE 53/tcp
EXPOSE 53/udp

# 启动MosDNS
CMD ["mosdns", "-c", "/etc/mosdns/config.yaml"]
