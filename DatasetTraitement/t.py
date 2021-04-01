import re
import os

# string = "09Patient 1TM09"
# patientID = int(re.findall(r"\d+\.?\d*", string)[0])
# print(patientID)

# list_path = ["aaa.txt", "bbb.txt"]
# traintestlist = [[["train0"],["train1"],["train2"],["train3"]],[["test0"], ["test1"], ["test2"], ["test3"]]]
#
# for n in range(len(list_path)):
#     with open(list_path[n], mode='a+', encoding='utf-8') as f:
#         icount = 0
#         for i in traintestlist[n]:
#             icount = icount + 1
#             for j in i:
#                 f.write(j + ' ' + str(icount) + '\n')

# path_testlist = "test.txt"
# if not os.path.exists(path_testlist):
#     with open(path_testlist, mode='w', encoding='utf-8') as f:
#         print("\"test.txt\" 创建成功")
# else:
#     with open(path_testlist, "r+") as f:
#         f.seek(0)
#         f.truncate()  # 清空文件
from subprocess import call
from sys import path

classInd = ['Bline0104', 'Bline0507', 'Bline0810', 'BlineBlanc']
list_path = ["trainlist.txt", "testlist.txt"]
traintestlist = [[[], [], [], []],
                 [[], [], [], []]]  # [trainlist, testlist]
for i in range(len(list_path)):
    with open(list_path[i], "r+") as f:
        for line in f:
            classid, path_video = os.path.split(line)
            print("classid: ", classid)
            print("path_video: ", path_video)
            traintestlist[i][classInd.index(classid)].append(line.strip('\n'))

        # f.seek(0)
        # f.truncate()  # 清空文件

for i in traintestlist:
    print("----------------------------------------------------------------")
    for j in i:
        print("****************************************************************")
        for k in j:
            # if k != None:
                print(k)

tempstr1 = "1Patient 1CP01_M0_2019010A"
tempstr2 = "Bline0507/v_Bline0507_g001_c02_1Patient 1CP01_M0_2019010A.avi 1"

# n_count = sum([k.count(tempstr1)
#         for i in traintestlist if i != None
#         for j in i if j != None
#         for k in j if k != None ])
# print(n_count)
# if(n_count == 0):
#     print(False)
# else:
#     print(True)

# print(tempstr2.strip().split(' '))
print(tempstr2.strip())
print(re.split('\d+$',tempstr2.strip())[0].strip())
print(re.split('\d+$',tempstr2)[0].strip())

tlist = [[],[]]
for i in range(len(list_path)):
    with open(list_path[i], "r+") as f:
        print("-----------------------------------------")
        for row in list(f):
            temp_path = re.split('\d+$', row.strip())[0].strip()
            print("temp_path: ", temp_path)
            tlist[i].append(temp_path)


for i in tlist:
    print("===================================")
    print(i)

video_path = "E:/S9_PRD/BLine_Tagging/v_Bline0810_g001_c01_3Patient 1DR03_M0_2019010C.avi"
pathdir, video = os.path.split(video_path)
videoname = video.split(".")[0]
outputFolder_Image = pathdir + "/" + str(videoname)
if not os.path.exists(outputFolder_Image):
    os.makedirs(outputFolder_Image)
    call(["ffmpeg", "-i", video_path, outputFolder_Image + "/image-%04d.jpg"])

import cv2
tmppath = "E:\S9_PRD\BLine_Tagging" + "\\" +"v_Bline0810_g001_c01_3Patient 1DR03_M0_2019010C.avi"
print(tmppath)
# vc = cv2.VideoCapture(tmppath) #读入视频文件
# print(vc)
# c=0
# rval=vc.isOpened()
# #timeF = 1  #视频帧计数间隔频率
# while rval:   #循环读取视频帧
#     c = c + 1
#     rval, frame = vc.read()
# #    if(c%timeF == 0): #每隔timeF帧进行存储操作
# #        cv2.imwrite('smallVideo/smallVideo'+str(c) + '.jpg', frame) #存储为图像
#     if rval:
#         cv2.imwrite('driveway-320x240/driveway-320x240'+str(c).zfill(8) + '.jpg', frame) #存储为图像
#         cv2.waitKey(1)
#     else:
#         break
# vc.release()