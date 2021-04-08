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
    Read the data in the "Centre 1 Tours" folder according to the Excel data file,
    And process into LungBline dataset and lungblineTrainTestlist folder(trainlist + testlist)
    '''

    def __init__(self,path_dataFolder, excel_path, DEBUG=False):
        print("--------------Fonc: _init_--------------")

        self.DEBUG = DEBUG

        if self.DEBUG:
            try:
                self.DataArbreCreate(path_dataFolder)

                self.xlsxRead(excel_path)

                self.DataArbreWrite()

                # self.get_train_test_lists()

                # self.videoToImage()

            except Exception as e:
                print('The database preparation failed and the process was terminated')
                # Write the video path in Bline0?0? into trainlist.txt / testlist.txt in the order of classInd
                for n in range(len(self.list_path)):
                    with open(self.list_path[n], mode='a+', encoding='utf-8') as f:
                        for i in self.traintestlist[n]:
                            for j in i:
                                # if (j != None):
                                    f.write(j + '\n')

            self.get_train_test_lists()

            self.videoToImage()



    def xlsxRead(self,excel_path):
        '''
        Read the "baseAnnotéeWorkBook.xlsx" data file
        :param excel_path: path of data excel (note the number of B lines for each dicom file)
            (here is path of "centre 1 tours")
        :return:
        '''
        print("--------------Fonc: xlsxRead--------------")

        try:
            excelData = pd.read_excel(excel_path,1) # Read the data in the second worksheet
        except Exception as e:
            print('File open failed')
            return e
        else:
            sheet_names = list(excelData.keys())
            sheet_define = ['Patient', 'Exam', 'File Name', 'Irrégularité ligne pleurale',
           'Nb lignes B', 'Score CPI', 'Opérateur']
            if sheet_names != sheet_define:
                print("The format of the data table is incorrect, please refer to the example data table 'baseAnnotéeWorkBook.xlsx'")
            else:
                print("sheet_name: ", sheet_names)
                self.xisxlist = excelData.values
                n_xisxlist = len(self.xisxlist)
                print("Total available data：", n_xisxlist)
                print("ex(xisxlist[0]): ", self.xisxlist[0])

                if n_xisxlist % TestPointBase != 0:
                    print("The total number of test point data of patient is incorrect, not a multiple of 'TestPointBase' ('TestPointBase' data is generated at a time test), please modify the xlsx file")
                else:
                    n_patient = int(n_xisxlist/TestPointBase)
                    print("Total number of patients：", n_patient)

                    self.n_trainPatient = int(math.ceil(n_patient * RadioTrainTest))
                    self.n_testPatient = n_patient - self.n_trainPatient
                    print("Number of patients in training set：", self.n_trainPatient)
                    print("Number of patients in testing set：", self.n_testPatient)



    def DataArbreCreate(self,path_dataFolder):
        '''
        Create some necessary directories and files (the default is initially empty)
        :param path_dataFolder: path of folder DICOM (here is path of "centre 1 tours")
        :return:
        '''
        print("--------------Fonc: DataArbreCreate--------------")

        self.classInd = ['Bline0104', 'Bline0507', 'Bline0810', 'BlineBlanc']
        self.traintestlist = [[[], [], [], []],
                              [[], [], [], []]]  # [trainlist, testlist] have 'classInd'

        self.path_dataFolder = path_dataFolder
        path_parent = os.path.dirname(self.path_dataFolder)

        folder_names = ["LungBline", "Data", "lungblineTrainTestlist" ]

        path_LungBline = path_parent + "/" + folder_names[0] # LungBline
        path_Data = path_parent + "/" + folder_names[1] # Data
        path_lungblineTrainTestlist = path_parent + "/" + folder_names[2] # lungblineTrainTestlist
        folder_groups = [path_LungBline, path_Data, path_lungblineTrainTestlist]

        # Create a folder: LungBline, Data, lungblineTrainTestlist
        for i in range(len(folder_groups)):
            if not os.path.exists(folder_groups[i]):
                os.makedirs(folder_groups[i])
                print("folder: /" + folder_names[i] + " is created successfully")

        # Create a folder: Data/train, Data/test
        data_folder_groups = ["train", "test"]
        for i in data_folder_groups:
            path_folder_groups = folder_groups[1] + "/" + i
            if not os.path.exists(path_folder_groups):
                os.makedirs(path_folder_groups)
                print("folder: /" + folder_names[1] + "/" + i + " is created successfully")

        # Create a folder: LungBline/Bline0?0?
        for i in self.classInd:
            path_Bline = folder_groups[0] + "/" + str(i)
            if not os.path.exists(path_Bline):
                os.makedirs(path_Bline)
                print("folder: /" + folder_names[0] + "/" + str(i) + " is created successfully")

        # Create a folder: Data/train/Bline0?0?, Data/test/Bline0?0?
        for i in self.classInd:
            for j in data_folder_groups:
                path_Bline = folder_groups[1] + "/" + j + "/" + str(i)
                if not os.path.exists(path_Bline):
                    os.makedirs(path_Bline)
                    print("folder: /" + folder_names[1] + "/" + j + "/" + str(i) + " is created successfully")

        # Create a txt file: lungblineTrainTestlist/classInd.txt
        path_classInd = path_lungblineTrainTestlist + "/" + "classInd.txt"
        if not os.path.exists(path_classInd):
            with open(path_classInd, mode='w', encoding='utf-8') as f:
                j = 1
                for i in self.classInd:
                    f.write(str(j) + ' ' + i + '\n')
                    j = j + 1
            print("/" + folder_names[0] + "/classInd.txt is written successfully")

        # Create a txt file: lungblineTrainTestlist/trainlist.txt, lungblineTrainTestlist/testlist.txt
        path_trainlist = path_lungblineTrainTestlist + "/" + "trainlist.txt"
        path_testlist = path_lungblineTrainTestlist + "/" + "testlist.txt"
        self.list_path = [path_trainlist, path_testlist]
        for i in range(len(self.list_path)):
            if not os.path.exists(self.list_path[i]):
                with open(self.list_path[i], mode='w', encoding='utf-8') as f:
                    print("/" + folder_names[2] + "/" + os.path.split(self.list_path[i])[1] + " is created successfully")
            else:
                # Read the data in trainlist.txt and testlist.txt to traintestlist
                with open(self.list_path[i], "r+") as f:
                    for line in f:
                        classid, path_video = os.path.split(line)
                        self.traintestlist[i][self.classInd.index(classid)].append(line.strip('\n'))
                    f.seek(0)
                    f.truncate()  # clear data in txt




    def DataArbreWrite(self):
        '''
        Store the obtained cut video in the corresponding Bline0?0? folder
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

                # print("parent path: ",tempPath)

                if os.path.exists(tempPath):
                    files = os.listdir(tempPath) # Get all files (folders) in the current folder

                    for file in files:  # Traverse folders
                        if os.path.isdir(tempPath + "/" + file):  # Determine whether it is a folder, enter it if it is a folder
                            tempPath = tempPath + "/" + file + "/" + i[2] # eg: /Centre 1 Tours/23Patient 1RM23/1020M0/201906/20190104
                        else:
                            tempPath = tempPath + "/" + i[2] # eg: /Centre 1 Tours/1Patient 1CP01/101M0/2019010C

                        if os.path.exists(tempPath):
                            self.inputPath_DICOM = tempPath

                            print("inputPath_DICOM : ",self.inputPath_DICOM)


                path_LungBline = os.path.dirname(self.path_dataFolder) + "/" + "LungBline"
                tempnamelist = [i[0].split( )[0] + "_" + i[0].split( )[1], i[1], i[2]]
                # Judge the classID according to "Nb lignes B"
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
                print("outputPath_VideoCut : ", self.outputPath_VideoCut)

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
                print("Find n_count = ：",n_count)
                if (n_count == 0):
                    reader = DICOMReader(self.inputPath_DICOM, self.outputPath_VideoCut, n_gBline[index], tempnamelist, True)
                    print(str(self.classInd[index]) + ": DICOM converted AVI successfully")

                    for i in range(len(reader.videonamelist)):
                        print("******: ", i)
                        if (count <= self.n_trainPatient * TestPointBase):
                            # self.traintestlist[0][index].append(reader.videonamelist[i])
                            self.traintestlist[0][index].append(reader.videonamelist[i] + " " + str(1 + self.classInd.index(os.path.split(reader.videonamelist[i])[0])))
                        else:
                            self.traintestlist[1][index].append(reader.videonamelist[i])
                            # self.traintestlist[1][index].append(reader.videonamelist[i] + " " + str(1 + self.classInd.index(os.path.split(reader.videonamelist[i])[1])))



        # Write the video path in Bline0?0? into trainlist.txt / testlist.txt in the order of classInd
        for n in range(len(self.list_path)):
            with open(self.list_path[n], mode='a+', encoding='utf-8') as f:
                for i in self.traintestlist[n]:
                    for j in i:
                        # if (j != None):
                            f.write(j + '\n')


    def isDigit(self,x):
        '''
        Determine whether the data in the "Nb lignes B" column in the xlsx file is "#N/A"
        :param x: self.xisxlist[i][4]
        :return: int(x) / False
        '''
        try:
            x=int(x)
            return isinstance(x,int)
        except ValueError:
            return False


    def get_train_test_lists(self):

        # Read the data in trainlist.txt and testlist.txt to train_test_list
        self.train_test_list = [[], []] # [trainlist,testlist] --> No classId at the end of each string
        path_LungBline = os.path.dirname(self.path_dataFolder) + "/" + "LungBline"
        for i in range(len(self.list_path)):
            if(i == 0):
                with open(self.list_path[i], "r+") as f:
                    # video path in train and test list
                    self.train_test_list[i] = [path_LungBline + "/" + re.split('\d+$', row.strip())[0].strip() for row in list(f)]
                    print("1. ++++++++++++", self.train_test_list[i])
            else:
                with open(self.list_path[i], "r+") as f:
                    # video path in train and test list
                    self.train_test_list[i] = [path_LungBline + "/" + row.strip() for row in list(f)]

        # # Set the groups in a dictionary.
        # file_groups = {
        #     'train': self.train_test_list[0],
        #     'test': self.train_test_list[1]
        # }

        # print video path
        for i in self.train_test_list:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++")
            for j in i:
                print(j)




    def videoToImage(self):
        '''
        Convert the videos in the "LungBline" folder into pictures
        and store them in the corresponding train and test folders under the folder Data,
        and create a data_file.csv file
        :return:
        '''
        print("-------------------Fonc: videoToImage-------------------")

        path_parent = os.path.dirname(self.path_dataFolder)
        path_Data = path_parent + "/" + "Data"  # Data

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
                        print("folder : " + outputFolder_Image + " is created successfully")

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
