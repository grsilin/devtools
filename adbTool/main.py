#!/usr/bin/python

from subprocess import check_output, CalledProcessError

from tempfile import TemporaryFile

import re

import tkinter as tk


class AndroidDevice(object):
    def __init__(self, sn, name, state):
        self.sn = sn
        self.name = name
        self.state = state


def __executeCmd(*args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t)
            return 0, out
        except CalledProcessError as e:
            t.seek(0)
            return e.returncode, t.read()


def executeCmd(cmd):
    cmd = str(cmd)
    args = cmd.split(' ')
    return __executeCmd(*args)


def formatCmd(sn, cmd):
    cmd = "adb -s {} {}".format(sn, cmd)
    return cmd


def bytes2str(bytes):
    return str(bytes, encoding='utf-8')


def getAllDevices():
    cmd = 'adb devices'
    (code, out) = executeCmd(cmd)
    if code != 0:
        print('something is error')
        return False
    outstr = bytes2str(out)
    devices = []
    for item in outstr.split("\r\n"):
        if(re.match("[0-9A-Z]{5,20}[\s]*device", item)):
            device = item.split()
            (code, out) = executeCmd(
                formatCmd(device[0], "shell getprop ro.build.product"))
            devices.append(AndroidDevice(
                device[0], bytes2str(out).strip(), device[1]))
    return devices


def selectDevice():
    print("change to:" + selectDeviceSn.get())


def doExecuteCmd(event):
    allContent = displayText.get("0.0", "end").split("\n")
    last = allContent[len(allContent) - 2]
    print(formatCmd(selectDeviceSn.get(), last))
    (code, result) = executeCmd(formatCmd(selectDeviceSn.get(), last))
    displayText.insert("end", "\r\n")
    displayText.insert("end", bytes2str(result).strip())



size = {"width": 700, "height": 500}

devices = getAllDevices()

root = tk.Tk()  # 创建主窗体
selectDeviceSn = tk.StringVar()
root.title("adb tool")
root.geometry(str(size["width"])+"x"+str(size["height"]))

deviceList = tk.LabelFrame(text='select device')

if(len(devices) > 0):
    # 创建设备列表
    for item in devices:
        print(item.sn + " -> "+item.name+" -> " + item.state)
        r = tk.Radiobutton(deviceList, text=item.name+"/"+item.sn+"/"+item.state,
                           variable=selectDeviceSn, value=item.sn, command=selectDevice)
        r.pack()
    deviceList.pack(side=tk.TOP)
else:
    tk.Label(root, text="no device").pack()

# 命令窗口，暂无TAB
cmdView = tk.LabelFrame(text='command:')
displayText = tk.Text(cmdView)
displayText.bind('<Return>', doExecuteCmd)
displayText.pack()
cmdView.pack(side=tk.BOTTOM)

# 进入消息循环
root.mainloop()
