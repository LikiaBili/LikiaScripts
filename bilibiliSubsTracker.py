import json
from urllib import request
import time
from datetime import datetime

elapsed = -5
pfhelp = 0
defaultuid = 14444480
goal = 200000

uid = int(input("请输入uid,0为默认（白羽千夏）\n输入完成后按回车\n"))

if(uid == 0):
	uid = defaultuid

url = request.urlopen('https://api.bilibili.com/x/relation/stat?vmid='+str(uid))
Data = json.loads(str(url.read().decode('utf-8')))
deffollow = Data['data']['follower']
Follows	= deffollow	
total = 0
unsubs = 0
cleartotal = 0

while('true'):
	pfhelp = Follows
	url = request.urlopen('https://api.bilibili.com/x/relation/stat?vmid='+str(uid))
	Data = json.loads(str(url.read().decode('utf-8')))
	Follows = Data['data']['follower']

	elapsed = elapsed+5

	plusfollow = Follows - pfhelp

	if(plusfollow >= 0):
		total += plusfollow
		plus = "+"
	else:
		unsubs -= plusfollow
		plus = ""

	cleartotal += plusfollow
	fpm = 0
	dpm = 0
	cspm = 0
	if(float(elapsed)/60.0 != 0):
		fpm = float(total)/(float(elapsed)/60.0)
		fpm = float(unsubs)/(float(elapsed)/60.0)
		cspm = float(cleartotal)/(float(elapsed)/60.0)

	print("==============================================")
	print("当前时间"+datetime.now().strftime("%H:%M:%S"))
	if(Follows >= goal):
		print(f"粉丝数:{Follows},每分钟涨粉数:{round(fpm,4)},每分钟掉粉数(不准):{round(dpm,4)},每分钟净涨粉数:{round(cspm,4)} ({plus}{plusfollow})\n自程序运行开始后：涨粉{total} 掉粉{unsubs} \n目标已达成!!!!!!!!!!!!!!!!!!!!!!!")
	else:
		remaining = "[未知]"
		if(fpm > 0):
			remaining = str((goal-Follows)/fpm)
		print(f"粉丝数:{Follows},每分钟涨粉数:{round(fpm,4)},每分钟掉粉数(不准):{round(dpm,4)},每分钟净涨粉数:{round(cspm,4)} ({plus}{plusfollow})\n自程序运行开始后：涨粉{total} 掉粉{unsubs}\n距离目标{str(goal)}粉丝还剩{str(goal-Follows)}，预计需要{remaining}分钟达成目标")
	time.sleep(5)