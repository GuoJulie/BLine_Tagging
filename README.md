# BLine_Tagging
 P3D + pytorch + dataset : LungBline 
 

## Pseudo-3D Residual Networks

This repo implements the network structure of P3D[1] with PyTorch, pre-trained model weights are converted from caffemodel, which is supported from the [author's repo](https://github.com/ZhaofanQiu/pseudo-3d-residual-networks)


### Requirements:

- pytorch
- numpy
- ffmpeg (for extract image frames from videos)

### Pretrained weights

1, P3D-199 trained on Kinetics dataset:

 [Google Drive url](https://drive.google.com/drive/folders/1u_l-yvhS0shpW6e0tCiqPE7Bd1qQZKdD)
 
2, P3D-199 trianed on Kinetics Optical Flow (TVL1):

 [Google Drive url](https://drive.google.com/drive/folders/1u_l-yvhS0shpW6e0tCiqPE7Bd1qQZKdD)

 
### Prepare Dataset LungBline
First, download the dataset DICOM "Centre 1 Tours" from ??? into the "Dataset" folder.

Next run scripts in the folder "DatasetTraitement" to create dataset LungBline 
dataset: LungBine (video: folder - "LungBline", list: folder - lungblineTrainTestlist)
and extract image frames from videos (folder - Data);
```
python DatasetPrepare.py
```

### Run Code
1, For Training from scratch
```
python main.py /path/data/ LungBline (if entre "python main.py /path/data/ ", UCF101 dataset is used by default)
```
2, For Fine-tuning
```
python main.py /path/data/ --pretrained LungBline
```
3, For Evaluate model
```
python main.py /path/data/ --resume=checkpoint.pth.tar --evaluate LungBline
```
4, For testing model
```
python main.py /path/data/ --test LungBline
```

### Experiment Result From Us
Dataset | Accuracy
---|---|
LungBline | ?
UCF-101 | 81.6%

Reference:

 [1][Learning Spatio-Temporal Representation with Pseudo-3D Residual,ICCV2017](http://openaccess.thecvf.com/content_iccv_2017/html/Qiu_Learning_Spatio-Temporal_Representation_ICCV_2017_paper.html)
