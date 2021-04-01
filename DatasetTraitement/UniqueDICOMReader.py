import pydicom as dicom
import os
import cv2
import numpy as np
import sys
import tkinter as tk
import math
from tkinter import filedialog

np.set_printoptions(threshold=sys.maxsize)


class DICOMReader:
    """
    This class reads a DICOM file and extract all its images to a folder.
    All images are extracted without compression and in the TIFF format.
    """

    # those coordinates correspond to the sub rectangle containing only the interesting part of the ultra sound image
    x1 = [120, 90]
    X2 = [120, 495]
    X3 = [800, 495]
    X4 = [800, 90]
    xmin = 120
    xmax = 800
    ymin = 90
    ymax = 495

    def __init__(self, image_filename, DEBUG=False):
        """
        Read the DICOM file, store the number of image and it's size
        :param image_filename: path of the dicom file
        """
        self.image_path = image_filename
        self.path, self.filename = os.path.split(self.image_path)
        self.DEBUG = DEBUG

        if self.DEBUG:
            print('path:', self.path, 'filename:', self.filename)

        self.ds = dicom.dcmread(self.image_path)
        self.nb_images, self.height, self.width = self.ds.pixel_array.shape

    def get_dicom_details(self):
        if self.DEBUG:
            print(self.nb_images, "images", "height", self.height, "width", self.width)

        return self.nb_images, self.height, self.width

    # image pixel: 300*300
    def extract_images_300_opencv_dev(self, save_to_file=False):

        print("4_temp_img_path: ")

        array_image = []

        temp_dir_path = os.path.dirname(self.path) + '/' + os.path.split(self.path)[
            1] + '_Images'
        print("Img - temp_dir_path :", temp_dir_path)

        temp_imgdir_path = os.path.dirname(self.path) + '/' + os.path.split(self.path)[
            1] + '_Images/' + self.filename + "_images"
        print("Img - temp_imgdir_path :", temp_imgdir_path)

        # create a folder
        if not os.path.isdir(temp_dir_path) and save_to_file:
            os.mkdir(temp_dir_path)

        if not os.path.isdir(temp_imgdir_path) and save_to_file:
            os.mkdir(temp_imgdir_path)

        for img_index in range(self.nb_images):
            temp_img_path = temp_imgdir_path + '/' + self.filename + '_' + str(img_index) + '.tiff'
            print("Img - temp_img_path :", temp_img_path)

            # resize_image = self.ds.pixel_array[img_index][100:500, 265:665]  # Clipping coordinates:[y0:y1, x0:x1]
            resize_image = cv2.resize(self.ds.pixel_array[img_index], (300, 300), interpolation=cv2.INTER_CUBIC)

            array_image.append(resize_image)
            self.img_height = resize_image.shape[0]
            self.img_width = resize_image.shape[1]

            if save_to_file:
                cv2.imwrite(temp_img_path, resize_image, [cv2.IMWRITE_TIFF_COMPRESSION, 1])
                # cv2.imwrite(temp_img_path, resize_image, [cv2.])

        if self.DEBUG:
            print(self.nb_images, 'images saved to', self.filename + "_images")

        return array_image

    #  4 frames par un video
    def extract_videos_opencv_dev(self, save_to_file=False):

        temp_imgdir_path = os.path.dirname(self.path) + '/' + os.path.split(self.path)[
            1] + '_Images/' + self.filename + "_images"
        temp_videodir_path = os.path.dirname(self.path) + '/' + os.path.split(self.path)[1] + '_Videos'

        # create a folder
        if not os.path.isdir(temp_videodir_path) and save_to_file:
            os.mkdir(temp_videodir_path)

        filenum = len(
            [lists for lists in os.listdir(temp_imgdir_path) if os.path.isfile(os.path.join(temp_imgdir_path, lists))])

        fps = 10
        size = (self.img_width, self.img_height)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        time = 10
        n = int(math.floor(filenum / (fps * time)))
        print("filenum = ", filenum)
        print("n = ", n)

        # videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '.avi', fourcc, fps, size)
        # videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '.mp4', -1, fps, size)

        for i in range(1, n + 1):
            # videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '_c0' + str(i) + '.mp4', -1, fps, size)
            videoWriter = cv2.VideoWriter(temp_videodir_path + '/' + self.filename + '_c0' + str(i) + '.avi', fourcc,
                                          fps, size)
            for j in range((i - 1) * time * fps, i * time * fps - 1):
                file_path = temp_imgdir_path + '/' + self.filename + '_' + str(j) + '.tiff'
                frame = cv2.imread(file_path)
                videoWriter.write(frame)
            videoWriter.release()

            if self.DEBUG:
                print(self.filename + '_c0' + str(i) + '.avi saved to', os.path.split(self.path)[1] + '_Videos')

        # for i in range(0, filenum):
        #     file_path = temp_imgdir_path + '/' + self.filename + '_' + str(i) + '.tiff'
        #     frame = cv2.imread(file_path)
        #     videoWriter.write(frame)
        # videoWriter.release()
        #
        # if self.DEBUG:
        #     print(self.filename + '.avi saved to', os.path.split(self.path)[1] + '_Videos')


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    reader = DICOMReader(file_path, True)
    reader.get_dicom_details()
    # reader.extract_images_opencv_dev(True)
    reader.extract_images_300_opencv_dev(True)
    reader.extract_videos_opencv_dev(True)

    # inputPath_DICOM = "E:/S9_PRD/BLine_Tagging/Dataset/Centre 1 Tours/1Patient 1CP01/101M0/2019010A"
    # outputPath_VideoCoupe = "E:/S9_PRD/BLine_Tagging/Dataset/LungBline/Bline0507"
    # n_gBline0507 = 1