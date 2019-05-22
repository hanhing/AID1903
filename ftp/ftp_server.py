"""
    ftp 文件服务器
        1.技术分析
            * 并发模型  多线程并发
            * 数据传输  tcp传输

        2.结构设计
            * 客户端发起请求,打印请求提示界面
            * 文件传输功能封装为类

        3.功能分析
            * 网络搭建
            * 查看文件库信息
            * 下载文件
            * 上传文件
            * 客户端退出

        4.协议
            L  表示请求文件列表
"""
"""
    FTP文件服务器
"""
from socket import *
from threading import Thread
import sys,os
from time import sleep

# 全局变量
HOST = "127.0.0.1"
PORT = 8888
ADDR = (HOST, PORT)
FTP = "/home/tarena/month02/day11/FTP/" # 文件库路径
# 将客户端请求功能封装为类
class FtpServer:
    def __init__(self,connfd,FTP_PATH):
        self.connfd =connfd
        self.path = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send("该文件类别为空".encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        fs = ""
        for file in files:
            if file[0] != '.' and os.path.isfile(self.path+file):
                fs += file + '\n' # 添加消息边界
        self.connfd.send(fs.encode())

    def do_get(self,filename):
        try:
            fd = open(self.path+filename,'rb')
        except IOError:
            self.connfd.send('文件不存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        # 发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self,filename):
        if os.path.exists(self.path+filename):
            self.connfd.send('该文件已存在'.encode())
            return
        self.connfd.send(b'OK')
        fd = open(self.path.filename,'wb')
        # 接收文件
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()

# 客户端请求处理函数
def handle(connfd):
    # 选择文件夹
    cls =connfd.recv(1024).decode()
    FTP_PATH = FTP + cls +'/'
    ftp = FtpServer(connfd,FTP_PATH)
    while True:
        # 接收客户端请求
        data = connfd.recv(1024).decode()
        # 如果客户端断开返回data为空
        if not data or data[0] == 'Q':
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)



# 网络搭建
def main():
    s = socket()  # tcp套接字
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)
    print("Listen the port 8888...")
    while True:
        try:
            connfd, addr = s.accept()
        except KeyboardInterrupt:
            print("退出服务程序")
            return
        except Exception as e:
            print(e)
            continue
            # 创建新的线程处理客户端请求
        print("链接客户端:",addr)
        # 创建线程处理请求
        client = Thread(target=handle,args=(connfd,))
        client.setDaemon(True)
        client.start()
if __name__ == '__main__':
    main()
