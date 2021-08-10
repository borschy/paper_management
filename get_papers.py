import os
import re
import sys
import urllib
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
# 设置超时
from random import randint
import time
import csv
from tqdm import tqdm
import pickle 

timeout = 5
socket.setdefaulttimeout(timeout)


class Crawler:
    # 睡眠时长
    __time_sleep = 0.1
    __amount = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    # 获取图片url内容等
    # t 下载图片时间间隔
    def __init__(self, t=0.1, save_path="arxiv_data"):
        self.save_path = save_path
        self.time_sleep = t


    def get_val_between(self, text, a, b, ptr, lmt=50):
        try: 
            start_index = text.index(a, ptr)+len(a)
            end_index = text.index(b, start_index-1)
        except ValueError: 
            return False, ptr+1

        val = text[start_index:end_index]

        # if len(val) > lmt: return False, start_index+1
        return val, end_index


    def parse(self, text):
        if text == None: return
        information = {}
        information["title"], end_idx = self.get_val_between(text, '<meta name="citation_title" content="', r'"/>', 0)
        information["authors"] = []
        while True:
            name, end_idx = self.get_val_between(text, 'meta name="citation_author" content="', r'"/>', end_idx)
            if name == False: break
            information["authors"].append(name)
        information["date"], end_idx = self.get_val_between(text, '<meta name="citation_date" content="', r'"/>', 0)
        information["pdf"], end_idx = self.get_val_between(text, '<meta name="citation_pdf_url" content="', r'"/>', 0)
        information["id"], end_idx = self.get_val_between(text, '<meta name="citation_arxiv_id" content="', r'"/>', 0)
        information["abstract"], end_idx = self.get_val_between(text, '<meta name="citation_abstract" content="', r'"/><meta name="twitter:site"', 0)

        information["abstract"] = information["abstract"].replace("\n", " ")

        return information

    
    def download_pdf(self, url, title, date):
        try:
            if not os.path.exists(self.save_path): os.mkdir(self.save_path)
            title = date.replace("/", "") +" "+ title.replace(":", " ") + ".pdf"
            file_path = os.path.join(self.save_path, title)
            # 设置header防403
            time.sleep(self.time_sleep)
            opener = urllib.request.build_opener()
            opener.addheaders = [
                ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'),
            ]
            urllib.request.install_opener(opener)
            # urllib.request.urlretrieve(url, file_path)
            return True
        except urllib.error.HTTPError as urllib_err:
            print(urllib_err)
            return False
        except Exception as err:
            time.sleep(1)
            print(err)
            return False







    def save_csv(self,info_batch):
        if len(info_batch):
            if not os.path.exists(self.save_path): os.mkdir(self.save_path)
            file_path = os.path.join(self.save_path, "paper_info.csv")

            with open(file_path, 'w', encoding="utf-8") as f:  # You will need 'wb' mode in Python 2.x
                w = csv.DictWriter(f, info_batch[0].keys())
                w.writeheader()
                for info in info_batch:
                    if info != None:
                        w.writerow(info)
            print("Save to csv called!")
        else:
            print("Save to csv called but info is empty!")
            


    # 开始获取
    def get_info(self, url):
        blank_links = []
        # 设置header防403
        try:
            time.sleep(self.time_sleep)
            req = urllib.request.Request(url=url, headers=self.headers)
            page = urllib.request.urlopen(req)
            rsp = page.read() # the response is the html, so can't call json.loads(rsp)
            output = rsp.decode('utf-8')
            page.close()

            return output

        except UnicodeDecodeError as e:
            print(e)
            print('-----UnicodeDecodeErrorurl:', url)
            blank_links.append(url)
        except urllib.error.URLError as e:
            print(e)
            print("-----urlErrorurl:", url)
            blank_links.append(url)
        except socket.timeout as e:
            print(e)
            print("-----socket timout:", url)
            blank_links.append(url)
        print(f"Errors: {blank_links}")
            



    def run(self):
        """
        爬虫入口

        """
        info_batch = []
        links = ["https://arxiv.org/abs/2106.11776", "https://arxiv.org/abs/2107.00372", "https://arxiv.org/abs/2108.02947",
                 "https://arxiv.org/abs/1812.05944", "https://arxiv.org/abs/2104.01495", "https://arxiv.org/abs/2103.05423",
                 "https://arxiv.org/abs/2001.05566", ""]

        with tqdm(range(len(links))) as pbar:
            for i in links:
                item_raw_info = self.get_info(i)
                item_dict = self.parse(item_raw_info)
                downloaded = self.download_pdf(item_dict["pdf"], item_dict["title"], item_dict["date"])

                item_dict["downloaded"] = downloaded
                info_batch.append(item_dict)

        self.save_csv(info_batch)
        print("Finished!")
            


if __name__ == '__main__':
    ''' Given a bunch of links, summarize and download them. ?
        I think a search function is too wide a net. 
        For links would also need to estimate link (abstract) similarity. PaddleNLP? '''


    crawler = Crawler(t=1, save_path="arxiv_data/")  # 抓取延迟为 0.05
    crawler.run()