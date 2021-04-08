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
    All images are extracted with compression of parameter SizeVideo and in the TIFF format.
    All image converted videos are in avi format.
    """

    def __init__(self, inputPath_DICOM, outputPath_VideoCut, n_gBline, tempnamelist, DEBUG=False):
        """
        :param inputPath_DICOM: path of the dicom file
        :param outputPath_VideoCut: path of the folder where the generated videos are located
        :param n_gBline: The predicted position of the video in Bline0?0? (the ?th group video in folder Bline0?0?)
        :param tempnamelist: a few columns in the excel file --> [excel[0], excel[1], excel[2]]
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
        '''
        Get some information about DICOM files
        :return: Number of images in DICOM file, image length and width
        '''
        if self.DEBUG:
            print(self.nb_images, "images", "height", self.height, "width", self.width)

        return self.nb_images, self.height, self.width


    def extract_images_opencv_dev(self, save_to_file=False):
        '''
        Read the images in DICOM and save them in the folder
        resize image pixel with 300*300 (SizeVideo)
        :param save_to_file: True / False
        :return array_image: the read image is stored in an array
        '''

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


    def extract_videos_opencv_dev(self, save_to_file=False):
        '''
        Convert Image to video based on Fps and VideoDuration, and save the video path to the videonamelist
        :param save_to_file: True / False
        :return:
        '''

        filenum = len([lists for lists in os.listdir(self.temp_imgdir_path) if os.path.isfile(os.path.join(self.temp_imgdir_path, lists))])

        size = (SizeVideo[0], SizeVideo[1])
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        n = int(math.floor(filenum / (Fps * VideoDuration)))
        print("filenum = ", filenum)
        print("n = ", n)

        self.videonamelist = []

        for i in range(1, n+1):
            videoName = "v_" + self.videofoldername + "_g" + "%03d" % self.n_gBline + "_c" + "%02d" % i + "_" + self.tempnamelist[0] + "_" + self.tempnamelist[1] + "_" + self.tempnamelist[2] + ".avi"
            videoWriter = cv2.VideoWriter(self.pathVideoFolder + '/' + videoName, fourcc, Fps, size)
            for j in range((i-1)*VideoDuration*Fps,i*VideoDuration*Fps):
                file_path = self.temp_imgdir_path + '/' + self.filename + '_' + str(j) + '.tiff'
                frame = cv2.imread(file_path)
                videoWriter.write(frame)
            videoWriter.release()

            # classInd = ['Bline0104', 'Bline0507', 'Bline0810', 'BlineBlanc']
            # self.videonamelist.append(self.videofoldername + "/" + videoName + " " + str(1 + classInd.index(self.videofoldername)))

            self.videonamelist.append(self.videofoldername + "/" + videoName)

            if self.DEBUG:
                print(videoName + ' saved to', self.pathVideoFolder)

        shutil.rmtree(self.temp_imgdir_path) # Delete the image folder corresponding to DICOM

        # if self.DEBUG:
        #     print(self.filename + '.avi saved to', os.path.split(self.path)[1] + '_Videos')



if __name__ == "__main__":
    # root = tk.Tk()
    # root.withdraw()
    # file_path = filedialog.askopenfilename()

    # test - delete
    inputPath_DICOM = "E:/S9_PRD/BLine_Tagging/Dataset/Centre 1 Tours/1Patient 1CP01/101M0/2019010A"
    outputPath_VideoCut = "E:/S9_PRD/BLine_Tagging/Dataset/LungBline/Bline0507"
    n_gBline0507 = 1
    tempnamelist = ["1Patient 1CP01", "M0", "2019010A"]

    reader = DICOMReader(inputPath_DICOM, outputPath_VideoCut, n_gBline0507, tempnamelist, True)


