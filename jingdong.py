import requests
import threading
from queue import Queue
import time
import xlwt

def request_queue(queue, headers, allInfo):
    try:
        # 读取队列数据
        q = queue.get()
        response = requests.get(q, headers=headers).json()
        allInfo.append(response)
    except Exception as e:
        print(e)

def get_data(list,type):
    data = []
    # 循环页数
    for i in list:
        # 循环40个数据
        for j in i["datas"]:
            info = []
            title = j["title"]
            city = j["city"]
            currentPrice = j["currentPriceCN"]
            assessmentPrice = j["assessmentPriceCN"]
            if assessmentPrice == '0':
                assessmentPrice = j["marketPriceCN"]
            timeStamp = int(str(j["startTime"])[0:10])
            if type == 0:
                info.append(title)
                info.append(city)
                info.append(currentPrice)
                info.append(assessmentPrice)
            else:
                info.append(title)
                info.append(city)
                info.append(currentPrice)
                info.append(assessmentPrice)
                timeArray = time.localtime(timeStamp)
                otherStyleTime = time.strftime("%m--%d %H:%M", timeArray)
                info.append(otherStyleTime)
            data.append(info)
    return data

def save_excel(filename,list,type):
    # 创建工作簿
    f = xlwt.Workbook()

    # 创建一个sheet
    sheet1 = f.add_sheet(filename, cell_overwrite_ok=True)
    # 设置第一列的width
    col1 = sheet1.col(0)
    col1.width = 256 * 38

    # 初始化第一行
    if type==0:
        row0 = ['标题', '城市', '当前价','评估价']
    else:
        row0 = ['标题', '城市', '当前价','评估价','开始时间']
    for i in range(0, len(row0)):
        sheet1.write(0, i, row0[i])

    # 填写数据
    for m in range(len(list)):
        for n in range(len(list[m])):
            sheet1.write(m+1,n,list[m][n])


    # 保存文件
    f.save("d:\\"+filename+".xls")

def main():
    # 头部伪装
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Referer': 'https://auction.jd.com/'
    }

    auction_url = Queue()
    notice_url = Queue()
    # 将10页的url,放入队列
    for i in range(1, 11):
        auctionUrl = "https://api.m.jd.com/api?appid=paimai-search-soa&functionId=paimai_unifiedSearch&body={%22apiType%22:2,%22page%22:" + str(
            i) + ",%22pageSize%22:40,%22reqSource%22:0,%22childrenCateId%22:%2212728%22}&loginType=3"
        noticeUrl = "https://api.m.jd.com/api?appid=paimai-search-soa&functionId=paimai_unifiedSearch&body={%22apiType%22:2,%22page%22:" + str(
            i) + ",%22pageSize%22:40,%22reqSource%22:0,%22childrenCateId%22:%2212728%22,%22paimaiStatus%22:%220%22}&loginType=3"
        auction_url.put(auctionUrl)
        notice_url.put(noticeUrl)

    # 数据列表
    auction_info = []
    notice_info = []
    for i in range(10):
        threading1 = threading.Thread(target=request_queue, args=(auction_url, headers, auction_info))
        threading2 = threading.Thread(target=request_queue, args=(notice_url, headers, notice_info))
        threading1.start()
        threading2.start()
        if i == 9:
            threading1.join()
            threading2.join()

    # 解析数据
    auction_data = get_data(auction_info,0)
    notice_data = get_data(notice_info, 1)

    # 将数据写入文件
    save_excel("拍卖中房产信息", auction_data, 0)
    save_excel("预告中房产信息", notice_data, 1)

if __name__ == '__main__':
    main()
