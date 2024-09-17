import requests
import json
import time
import io

bvid = input("input bvid =>")
keywords = []
while True:
    keyword = input("input keyword, #EXIT to continue, #FILE to retrieve data from hitterkwd.txt =>")
    if keyword == "#EXIT":
        break
    if keyword == "#FILE":
        kwdfile = io.open("hitterkwd.txt", mode="r", encoding="utf-8")
        Lines = kwdfile.read().split('\n')
        for kwd in Lines:
            keywords.append(kwd)
        kwdfile.close()
        print("Loaded keywords from hitterkwd.txt")
        break
    keywords.append(keyword)

cookie = input("input cookie, #FILE to retrieve from bilicookie.txt =>")
if cookie == "#FILE":
    cookiefile = io.open("bilicookie.txt", mode="r", encoding="utf-8")
    cookie = cookiefile.read()
    cookiefile.close()

#request api
def getAvid(bvid):
    rjson = fetch(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}")
    return rjson["data"]["aid"]

def commentApi(page,avid):
    return fetch(f"https://api.bilibili.com/x/v2/reply/main?next={page}&type=1&oid={avid}&mode=3")

def fetch(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Cookie':cookie}
    response = requests.get(url=url,headers=headers)
    return response.json()

#logger
def log(message):
    global logfile
    logfile.write(f"{message}\n")
    print(message)

#analayze api
def analayzeComment(comment):
    global keywords
    cText = comment["content"]["message"]
    for kwd in keywords:
        if kwd in cText:
            return True
    return False

def analayzeCommentReplies(comment):
    global keywords,repliesScanned
    replies = comment["replies"]
    hits = []
    for reply in replies:
        if analayzeComment(reply):
            hits.append(reply)
        repliesScanned += 1
    return hits

def hitMessageSingle(comment):
    log(">>>>> Found HIT keyword")
    uid = comment["member"]["mid"]
    uname = comment["member"]["uname"]
    ctime = comment["ctime"]
    msg = comment["content"]["message"]
    log(f"uid{uid} User: {uname}")
    log(f"Timestamp {ctime}")
    log(f"\"{msg}\"")

def hitMessageMulti(replies):
    if len(replies) == 0:
        return
    log(">>>>>>>>>> Found HIT keyword in replies")
    log("Origin Comment:")
    uid = comment["member"]["mid"]
    uname = comment["member"]["uname"]
    ctime = comment["ctime"]
    msg = comment["content"]["message"]
    log(f"uid{uid} User: {uname}")
    log(f"Timestamp {ctime}")
    log(f"\"{msg}\"")
    log("Hitted Replies:")
    for reply in replies:
        uid = reply["member"]["mid"]
        uname = reply["member"]["uname"]
        ctime = reply["ctime"]
        msg = reply["content"]["message"]
        log(f"uid{uid} User: {uname}")
        log(f"Timestamp {ctime}")
        log(f"\"{msg}\"")

#runtime
startTime = time.time()
logfile = io.open(f"CommentScan {startTime} {bvid}.log", mode="w", encoding="utf-8")
commentScanned = 0
repliesScanned = 0
page = 1
retry = 0
avid = getAvid(bvid)

log("""
    ===============================================================================
  / ____|                                   | |   | |  | (_) | | |           
 | |     ___  _ __ ___  _ __ ___   ___ _ __ | |_  | |__| |_| |_| |_ ___ _ __ 
 | |    / _ \\| '_ ` _ \\| '_ ` _ \\ / _ \\ '_ \\| __| |  __  | | __| __/ _ \\ '__|
 | |___| (_) | | | | | | | | | | |  __/ | | | |_  | |  | | | |_| ||  __/ |   
  \\_____\\___/|_| |_| |_|_| |_| |_|\\___|_| |_|\\__| |_|  |_|_|\\__|\\__\\___|_|   
    ===============================================================================
  """)
log("running V1.1 bug patch CommentHitter by Likia")
log("logging following keywords:")
for kwd in keywords:
    log(f"- \"{kwd}\"")
log(f"bvid {bvid} => avid {avid}")

while True:
    try:
        pageComments = commentApi(page,avid)["data"]["replies"]

        if len(pageComments) == 0:
            log(f"No more remaining comments detected. elapsed {time.time() - startTime}, scanned {commentScanned} comments and {repliesScanned} replies in total of {commentScanned+repliesScanned} / {page-1} pages")
            logfile.close()
            exit()

        for comment in pageComments:
            if analayzeComment(comment):
                hitMessageSingle(comment)
            hitMessageMulti(analayzeCommentReplies(comment))
            commentScanned += 1

        log(f"Page {page} done.")
        page += 1
        retry = 0
    except Exception as e:
        retry += 1
        if retry > 5:
            log("Maximum retry exceeded. Exiting Program.")
            logfile.close()
            exit()
        log(f"Unexpected Error Occurred. Retry {retry}")
        log(repr(e))
