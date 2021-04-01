import shutil
import pydicom as dicom
import os
import cv2
import numpy as np
import sys
import tkinter as tk
import math
from tkinter import filedialog
from Setting import *

np.set_printoptions(threshold=sys.maxsize)


class DICOMReader:
    """
    This class reads a DICOM file and extract all its images to a folder.
    All images are extracted without compression and in the TIFF format.
    """

    def __init__(self, inputPath_DICOM, outputPath_VideoCut, n_gBline, tempnamelist, DEBUG=False):
        """
        Read the DICOM file, store the number of image and it's size
        :param inputPath_DICOM: path of the dicom file
        :param outputPath_VideoCut: path of the folder where the generated videos are located
        :return list(Filenames of the cut videos)
        """
        self.pathDicom = inputPath_DICOM
        self.pathVideoFolder = outputPath_VideoCut
        self.n_gBline = n_gBline

        self.path, self.filename = os.path.split(self.pathDicom) # /Centre 1 Tours/1Patient 1CP01/101M0   +   2019010A
        # temppath, tempname = os.path.split(self.path) # /Centre 1 Tours/1Patient 1CP01    +    101M0
        self.tempnamelist = tempnamelist
        self.videofoldername =  os.path.split(self.pathVideoFolder)[1]
        self.DEBUG = DEBUG

        if self.DEBUG:
            print('path:', self.path, 'filename:', self.filename)

        self.ds = dicom.dcmread(self.pathDicom)
        self.nb_images, self.height, self.width = self.ds.pixel_array.shape

        self.get_dicom_details()
        self.extract_images_opencv_dev(True)
        self.extract_videos_opencv_dev(True)

        # for i in self.videonamelist:
        #     print(i)
        #     print(len(self.videonamelist))



    def get_dicom_details(self):
        if self.DEBUG:
            print(self.nb_images, "images", "height", self.height, "width", self.width)

        return self.nb_images, self.height, self.width


    # image pixel: 300*300
    def extract_images_opencv_dev(self, save_to_file=False):

        print("4_temp_img_path: ")

        array_image = []

        # eg: /LungBline/Bline0507/2019010A
        self.temp_imgdir_path = self.pathVideoFolder + "/" + self.filename

        # create a folder
        if not os.path.isdir(self.temp_imgdir_path) and save_to_file:
            os.mkdir(self.temp_imgdir_path)

        for img_index in range(self.nb_images):
            # eg: /LungBline/Bline0507/2019010A/2019010A_0.tiff
            temp_img_path = self.temp_imgdir_path + '/' + self.filename + '_' + str(img_index) + '.tiff'

            # resize_image = self.ds.pixel_array[img_index][100:500, 265:665]  # Clipping coordinates:[y0:y1, x0:x1]
            resize_image = cv2.resize(self.ds.pixel_array[img_index], (SizeVideo[0],SizeVideo[1]), interpolation=cv2.INTER_CUBIC)

            array_image.append(resize_image)
            # self.img_height = resize_image.shape[0]
            # self.img_width = resize_image.shape[1]

            if save_to_file:
                cv2.imwrite(temp_img_path, resize_image, [cv2.IMWRITE_TIFF_COMPRESSION, 1])
                # cv2.imwrite(temp_img_path, resize_image, [cv2.])

        if self.DEBUG:
            print(self.nb_images, 'images saved to', self.filename + "_images")

        return array_image


    #  4 frames par un video
    def extract_videos_opencv_dev(self, save_to_file=False):

        # temp_imgdir_path = os.path.dirname(self.path) + '/' + os.path.split(self.path)[1] + '_Images/' + self.filename + "_images"
        # temp_videodir_path = os.path.dirname(self.path) + '/' + os.path.split(self.path)[1] + '_Videos'


        # create a folder
        # if not os.path.isdir(temp_videodir_path) and save_to_file:
        #     os.mkdir(temp_videodir_path)

        filenum = len([lists for lists in os.listdir(self.temp_imgdir_path) if os.path.isfile(os.path.join(self.temp_imgdir_path, lists))])


        # Fps = 10
        size = (SizeVideo[0], SizeVideo[1])
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # VideoDuration = 10
        n = int(math.floor(filenum / (Fps * VideoDuration)))
        print("filenum = ", filenum)
        print("n = ", n)

        # videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '.avi', fourcc, Fps, size)
        # videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '.mp4', -1, Fps, size)

        self.videonamelist = []

        for i in range(1, n+1):
            videoName = "v_" + self.videofoldername + "_g" + "%03d" % self.n_gBline + "_c" + "%02d" % i + "_" + self.tempnamelist[0] + "_" + self.tempnamelist[1] + "_" + self.tempnamelist[2] + ".avi"
            # videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '_c0' + str(i) + '.mp4', -1, Fps, size)
            videoWriter = cv2.VideoWriter(self.pathVideoFolder + '/' + videoName, fourcc, Fps, size)
            for j in range((i-1)*VideoDuration*Fps,i*VideoDuration*Fps):
                file_path = self.temp_imgdir_path + '/' + self.filename + '_' + str(j) + '.tiff'
                frame = cv2.imread(file_path)
                videoWriter.write(frame)
            videoWriter.release()

            # 追加符合 trainlist.txt / testlist.txt 格式的视频路径 及 classid
            classInd = ['Bline0104', 'Bline0507', 'Bline0810', 'BlineBlanc']
            self.videonamelist.append(self.videofoldername + "/" + videoName + " " + str(1 + classInd.index(self.videofoldername)))

            if self.DEBUG:
                print(videoName + ' saved to', self.pathVideoFolder)

        shutil.rmtree(self.temp_imgdir_path) # 删除 DICOM 对应的 image 文件夹


        # for i in range(0, filenum):
        #     file_path = self.temp_imgdir_path + '/' + self.filename + '_' + str(i) + '.tiff'
        #     frame = cv2.imread(file_path)
        #     videoWriter.write(frame)
        # videoWriter.release()
        #
        # if self.DEBUG:
        #     print(self.filename + '.avi saved to', os.path.split(self.path)[1] + '_Videos')



if __name__ == "__main__":
    # root = tk.Tk()
    # root.withdraw()
    # file_path = filedialog.askopenfilename()

    inputPath_DICOM = "E:/S9_PRD/BLine_Tagging/Dataset/Centre 1 Tours/1Patient 1CP01/101M0/2019010A"
    outputPath_VideoCut = "E:/S9_PRD/BLine_Tagging/Dataset/LungBline/Bline0507"
    n_gBline0507 = 1
    tempnamelist = ["1Patient 1CP01", "M0", "2019010A"]

    # reader = DICOMReader(file_path, True)
    reader = DICOMReader(inputPath_DICOM, outputPath_VideoCut, n_gBline0507, tempnamelist, True)
    # reader.get_dicom_details()
    # # reader.extract_images_opencv_dev(True)
    # reader.extract_images_opencv_dev(True)
    # reader.extract_videos_opencv_dev(True)


