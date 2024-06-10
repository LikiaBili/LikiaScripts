import requests
import json
import time
import logging
from pycqBot import cqHttpApi, cqLog
from urllib import request

print("BOOTING!\n"*10)
remainingMessage = ""
maxTimestamp = 0
runTime = 0

################################################################

#Prefences
doAsk = True
sendToGroup = True

runTime = 0

################################################################

def getDynamicLinkResponce(link,dynamicid):
    global cookie
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0', 'Cookie':cookie}
        response = requests.get(url=link,headers=headers)
    except:
        print('|||请求出现异常错误|||')
        return -1
    if(response.status_code == 200):
        data = response.json()
        if(data['code'] == 0):
            if 'cards' in data['data']:
                return data['data']['cards'][dynamicid]
            print("？这个人没有任何动态哩")
            return -1
        else:
            print('API返回错误信息，信息：'+data['msg'])
            return -1
    else:
        print('API请求失败,状态码'+str(response.status_code))
        print(response.json())
        return -1

################################################################

#解析返回数据
def send(message):
    global remainingMessage
    remainingMessage += message + "\n"


def printSend():
    global remainingMessage
    print(""+remainingMessage)


def sendEnd(from_id):
    global remainingMessage,groupid
    print("Send Message:"+remainingMessage)
    if sendToGroup:
        cqapi.send_group_msg(from_id,remainingMessage)
    else:
        cqapi.send_private_msg(2141363802,remainingMessage)
    remainingMessage = ""


def justSend(message,from_id):
    global groupid
    print("Send Message:"+message)
    if sendToGroup:
        cqapi.send_group_msg(from_id,message)
    else:
        cqapi.send_private_msg(2141363802,remainingMessage)

################################################################

def Reslove(dynamic):
    #解压
    dynamiccard = json.loads(dynamic['card'])
    dt = dynamic['desc']['type']
    #输出基本数据
    send(f"用户：\"{dynamic['desc']['user_profile']['info']['uname']}\"的动态")
    send("动态类型："+str(dt))
    #根据动态类型分析数据并输出
    if(dt == 8):
        send("动态原文：")
        send(f"{dynamiccard['dynamic']}\n\n")
        send("发布视频：")
        send(f"《{dynamiccard['title']}》")
        send(">>>https://bilibili.com/video/"+dynamic['desc']['bvid']+"<<<")
        send(f"[CQ:image,file={dynamiccard['pic']}]")
        print(dynamiccard)
        send("视频简介：\n"+dynamiccard['desc'])
    elif(dt == 1):
        #WIP BUG: cant reconize retweet dynamic
        send("\n"+dynamiccard['item']['content'])
        #解析转发视频
        if 'origin' in dynamiccard:
            origin = json.loads(dynamiccard['origin'])
            try:
                send("\n转发视频："+origin['title'])
                send("视频作者："+origin['owner']['name']+f"[CQ:image,file={origin['owner']['face']}]")
                send(f"[CQ:image,file={origin['pic']}]")
                send("视频简介：\n"+origin['desc'])
            except:
                send("\n转发内容解析失败，请自行查看动态内容")
            #send(str(origin))
    elif(dt == 4):
        send("内容:\n"+dynamiccard['item']['content'])
        #是否包含卡片
        if 'add_on_card_info' in dynamic['display']:
            attachcard = dynamic['display']['add_on_card_info'][0]
            showtype = attachcard['add_on_card_show_type']
            #根据卡片类型输出卡片内容
            if(showtype == 5):
                send('分享视频：'+attachcard['ugc_attach_card']['title'])
    elif(dt == 2):
        send("内容:\n"+dynamiccard['item']['description'])
        for i in range(dynamiccard['item']['pictures_count']):
            if i == 0:
                send("分享图片：")

            send(f"[CQ:image,file={dynamiccard['item']['pictures'][i]['img_src']}]")
    else:
        send("未知动态类型，无法解析")

################################################################
oncejob_i = 0

def oncejob(from_id):
    global oncejob_i,groupid
    oncejob_i += 1
    if(oncejob_i == 2):
        resp = getDynamicLinkResponce(link,0)
        Reslove(resp)
        printSend()
        sendEnd(groupid)

def timejob(from_id):
    global maxTimestamp,remainingMessage,runTime,groupid
    remainingMessage = ""
    newest = getDynamicLinkResponce(link,0)
    if(newest == -1): #如果返回值异常则跳过判断
        print("返回值异常")
        return
    #print(dyid)
    #print(previd)
    #print(uid)
    if(newest['desc']['timestamp'] > maxTimestamp):
        send(newest['desc']['user_profile']['info']['uname']+"发布动态更新！")
        print(newest['desc']['user_profile']['info']['uname']+"发布动态更新！")
        Reslove(newest)
        sendEnd(groupid)
        maxTimestamp = newest['desc']['timestamp']
    runTime = runTime + 5
    if runTime%21600 == 0:
        cqapi.send_group_msg(962918748,f"程序本次运行已运行{(runTime/3600.0)*40}分钟 (Fixed, inter3600s = 40min)")

################################################################

defaultuid = 14444480
if doAsk:
    uid = int(input('输入用户uid\n0为默认（白羽千夏）\n-1为Likia(测试用)\n输入其他数为特定uid\n比如输入114514查询uid114514的动态((\n=>'))
    if(uid == 0):
        uid = defaultuid
    if(uid == -1):
        uid = 514993873
    link = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid='+str(uid)
    if(sendToGroup):
        groupid = int(input("请输入群聊号，\n0:私人测试群\n1:白羽千夏二群\n2:塞琳催更二群\n=>"))
        if(groupid == 0):
            groupid = 962918748
        elif(groupid == 1):
            groupid = 455527686
        elif(groupid == 2):
            groupid = 966375491
    else:
        groupid = 962918748
    order = int(input('请在这里输入你想要获取的动态序号\n最新的第一个输入0，最新的第二个输入1，以此类推，如果想要实时更新最新数据请输入-1\n=>'))
    cookie = input('请在这里复制你的账号Cookie信息. 本脚本使用的API需要你的Cookie才能访问. \n你的Cookie可以被用来登录你的账号，我们不会储存这个信息，请妥善保管. \n如果你输入#TEXTFILE 我们将会从同目录的bilicookie.txt获取你的cookie.\n =>>> ')
    if cookie == "#TEXTFILE":
        cookiefile = open("bilicookie.txt","r")
        cookie = cookiefile.read()
        cookiefile.close()
else:
    uid = defaultuid
    groupid = 455527686
    order = -1
    cookiefile = open("bilicookie.txt","r")
    cookie = cookiefile.read()
    cookiefile.close()

#################################################################

if order >= 0:
    cqapi = cqHttpApi()
    bot = cqapi.create_bot(
        group_id_list=[
        groupid
        ],
    )
    bot.timing(oncejob, "onceJob", {
        "timeSleep": 10
    })
    bot.start()
else:
    # 启用日志 默认日志等级 DEBUG
    cqapi = cqHttpApi()
    maxTimestamp = getDynamicLinkResponce(link,0)['desc']['timestamp']
    bot = cqapi.create_bot(
        group_id_list=[
            groupid
        ],
    )

    # bot 会自动新开一个名为 timejob 的线程
    bot.timing(timejob, "timejob", {
        # 每隔5秒
        "timeSleep": 5
    })

    bot.start()
