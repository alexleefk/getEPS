import os
import sys

def merge_csv(src_path, out_path):
    file_no=0
    try:
        for filename in os.listdir(src_path):
            header_list = []
            fy_list = []
            eps_list = []
            start_year = 0
            end_year = 0
            curr_year = 0
            if os.path.isfile(src_path + "\\" + filename):
                with open(src_path + "\\" + filename) as f:
                    #assumption: file only contains 2 lines, fincial year and eps
                    print("Merging....",filename)
                    content = f.readlines()
                    # remove whitespace characters like `\n` at the end of each line
                    content = [x.strip() for x in content] 
                    if len(content) >1:
                        fy_list = content[0].split(',')
                        eps_list = content[1].split(',')
                    else:
                        continue
                    
                    #write output to file
                    output = ""
                    
                    #processing the first eps file, write header
                    if file_no == 0:
                        if (len(fy_list) >0) and start_year==0:
                            start_year = int(str(fy_list[0])[:4])-1
                            end_year = int(str(fy_list[len(fy_list)-2])[:4])+1
                        output = "code,"
                        curr_year = start_year
                        while (curr_year <= end_year):
                            output = output + str(curr_year) + "H1," + str(curr_year) + "H2," 
                            header_list.append(str(curr_year) + "H1")
                            header_list.append(str(curr_year) + "H2")
                            if curr_year == end_year:
                                output = output + "\n"
                            curr_year = curr_year + 1
                            

                        with open(out_path+'\esp_all.csv', 'w') as o:
                            o.write(output)
                        o.close()
                        file_no = file_no +1
                    
                    i=1 #index to header_list
                    j=0 #index to fy_list
                    output = str(filename)[:5] + ","
                    
                    #get header from output file
                    with open(out_path+'\esp_all.csv') as r:
                        content = r.readline()
                        #print("content="+str(content))
                        header_list = str(content).split(',')
                    r.close()                       
                    
                    
                    while (i < len(header_list)-1):
                        print("header = " + str(header_list[i])[:4] +" , fy = "+str(fy_list[j])[:4]+" , eps = "+str(eps_list[j]))
                        print("j = " + str(j) + "   len(fy_list) = "+ str(len(fy_list))+ " i= " + str(i))
                        if (j >= len(fy_list)-1):
                            if len(str(fy_list[j])) > 0:
                                output = output + "," + str(eps_list[j])
                                print("output in last eps = ", output)
                            else:
                                #no more data in fy/eps list
                                print("no more data in fy/eps list ")
                            break
                            
                        if int(str(header_list[i])[:4]) < int(str(fy_list[j])[:4]):
                            #header contains a year where fy doesn't have
                            i = i+1
                            output = output + ","
                            print("output in fy missing = ", output)
                            continue
                            
                        elif int(str(header_list[i])[:4]) == int(str(fy_list[j])[:4]):
                            #header contains a year where fy presence, check if both hy and fy result appears
                            print("FY matched = ", str(header_list[i])[:4] +", "+str(fy_list[j])[:4]+","+str(j)+" , "+str(len(fy_list)-2))
                            if j < len(fy_list)-2 : #make sure array won't overflow
                                if (int(str(fy_list[j])[:4]) == int(str(fy_list[j+1])[:4])):
                                    #both fy and hy result exist, display fy result as 2H result only
                                    output = output + str(eps_list[j]) + "," + str(float(eps_list[j+1]) - float(eps_list[j])) 
                                    print("output in fyhy = ", output)
                                    j = j+2
                                else:
                                    #only fy result exists
                                    if int(str(fy_list[j])[5:]) <= 6:
                                        output = output + str(eps_list[j]) 
                                        print("output in hy only = ", output)
                                    else:
                                        output = output + "," + str(eps_list[j]) 
                                        print("output in fy only = ", output)
                                    j = j+1
                            else:
                                #only fy result exists
                                if int(str(fy_list[j])[5:]) <= 6:
                                    output = output + str(eps_list[j]) 
                                    print("output in hy only = ", output)
                                else:
                                    output = output + "," + str(eps_list[j]) 
                                    print("output in fy only = ", output)
                                j = j+1
                        
                        else:
                            print("something wrong while merging...." + filename+"i=" +str(i), "j="+str(j))
                        i = i+1
                    #print("ending loop length of header list: " + str(len(header_list)))
                    #print("file no = " + str(file_no))
                    with open(out_path+'\esp_all.csv', 'a') as o:
                        output = output + "\n"
                        #print("output1 = ", output)
                        o.write(output)
                    o.close()
                f.close()

                
    except:
        print("Unexpected error:"+ str(sys.exc_info()[0]))
        raise
        
    return
    
src_path = os.getcwd() + "\\csv"
merge_csv(src_path, os.getcwd())