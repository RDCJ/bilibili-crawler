import requests
import json
import time

#保存字典为json
def dic2json(data, path):
    with open(path, "w", encoding='utf-8') as f:
        f.writelines(json.dumps(data, ensure_ascii=False))
    f.close()

#根据bv号获取oid
def get_oid(bvid, header):
    #https://api.bilibili.com/x/player/pagelist?bvid=BV1T5411x7y3&jsonp=jsonp
    url = "http://api.bilibili.com/x/web-interface/archive/stat?bvid={}".format(bvid)
    html = requests.get(url, headers=header)
    data = html.json()
    return data["data"]["aid"]

#评论为嵌套结构，因此递归合并结果
def decodeReply(replies):
    result = []
    for reply in replies:
        result.append(reply['content']['message'])
        if reply['replies'] != None:
            result.extend(decodeReply(reply['replies']))
    return result

#获取一个视频的comment
def getComment(oid, header, p=0, sort=2):
    #oid=视频id，pn=页码
    #sort控制排序顺序，1按时间排序，2按热度排序
    url='https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn={}&type=1&oid={}&sort={}'.format(p+1, oid, sort)
    comments = []
    try:
        html = requests.get(url, headers=header)
        data = html.json()
        replies = data["data"]["replies"]
        comments = decodeReply(replies)
        return comments
    except:
        print(url+'爬取异常')


def main(bv_path, maxp=100, time_gap=5):
    header={"Cookie":"buvid3=05D72C76-38C1-4F69-AC93-B90C56C0907D110236infoc; LIVE_BUVID=AUTO2015623146874484; sid=53khd8hr; CURRENT_FNVAL=16; stardustvideo=1; rpdid=|(u)~J|uYYRJ0J'ulYJ|~Jul~; _uuid=2A50132F-BFC3-E691-823F-99041AAD3E4B52177infoc; im_notify_type_385625993=0; UM_distinctid=16e12522eb7797-0b291c8a138e46-5373e62-144000-16e12522eb855f; laboratory=1-1; DedeUserID=385625993; DedeUserID__ckMd5=8fb7192f0bcda3a1; SESSDATA=7b969aa2%2C1584488173%2Cf651ce21; bili_jct=65262388cd0ecce875f0530143e0ebb7; CURRENT_QUALITY=32; bp_t_offset_385625993=363207981016294510; INTVER=1",
        "User-Agent":"Mozilla/5.0"}

    with open(bv_path,"r") as f:
        bv_list = f.readlines()
    bv_list = [x.replace('\n','') for x in bv_list]

    all_comments = []
    for bvid in bv_list:
        oid = get_oid(bvid, header)
        dic_tmp = {}
        comments = []
        for p in range(maxp):
            time.sleep(time_gap)
            comments.extend( getComment(oid, header, p, sort=2) )
        dic_tmp["bvid"] = bvid
        dic_tmp["comments"] = comments
        all_comments.append(dic_tmp)
        print("%s finished."%(bvid))
    
    dic2json(all_comments, "./all_comments.json")


if __name__=="__main__":
    bv_path = "./bv2.txt"
    main(bv_path, maxp=3)