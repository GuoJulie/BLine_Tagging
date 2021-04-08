from __future__ import print_function
import argparse
from train import *
from test import *


parser = argparse.ArgumentParser(description='PyTorch Pseudo-3D fine-tuning')
parser.add_argument('data', metavar='DIR', help='path to dataset')
parser.add_argument('--data-set', default='UCF101', const='UCF101', nargs='?', choices=['UCF101', 'LungBline'])
parser.add_argument('--workers', default=4, type=int, metavar='N', help='number of data loading workers (default: 4)')
parser.add_argument('--early-stop', default=10, type=int, metavar='N', help='number of early stopping')
parser.add_argument('--epochs', default=10, type=int, metavar='N', help='number of total epochs to run')
parser.add_argument('--start-epoch', default=0, type=int, metavar='N', help='manual epoch number (useful on restarts)')
parser.add_argument('-b', '--batch-size', default=4, type=int, metavar='N', help='mini-batch size (default: 256)')
parser.add_argument('--lr', '--learning-rate', default=1e-4, type=float, metavar='LR', help='initial learning rate')
parser.add_argument('--momentum', default=0.9, type=float, metavar='M', help='momentum')
parser.add_argument('--dropout', default=0.5, type=float, metavar='M', help='dropout')
parser.add_argument('--weight-decay', default=1e-4, type=float, metavar='W', help='weight decay')
parser.add_argument('--print-freq', default=1, type=int, metavar='N', help='print frequency')
parser.add_argument('--resume', default='', type=str, metavar='PATH', help='path to latest checkpoint')
parser.add_argument('--evaluate', dest='evaluate', action='store_true', help='evaluate model on validation set')
parser.add_argument('--test', dest='test', action='store_true', help='evaluate model on test set')
parser.add_argument('--random', dest='random', action='store_true', help='random pick image')
parser.add_argument('--pretrained', dest='pretrained', action='store_true', help='use pre-trained model')
parser.add_argument('--model-type', default='P3D', choices=['P3D', 'C3D', 'I3D'], help='which model to run the code')
parser.add_argument('--num-frames', default=16, type=int, metavar='N', help='number frames per clip')
parser.add_argument('--log-visualize', default='./runs', type=str, metavar='PATH', help='tensorboard log')



def main():
    '''
    Read the parameters entered by the command line in terminal,
    determine the selected data set, the selected network structure and the defined learning parameters,
    then perform training or test operations.
    '''

    # global num_classes

    args = parser.parse_args()
    args = vars(args)

    # python main.py E:/S9_PRD/RefTest/P3D_Tensorflow/P3D_Test/data
    if args['data_set'] == 'UCF101': # python main.py path/data
        print('UCF101 data set')
        name_list = 'ucfTrainTestlist'
        num_classes = 3
    else:
        # python main.py E:/S9_PRD/RefTest/P3D_Tensorflow/P3D_Test/data --data-set=LungBline
        print("LungBline data set")
        num_classes = 4
        name_list = 'lungblineTrainTestlist'

    print("num_classes: ", num_classes)

    if args['test']:
        Testing(name_list=name_list, num_classes=num_classes, modality='RGB', **args)
    else:
        Training(name_list=name_list, num_classes=num_classes, modality='RGB', **args)


if __name__ == '__main__':
    main()

