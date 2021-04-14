# BLine_Tagging
 P3D + pytorch + dataset : LungBline 
 

## Pseudo-3D Residual Networks

This repo implements the network structure of P3D[1] with PyTorch, pre-trained model weights are converted from caffemodel, which is supported from the [author's repo -1](https://github.com/ZhaofanQiu/pseudo-3d-residual-networks) and [author's repo -2](https://github.com/naviocean/pseudo-3d-pytorch)


### Requirements:

- pytorch
- numpy
- ffmpeg (for extract image frames from videos)

### Datasets and Pretrained weights

Les liens suivants comprennent l'ensemble de données d'origine, l'ensemble de données prétraitées, le modèle entraîné et les résultats d'apprentissage. 
(Le nombre 3 ou 4 de sous-titre est le nombre de catégories dans un ensemble de données)

1, LungBline-4: (Bline0104, Bline0507, Bline0810, BlineBlanc)
 [Google Drive url](https://drive.google.com/drive/folders/1027MKcjOEUApx1eKaNhtixVQk0TkMFoY?usp=sharing)

2, UCF101-3:
 [Google Drive url](https://drive.google.com/drive/folders/1vEjU9NnTikhCoeQK1Soocg7BbFhdpD3u?usp=sharing)

3, LungBline-3: (Bline0104, Bline0507, Bline0810)
 [Google Drive url](https://drive.google.com/drive/folders/1bp-tLGxinZkgSpSkDVb5bwXmmjW66_3i?usp=sharing)
 
 
### Prepare Dataset LungBline

First, download the dataset DICOM "Centre 1 Tours" from [M.Nicolas Ragot](https://www.univ-tours.fr/annuaire/m-nicolas-ragot) into the "Dataset" folder.

Next run scripts in the folder "DatasetTraitement" to create dataset LungBline 
dataset: LungBine (video: folder - "LungBline", list: folder - lungblineTrainTestlist)
and extract image frames from videos (folder - Data);
```
python DatasetPrepare.py
```


### Run Code
1, For Training from scratch
```
python main.py /path/data --data-set=LungBline
```

2, For Evaluate model
```
python main.py /path/data --data-set=LungBline --resume=checkpoint.pth.tar --evaluate 
```

3, For testing model
```
python main.py /path/data --data-set=LungBline --test 
```


### Experiment Result From Us
Dataset | Accuracy | Loss
---|---|---|
LungBline | 54.930 | 1.053
LungBline(3) | 51.429 | 1.533
UCF-101(3) | 54.167 | 1.300


### Reference:

 [1][Learning Spatio-Temporal Representation with Pseudo-3D Residual,ICCV2017](http://openaccess.thecvf.com/content_iccv_2017/html/Qiu_Learning_Spatio-Temporal_Representation_ICCV_2017_paper.html)
