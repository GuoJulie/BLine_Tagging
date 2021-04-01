'''
根据 DICOM数据文件
获取 LungBline数据集
和 lungblineTrainTestlist 训练测试列表
'''
import csv
import math
import tkinter as tk
from subprocess import call
from tkinter import filedialog
import numpy  as np
import pandas as pd
from Setting import *
import os
import re
from DatasetTraitement.DICOMReader import *
import glob


class DatasetPrepare:

    '''
    根据Excel数据文件读取"Centre 1 Tours"文件下的数据，
    并处理成 LungBline数据集 和 lungblineTrainTestlist分类训练测试txt文件
    '''

    def __init__(self,path_dataFolder, excel_path, DEBUG=False):
        print("--------------Fonc: _init_--------------")

        self.DEBUG = DEBUG

        if self.DEBUG:
            try:
                self.DataArbreCreate(path_dataFolder)

                self.xlsxRead(excel_path)

                self.DataArbreWrite()

            except Exception as e: # 稍后测试
                print('数据库准备失败，进程终止')
                # 按 classInd的顺序将 Bline0?0?中的视频路径 写入 trainlist / testlist
                for n in range(len(self.list_path)):
                    with open(self.list_path[n], mode='a+', encoding='utf-8') as f:
                        for i in self.traintestlist[n]:
                            for j in i:
                                # if (j != None):
                                    f.write(j + '\n')

            self.get_train_test_lists()

            self.videoToImage(True)



    # 读取"baseAnnotéeWorkBook.xlsx"数据文件
    def xlsxRead(self,excel_path):
        print("--------------Fonc: xlsxRead--------------")

        try:
            excelData = pd.read_excel(excel_path,1) # 读取第二个工作表中的数据
        except Exception as e:
            print('文件打开失败')
            return e
        else:
            sheet_names = list(excelData.keys())
            sheet_define = ['Patient', 'Exam', 'File Name', 'Irrégularité ligne pleurale',
           'Nb lignes B', 'Score CPI', 'Opérateur']
            if sheet_names != sheet_define:
                print("数据表格式不正确，请参考示例数据表")
            else:
                print("sheet_name: ", sheet_names)
                self.xisxlist = excelData.values
                n_xisxlist = len(self.xisxlist)
                print("可用数据总数：", n_xisxlist)
                print("ex(xisxlist[0]): ", self.xisxlist[0])

                if n_xisxlist % TestPointBase != 0:
                    print("病人测试点数据总数不正确，不是TestPointBase的倍数（测试一次产生TestPointBase个测试数据）,请修改xlsx文件")
                else:
                    n_patient = int(n_xisxlist/TestPointBase)
                    print("病人总数：", n_patient)

                    self.n_trainPatient = int(math.ceil(n_patient * RadioTrainTest))
                    self.n_testPatient = n_patient - self.n_trainPatient
                    print("训练集病人数：", self.n_trainPatient)
                    print("测试集病人数：", self.n_testPatient)



    def DataArbreCreate(self,path_dataFolder):
        print("--------------Fonc: DataArbreCreate--------------")

        self.classInd = ['Bline0104', 'Bline0507', 'Bline0810', 'BlineBlanc']
        self.traintestlist = [[[], [], [], []],
                              [[], [], [], []]]  # [trainlist, testlist] 有classInd

        self.path_dataFolder = path_dataFolder
        path_parent = os.path.dirname(self.path_dataFolder)

        folder_names = ["LungBline", "Data", "lungblineTrainTestlist" ]

        path_LungBline = path_parent + "/" + folder_names[0] # 目录：LungBline
        path_Data = path_parent + "/" + folder_names[1] # 目录：Data
        path_lungblineTrainTestlist = path_parent + "/" + folder_names[2] # 目录：lungblineTrainTestlist
        folder_groups = [path_LungBline, path_Data, path_lungblineTrainTestlist]

        # 创建文件夹： LungBline, Data, lungblineTrainTestlist
        for i in range(len(folder_groups)):
            if not os.path.exists(folder_groups[i]):
                os.makedirs(folder_groups[i])
                print("文件夹 /" + folder_names[i] + " 创建成功")

        # 创建文件夹： Data/train, Data/test
        data_folder_groups = ["train", "test"]
        for i in data_folder_groups:
            path_folder_groups = folder_groups[1] + "/" + i
            if not os.path.exists(path_folder_groups):
                os.makedirs(path_folder_groups)
                print("文件夹 /" + folder_names[1] + "/" + i + " 创建成功")

        # 创建文件夹： LungBline/Bline0?0?
        for i in self.classInd:
            path_Bline = folder_groups[0] + "/" + str(i)
            if not os.path.exists(path_Bline):
                os.makedirs(path_Bline)
                print("文件夹 /" + folder_names[0] + "/" + str(i) + " 创建成功")

        # 创建文件夹： Data/train/Bline0?0?, Data/test/Bline0?0?
        for i in self.classInd:
            for j in data_folder_groups:
                path_Bline = folder_groups[1] + "/" + j + "/" + str(i)
                if not os.path.exists(path_Bline):
                    os.makedirs(path_Bline)
                    print("文件夹 /" + folder_names[1] + "/" + j + "/" + str(i) + " 创建成功")

        # 创建txt文件： lungblineTrainTestlist/classInd.txt
        path_classInd = path_lungblineTrainTestlist + "/" + "classInd.txt"
        if not os.path.exists(path_classInd):
            with open(path_classInd, mode='w', encoding='utf-8') as f:
                j = 1
                for i in self.classInd:
                    f.write(str(j) + ' ' + i + '\n')
                    j = j + 1
            print("/" + folder_names[0] + "/classInd.txt 写入成功")

        # 创建txt文件： lungblineTrainTestlist/trainlist.txt, lungblineTrainTestlist/testlist.txt
        path_trainlist = path_lungblineTrainTestlist + "/" + "trainlist.txt"
        path_testlist = path_lungblineTrainTestlist + "/" + "testlist.txt"
        self.list_path = [path_trainlist, path_testlist]
        for i in range(len(self.list_path)):
            if not os.path.exists(self.list_path[i]):
                with open(self.list_path[i], mode='w', encoding='utf-8') as f:
                    print("/" + folder_names[2] + "/" + os.path.split(self.list_path[i])[1] + " 创建成功")
            else:
                # 读取 trainlist.txt 和 testlist.txt 中的数据 到 traintestlist 中
                with open(self.list_path[i], "r+") as f:
                    for line in f:
                        classid, path_video = os.path.split(line)
                        self.traintestlist[i][self.classInd.index(classid)].append(line.strip('\n'))
                    f.seek(0)
                    f.truncate()  # 清空文件






    def DataArbreWrite(self):
        '''
        将获取的已剪切视频存放到 对应的Bline0?0?文件夹 中
        :return:
        '''
        print("--------------Fonc: DataArbreWrite--------------")

        count = 0
        n_gBline = [0,0,0,0]

        for i in self.xisxlist:
            print("------------------------------------------------------------------------------------------")

            count = count + 1

            tempPath = self.path_dataFolder + "/" + i[0] # eg: /Centre 1 Tours/1Patient 1CP01
            # print("i[0]: ",i[0])
            n_patientID = int(re.findall(r"\d+\.?\d*", i[0])[0])

            if os.path.exists(tempPath):
                if (n_patientID <= 10):
                    tempPath = tempPath + "/1" + "%02d" % n_patientID + i[1] # eg: /Centre 1 Tours/1Patient 1CP01/101M0
                elif(n_patientID < 20 and n_patientID > 10):
                    tempPath = tempPath + "/1" + "%03d" % n_patientID + i[1]  # eg: /Centre 1 Tours/11Patient 1HF11/1011M0
                else:
                    tempPath = tempPath + "/1" + "020" + i[1]  # eg: /Centre 1 Tours/22Patient 1BA22/1020M0

                # print("父路径",tempPath)

                if os.path.exists(tempPath):
                    files = os.listdir(tempPath) # 获取当前文件夹下所有文件（夹）

                    for file in files:  # 遍历文件夹
                        if os.path.isdir(tempPath + "/" + file):  # 判断是否是文件夹，是文件夹则进入
                            tempPath = tempPath + "/" + file + "/" + i[2] # eg: /Centre 1 Tours/23Patient 1RM23/1020M0/201906/20190104
                        else:
                            tempPath = tempPath + "/" + i[2] # eg: /Centre 1 Tours/1Patient 1CP01/101M0/2019010C

                        if os.path.exists(tempPath):
                            self.inputPath_DICOM = tempPath

                            print("inputPath_DICOM - 最终路径",self.inputPath_DICOM)


                path_LungBline = os.path.dirname(self.path_dataFolder) + "/" + "LungBline"
                tempnamelist = [i[0], i[1], i[2]]
                # 根据“Nb lignes B”判断 classID
                if(self.isDigit(i[4]) == False):
                    index = 3
                elif (int(i[4]) <= 4):
                    index = 0
                elif (int(i[4]) >= 5 and int(i[4]) <= 7):
                    index = 1
                else:
                    index = 2

                self.outputPath_VideoCut = path_LungBline + "/" + self.classInd[index]
                n_gBline[index] = n_gBline[index] + 1
                print("outputPath_VideoCut - 最终路径", self.outputPath_VideoCut)

                # videoname = os.path.split(self.outputPath_VideoCut)[1] +
                tempstr = tempnamelist[0] + "_" + tempnamelist[1] + "_" + tempnamelist[2]
                n_count = sum([k.count(tempstr)
                         for i in self.traintestlist
                         for j in i
                         for k in j])
                print("tempstr: ",tempstr)
                for i in self.traintestlist:
                    print("----------------------------------------------------------------")
                    for j in i:
                        print("****************************************************************")
                        for k in j:
                            # if k != None:
                                print(k)
                print("查找：",n_count)
                if (n_count == 0):
                    reader = DICOMReader(self.inputPath_DICOM, self.outputPath_VideoCut, n_gBline[index], tempnamelist, True)
                    print(str(self.classInd[index]) + ": DICOM 转换 AVI 成功")

                    for i in range(len(reader.videonamelist)):
                        print("******: ", i)
                        if (count <= self.n_trainPatient * TestPointBase):
                            self.traintestlist[0][index].append(reader.videonamelist[i])
                        else:
                            self.traintestlist[1][index].append(reader.videonamelist[i])


        # 按 classInd的顺序将 Bline0?0?中的视频路径 写入 trainlist / testlist
        for n in range(len(self.list_path)):
            with open(self.list_path[n], mode='a+', encoding='utf-8') as f:
                for i in self.traintestlist[n]:
                    for j in i:
                        # if (j != None):
                            f.write(j + '\n')


    def isDigit(self,x):
        '''
        判断 xlsx文件 中“Nb lignes B”列 的数据是否为 "#N/A"
        :param x: self.xisxlist[i][4]
        :return: int(x) / False
        '''
        try:
            x=int(x)
            return isinstance(x,int)
        except ValueError:
            return False


    def get_train_test_lists(self):

        # 读取 trainlist.txt 和 testlist.txt 中的数据 到 train_test_list 中
        self.train_test_list = [[], []] # [trainlist,testlist] 每个字符串末尾没有classId
        path_LungBline = os.path.dirname(self.path_dataFolder) + "/" + "LungBline"
        for i in range(len(self.list_path)):
            with open(self.list_path[i], "r+") as f:
                # train 和 test 的 video path
                self.train_test_list[i] = [path_LungBline + "/" + re.split('\d+$', row.strip())[0].strip() for row in list(f)]

        # Set the groups in a dictionary.
        file_groups = {
            'train': self.train_test_list[0],
            'test': self.train_test_list[1]
        }

        # 打印 video path
        for i in self.train_test_list:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++")
            for j in i:
                print(j)




    def videoToImage(self, DEBUG=False):
        print("-------------------Fonc: videoToImage-------------------")

        # 视频路径有了
        # train / test 文件夹 有了

        # 这是 Data的绝对路径
        path_parent = os.path.dirname(self.path_dataFolder)
        path_Data = path_parent + "/" + "Data"  # 目录：Data

        data_file = []
        folders = [path_Data + '/train', path_Data + '/test']

        for i in range(len(self.train_test_list)):
            for j in self.train_test_list[i]:
                if os.path.exists(j):
                    pathdir, video = os.path.split(j)
                    folderclassId = os.path.split(pathdir)[1]
                    videoname = video.split(".")[0]
                    outputFolder_Image = folders[i] + "/" + folderclassId + "/" + str(videoname)
                    if not os.path.exists(outputFolder_Image):
                        os.makedirs(outputFolder_Image)
                        print("文件夹 " + outputFolder_Image + " 创建成功")

                        # Now extract it.
                        call(["ffmpeg", "-i", j, outputFolder_Image + "/" + str(videoname) + "-%04d.jpg"])

                    n_frames_video = len(glob.glob(outputFolder_Image + "/" + str(videoname) + "*.jpg"))

                    data_file.append(
                        ["train" if i == 0 else "test", folderclassId, videoname, n_frames_video])

                    print("Generated %d frames for %s" %
                          (n_frames_video, videoname))

        path_csv = path_Data + "/data_file.csv"
        with open(path_csv, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(data_file)

        print("Extracted and wrote %d video files." % (len(data_file)))



if __name__ == "__main__":
    # root = tk.Tk()
    # root.withdraw()
    # print("请选取DICOM数据文件夹")
    # path_dataFolder = filedialog.askdirectory()  # path of "Centre 1 Tours"
    # print("请选取xlsx数据文件")
    # excel_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")]) # path of "baseAnnotéeWorkBook.xlsx"

    path_dataFolder = "E:/S9_PRD/BLine_Tagging/Dataset/Centre 1 Tours"
    # excel_path = "E:/S9_PRD/BLine_Tagging/Dataset/baseAnnotéeWorkBook-6(3-2).xlsx"
    # excel_path = "E:/S9_PRD/BLine_Tagging/Dataset/baseAnnotéeWorkBook-36(18-2).xlsx"
    excel_path = "E:/S9_PRD/BLine_Tagging/Dataset/baseAnnotéeWorkBook.xlsx"

    print(path_dataFolder)
    print(excel_path)

    DatasetPrepare(path_dataFolder,excel_path,True)
