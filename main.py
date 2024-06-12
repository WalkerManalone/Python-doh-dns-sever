import socket
from dnslib import DNSRecord, QTYPE, RR, RCODE, A
from dnslib.server import DNSServer, BaseResolver
import dns.resolver
from flask import Flask, request, jsonify, render_template_string
import threading

app = Flask(__name__)

# 定义域名到 IP 地址的映射
domains = {
    '*.google.com.': '142.250.74.60'
}

class CustomResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = request.q.qname
        qtype = request.q.qtype
        qname_str = str(qname)
        
        # 泛域名匹配
        for domain, ip in domains.items():
            if qname_str.endswith(domain):
                reply = request.reply()
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip)))
                return reply

        # 如果域名不存在，使用 1.1.1.1 进行转发查询
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['1.1.1.1']
        try:
            answer = resolver.resolve(qname_str, 'A')
            reply = request.reply()
            for rdata in answer:
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(rdata.address)))
        except dns.resolver.NXDOMAIN:
            reply = request.reply(rcode=RCODE.NXDOMAIN)
        except dns.exception.Timeout:
            reply = request.reply(rcode=RCODE.SERVFAIL)
        
        return reply

resolver = CustomResolver()

def start_dns_server():
    server = DNSServer(resolver, port=8053, address='0.0.0.0')
    server.start()

# 设置DoH接口
@app.route('/dns-query', methods=['GET', 'POST'])
def doh_query():
    if request.method == 'GET':
        dns_query = request.args.get('dns')
    elif request.method == 'POST':
        dns_query = request.data
    else:
        return jsonify({'error': 'Invalid request method'}), 405
    
    query = DNSRecord.parse(dns_query)
    reply = query.send('127.0.0.1', 8053, tcp=True)
    return reply

# 设置主页路由
@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Translate Mirror</title>
        </head>
        <body>
            <h1>Google Translate Mirror</h1>
            <iframe src="https://translate.google.com" width="100%" height="800px"></iframe>
        </body>
        </html>
    ''')

if __name__ == "__main__":
    # 启动DNS服务器线程
    dns_thread = threading.Thread(target=start_dns_server)
    dns_thread.start()

    # 启动Flask应用
    app.run(host='0.0.0.0', port=8000)
