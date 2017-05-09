from bs4 import BeautifulSoup
import requests
import csv
import os.path
import time

def _try_page(url, attempt_number):
    max_attempts = 5
    try:
        response = requests.get(url)
        response.raise_for_status()
    except:
        if attempt_number < max_attempts:
            attempt = attempt_number + 1
            time.sleep(1)
            print("sleeping 1s and try again...attempt = ",2)
            return _try_page(url, attempt_number=attempt)
        else:
            logger.error(e)
            raise RequestError('max retries exceed when trying to get the page at %s' % url)

    return response
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getEPSAAStock(sym,period):
    url = "http://www.aastocks.com/en/stocks/analysis/company-fundamental/earnings-summary?symbol="+sym+"&period="+period
    r  = _try_page(url,1)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    out=""
    ele_str = ""

    #get EPS from aastocks
    table_body = soup.find("div", {"id": "cp_repPLData_Panel8_3"})
    if table_body is not None:
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            for ele in cols:
                #print("ele = " + str(ele))
                ele_str = str(ele)
                ele_str = ele_str.replace(",","")
                #print("ele_str = " + ele_str)
                if is_number(ele_str):
                    out = out + ele_str + "," 
    
    
    return out

def getYearAAStock(sym,period):
    url = "http://www.aastocks.com/en/stocks/analysis/company-fundamental/earnings-summary?symbol="+sym+"&period="+period
    r  = _try_page(url,1)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    out=""
    
    #get Year from aastocks
    table_body = soup.find("div", {"id": "cp_repPLData_Panel5_0"})
    if table_body is not None:
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            for ele in cols:
                #print("ele = " + str(ele))
                if str(ele).find("/") > 0:
                    out = out + str(ele)[:7] + ","         
    
    return out

    
def genEPScsv(sym):
    fy = ""
    eps = ""   
     
    #get FY EPS
    fy_fy = getYearAAStock(sym,"4")
    eps_fy = getEPSAAStock(sym,"4")

    #get HY EPS
    fy_hy = getYearAAStock(sym,"2")
    eps_hy = getEPSAAStock(sym,"2")

    fy_fy_list = fy_fy.split(',')
    eps_fy_list = eps_fy.split(',')
    fy_hy_list = fy_hy.split(',')
    eps_hy_list = eps_hy.split(',')
    #print("fy_list = ", fy_fy)
    #print("fy_eps_list = ", eps_fy)
    #print("hy_list = ", fy_hy)
    #print("hy_eps_list = ", eps_hy)

    i=0 #fy counter
    j=0 #hy counter

    while (i<len(fy_fy_list)-1):
        year_diff = 0
        #print("i=",i)
        #print("j=",j)
        fy_year = int(str(fy_fy_list[i])[:4])
        if fy_hy == "":
            #no half year result
            year_diff = 1
        else:
            if (j < len(fy_hy_list) - 1):
                hy_year = int(str(fy_hy_list[j])[:4])
                year_diff = fy_year - hy_year
            else:
                #wrong data on aa stock, e.g. multiple fy income for same year (2277.HK)
                print("something wrong with this sym: ", sym)
                return
        #print("year_diff=",year_diff)
        if year_diff == 0:
            #intreim result year = full year result year, check which result is announced first
            if (int(str(fy_hy_list[j])[5:]) < int(str(fy_fy_list[i])[5:])) and (int(str(fy_hy_list[j])[5:]) <= 6):
                #print("half year goes first", fy, ",", str(fy_hy_list[j])[5:])
                fy = fy + str(fy_hy_list[j])[:7] + "," + str(fy_fy_list[i])[:7] + ","
                eps = eps + str(eps_hy_list[j]) + "," + str(eps_fy_list[i]) + ","
            else:
                #print("full year goes first", fy, ",", str(fy_hy_list[j])[5:])
                fy1_adjusted = int(str(fy_fy_list[i])[:4]) - 1
                #fy = fy + str(fy_fy_list[i])[:7] + "," + str(fy_hy_list[j])[:7] + ","
                #hard code the adjustment of finicial year
                fy = fy + str(fy1_adjusted) + "/12," + str(fy_hy_list[j])[:5] + "06,"
                eps = eps + str(eps_fy_list[i]) + "," + str(eps_hy_list[j]) + ","

            i = i+1
            j = j+1
            if (i==len(fy_fy_list)-1):
                #at last of fy result, check if next hy result announced or not
                #print("len=",len(fy_hy_list))
                #print("j22=",j)
                fy = fy + str(fy_hy_list[j])[:7]  
                eps = eps + str(eps_hy_list[j]) 
        else:
            #only fy result available
            fy = fy + str(fy_fy_list[i])[:7] + "," 
            eps = eps + str(eps_fy_list[i]) + "," 
            i = i+1

    with open('csv/'+sym+'.csv', 'w') as f:
        f.write(fy)
        f.write("\n")
        f.write(eps)
    f.close()
    
    return
    
def getHKStock():
    #get full list of stock from hkex
    url = "https://www.hkex.com.hk/eng/market/sec_tradinfo/stockcode/eisdeqty.htm"
    r  = _try_page(url,1)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    out=""
    
    rows = soup.find_all("table", class_="table_grey_border")
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        
        for ele in cols:
            if (is_number(str(ele)) > 0 and len(str(ele))==5 and int(str(ele)) < 10000):
                out = out + str(ele) + ","      
    #print ("out = ", out)
    return out

def main():    
    hk_stock = getHKStock()
    hk_stock_list = hk_stock.split(',')
    for stock in hk_stock_list:
        if os.path.isfile('csv/'+stock+'.csv'):
            print ("eps file exists, skipping... ", stock)
        else:
            print("Getting EPS for: ", stock, "....")
            genEPScsv(str(stock))
    return

main()
#print(getHKStock())
#genEPScsv("00001")
#genEPScsv("00016")