from __future__ import print_function

import os
import os.path
import shutil
import time

import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data as data

from Dataset import MyDataset
from logger import Logger
from lr_scheduler import CyclicLR
from meter import AverageMeter
from somemodels import p3d_model
from somemodels.p3d_model import *
from somemodels.C3D import C3D
from somemodels.i3dpt import I3D
# from video_transforms import *
from transforms import *
from main import *
from utils import check_gpu, transfer_model, accuracy, get_learning_rate
from visualize import Visualizer
import matplotlib.pyplot as plt


class Training(object):

    def __init__(self, name_list, num_classes, modality='RGB', **kwargs):
        self.__dict__.update(kwargs)
        self.num_classes = num_classes
        self.modality = modality
        self.name_list = name_list
        # set accuracy avg = 0
        self.count_early_stop = 0
        # Set best precision = 0
        self.best_prec1 = 0
        # init start epoch = 0
        self.start_epoch = 0

        self.Train_Accuracy_list = []
        self.Train_Loss_list = []
        self.Val_Accuracy_list = []
        self.Val_Loss_list = []

        if self.log_visualize != '':
            self.visualizer = Visualizer(logdir=self.log_visualize)

        self.checkDataFolder()

        self.loading_model()

        self.train_loader, self.val_loader = self.loading_data()

        # run
        self.processing()
        if self.random:
            print('random pick images')

    def check_early_stop(self, accuracy, logger, start_time):
        if self.best_prec1 <= accuracy:
            self.count_early_stop = 0
        else:
            self.count_early_stop += 1

        if self.count_early_stop > self.early_stop:
            print('Early stop')
            end_time = time.time()
            print("--- Total training time %s seconds ---" %
                  (end_time - start_time))
            logger.info("--- Total training time %s seconds ---" %
                        (end_time - start_time))
            exit()

    def checkDataFolder(self):
        '''
        Create a folder to store the trained model, generated log, image of learning curve etc ,.
        :return:
        '''
        try:
            os.stat('./' + self.model_type + '_' + self.data_set)
        except:
            os.mkdir('./' + self.model_type + '_' + self.data_set)
        self.data_folder = './' + self.model_type + '_' + self.data_set

    # Loading P3D model
    def loading_model(self):

        print('Loading %s model' % (self.model_type))

        if self.model_type == 'C3D':
            self.model = C3D()
            if self.pretrained:
                self.model.load_state_dict(torch.load('c3d.pickle'))
        elif self.model_type == 'I3D':
            if self.pretrained:
                self.model = I3D(num_classes=400, modality='rgb')
                self.model.load_state_dict(
                    torch.load('kinetics_i3d_model_rgb.pth'))
            else:
                self.model = I3D(num_classes=self.num_classes, modality='rgb')
        else:
            if self.pretrained:
                print("=> using pre-trained model")
                self.model = P3D199(
                    pretrained=True, num_classes=400, dropout=self.dropout)

            else:
                print("=> creating model P3D")
                self.model = P3D199(
                    pretrained=False, num_classes=400, dropout=self.dropout)
        # Transfer classes
        self.model = transfer_model(model=self.model, model_type=self.model_type, num_classes=self.num_classes)

        # Check gpu and run parallel
        # if check_gpu() > 0:
        #     self.model = torch.nn.DataParallel(self.model)

        # define loss function (criterion) and optimizer
        self.criterion = nn.CrossEntropyLoss()

        # if check_gpu() > 0:
        #     self.criterion = nn.CrossEntropyLoss()

        params = self.model.parameters()
        if self.model_type == 'P3D':
            params = p3d_model.get_optim_policies( model=self.model, modality=self.modality, enable_pbn=True)

        self.optimizer = optim.SGD(params=params, lr=self.lr, momentum=self.momentum, weight_decay=self.weight_decay)

        # self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer=self.optimizer, mode='min', patience=10, verbose=True)

        # optionally resume from a checkpoint
        if self.resume:
            if os.path.isfile(self.resume):
                print("=> loading checkpoint '{}'".format(self.resume))
                checkpoint = torch.load(self.resume)
                self.start_epoch = checkpoint['epoch']
                self.best_prec1 = checkpoint['best_prec1']
                self.model.load_state_dict(checkpoint['state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer'])
                print("=> loaded checkpoint '{}' (epoch {})".format(
                    self.evaluate, checkpoint['epoch']))
            else:
                print("=> no checkpoint found at '{}'".format(self.resume))

        if self.evaluate:
            file_model_best = os.path.join(
                self.data_folder, 'model_best.pth.tar')
            if os.path.isfile(file_model_best):
                print("=> loading checkpoint '{}'".format('model_best.pth.tar'))
                checkpoint = torch.load(file_model_best)
                self.start_epoch = checkpoint['epoch']
                self.best_prec1 = checkpoint['best_prec1']
                self.model.load_state_dict(checkpoint['state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer'])
                print("=> loaded checkpoint '{}' (epoch {})".format(
                    self.evaluate, checkpoint['epoch']))
            else:
                print("=> no checkpoint found at '{}'".format(self.resume))

        cudnn.benchmark = True

    # Loading data
    def loading_data(self):
        random = True if self.random else False
        size = 160
        # size = 300
        if self.model_type == 'C3D':
            size = 112
        if self.model_type == 'I3D':
            size = 224

        normalize = Normalize(mean=[0.485, 0.456, 0.406], std=[
            0.229, 0.224, 0.225])
        train_transformations = Compose([
            RandomSizedCrop(size),
            RandomHorizontalFlip(),
            # Resize((size, size)),
            # ColorJitter(
            #     brightness=0.4,
            #     contrast=0.4,
            #     saturation=0.4,
            # ),
            ToTensor(),
            normalize])

        val_transformations = Compose([
            # Resize((182, 242)),
            Resize(256),
            CenterCrop(size),
            ToTensor(),
            normalize
        ])

        self.train_dataset = MyDataset(
            self.data,
            data_folder="train",
            name_list=self.name_list,
            version="1",
            transform=train_transformations,
            num_frames=self.num_frames,
            random=random
        )

        val_dataset = MyDataset(
            self.data,
            data_folder="validation",
            name_list=self.name_list,
            version="1",
            transform=val_transformations,
            num_frames=self.num_frames,
            random=random
        )

        # Combines a dataset and a sampler, and provides an iterable over the given dataset.
        train_loader = data.DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.workers,
            pin_memory=True)

        val_loader = data.DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.workers,
            pin_memory=False)

        return (train_loader, val_loader)

    # run (Start learning and validating, then export the results to "train.log" and show the learning curve)
    def processing(self):
        log_file = os.path.join(self.data_folder, 'train.log')

        logger = Logger('train', log_file)

        iters = len(self.train_loader)
        step_size = iters * 2
        self.scheduler = CyclicLR(optimizer=self.optimizer, step_size=step_size, base_lr=self.lr)

        if self.evaluate:
            self.validate(logger)
            return

        self.iter_per_epoch = len(self.train_loader)
        logger.info('Iterations per epoch: {0}'.format(self.iter_per_epoch))
        print('Iterations per epoch: {0}'.format(self.iter_per_epoch))

        start_time = time.time()

        for epoch in range(self.start_epoch, self.epochs):
            # self.adjust_learning_rate(epoch)

            # train for one epoch
            train_losses, train_acc = self.train(logger, epoch)
            print("*********** train_acc.avg: ", train_acc.avg)
            print("*********** train_losses.avg: ", train_losses.avg)

            # evaluate on validation set
            with torch.no_grad():
                val_losses, val_acc = self.validate(logger)
                print("*********** val_acc.avg: ", val_acc.avg)
                print("*********** val_losses.avg: ", val_losses.avg)

            # self.scheduler.step(val_losses.avg)
            # log visualize
            info_acc = {'train_acc': train_acc.avg, 'val_acc': val_acc.avg}
            info_loss = {'train_loss': train_losses.avg, 'val_loss': val_losses.avg}
            self.visualizer.write_summary(info_acc, info_loss, epoch + 1)

            # print("+++++++iter_per_epoch: ",self.iter_per_epoch)
            # print("+++++++len(self.train_dataset): ",len(self.train_dataset))
            self.Train_Accuracy_list.append(train_acc.avg)
            self.Train_Loss_list.append(train_losses.avg)
            self.Val_Accuracy_list.append(val_acc.avg)
            self.Val_Loss_list.append(val_losses.avg)

            self.visualizer.write_histogram(model=self.model, step=epoch + 1)

            # remember best Accuracy and save checkpoint
            is_best = val_acc.avg > self.best_prec1
            self.best_prec1 = max(val_acc.avg, self.best_prec1)
            print("Best Accuracy: ", self.best_prec1)
            self.save_checkpoint({
                'epoch': epoch + 1,
                'state_dict': self.model.state_dict(),
                'best_prec1': self.best_prec1,
                'optimizer': self.optimizer.state_dict(),
            }, is_best)

            self.check_early_stop(val_acc.avg, logger, start_time)

        end_time = time.time()
        print("--- Total training time %s seconds ---" %
              (end_time - start_time))
        logger.info("--- Total training time %s seconds ---" %
                    (end_time - start_time))
        self.visualizer.writer_close()

        self.courbe()

    # Training (Train the model, measure the precision and record the loss, print the results on the command line of the terminal)
    def train(self, logger, epoch):
        batch_time = AverageMeter()
        data_time = AverageMeter()
        losses = AverageMeter()
        acc = AverageMeter()
        top1 = AverageMeter()
        top5 = AverageMeter()

        rate = get_learning_rate(self.optimizer)[0]
        # switch to train mode
        self.model.train()

        end = time.time()
        for i, (images, target) in enumerate(self.train_loader):
            # adjust learning rate scheduler step
            self.scheduler.batch_step()

            # measure data loading time
            data_time.update(time.time() - end)
            # if check_gpu() > 0:
            #     images = images
            #     target = target
            image_var = torch.autograd.Variable(images)
            label_var = torch.autograd.Variable(target)

            self.optimizer.zero_grad()

            # compute y_pred
            y_pred = self.model(image_var)
            # print("-----y_pred.shape:-----", y_pred.shape)
            if self.model_type == 'I3D':
                y_pred = y_pred[0]

            loss = self.criterion(y_pred, label_var)
            # measure accuracy and record loss
            if self.num_classes<=5:
                topkmax = self.num_classes
            else:
                topkmax = 5
            prec1, prec5 = accuracy(y_pred.data, target, topk=(1, topkmax))
            losses.update(loss.item(), images.size(0))
            acc.update(prec1.item(), images.size(0))
            top1.update(prec1.item(), images.size(0))
            top5.update(prec5.item(), images.size(0))
            # compute gradient and do SGD step

            loss.backward()
            self.optimizer.step()

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % self.print_freq == 0:
                print('Epoch: [{0}/{1}][{2}/{3}]\t'
                      'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                      'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                      'Lr {rate:.5f}\t'
                      'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                      'Prec@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                      'Prec@4 {top5.val:.3f} ({top5.avg:.3f})'.format(epoch, self.epochs, i, len(self.train_loader),
                                                                      batch_time=batch_time, data_time=data_time,
                                                                      rate=rate,
                                                                      loss=losses, top1=top1, top5=top5))

        logger.info('Epoch: [{0}/{1}]\t'
                    'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                    'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                    'Lr {rate:.5f}\t'
                    'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                    'Prec@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                    'Prec@4 {top5.val:.3f} ({top5.avg:.3f})'.format(epoch, self.epochs, batch_time=batch_time,
                                                                    data_time=data_time, rate=rate, loss=losses,
                                                                    top1=top1,
                                                                    top5=top5))
        return losses, acc

    # Validation
    def validate(self, logger):
        batch_time = AverageMeter()
        losses = AverageMeter()
        acc = AverageMeter()
        top1 = AverageMeter()
        top5 = AverageMeter()
        # switch to evaluate mode
        self.model.eval()

        end = time.time()
        for i, (images, labels) in enumerate(self.val_loader):
            # if check_gpu() > 0:
            #     images = images
            #     labels = labels

            image_var = torch.autograd.Variable(images)
            label_var = torch.autograd.Variable(labels)

            # compute y_pred
            y_pred = self.model(image_var)
            if self.model_type == 'I3D':
                y_pred = y_pred[0]

            loss = self.criterion(y_pred, label_var)

            # measure accuracy and record loss
            if self.num_classes<=5:
                topkmax = self.num_classes
            else:
                topkmax = 5
            prec1, prec5 = accuracy(y_pred.data, labels, topk=(1, topkmax))
            losses.update(loss.item(), images.size(0))
            acc.update(prec1.item(), images.size(0))
            top1.update(prec1.item(), images.size(0))
            top5.update(prec5.item(), images.size(0))
            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % self.print_freq == 0:
                print('TrainVal: [{0}/{1}]\t'
                      'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                      'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                      'Prec@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                      'Prec@4 {top5.val:.3f} ({top5.avg:.3f})'.format(
                    i, len(self.val_loader), batch_time=batch_time, loss=losses, top1=top1, top5=top5))

        print(
            ' * Accuracy {acc.avg:.3f}  Loss {loss.avg:.3f}'.format(acc=acc, loss=losses))
        logger.info(
            ' * Accuracy {acc.avg:.3f}  Loss {loss.avg:.3f}'.format(acc=acc, loss=losses))

        return losses, acc

    # save checkpoint to file
    def save_checkpoint(self, state, is_best):
        checkpoint = os.path.join(self.data_folder, 'checkpoint.pth.tar')
        torch.save(state, checkpoint)
        model_best = os.path.join(self.data_folder, 'model_best.pth.tar')
        if is_best:
            shutil.copyfile(checkpoint, model_best)

    # adjust learning rate for each epoch
    def adjust_learning_rate(self, epoch):
        """Sets the learning rate to the initial LR decayed by 10 every 3K iterations"""
        iters = len(self.train_loader)
        num_epochs = 3000 // iters
        decay = 0.1 ** (epoch // num_epochs)
        lr = self.lr * decay
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr * param_group['lr_mult']
            param_group['weight_decay'] = decay * param_group['decay_mult']

    # courbe d'apprentissage(acc et loss)
    def courbe(self):
        x_epochs = range(0, self.epochs)
        y_train_acc = self.Train_Accuracy_list
        y_val_acc = self.Val_Accuracy_list
        y_train_loss = self.Train_Loss_list
        y_val_loss = self.Val_Loss_list
        print("x_epochs: ", x_epochs)
        print("y_train_acc: ", y_train_acc)
        print("y_val_acc: ", y_val_acc)
        print("y_train_loss: ", y_train_loss)
        print("y_val_loss: ", y_val_loss)

        # plt.title('Accuracy and Loss')
        # plt.plot(x_epochs, y_train_acc, 'red', label='Training acc')
        # plt.plot(x_epochs, y_val_acc, 'orange', label='Validation acc')
        # plt.plot(x_epochs, y_train_loss, 'blue', label='Training loss')
        # plt.plot(x_epochs, y_val_loss, 'green', label='Validation loss')
        # plt.legend()
        #
        # # for xy in zip(x_epochs, y_val_acc):
        # #     plt.annotate("(%s,%s)" % xy, xy=xy, xytext=(-20, 10), textcoords='offset points')
        #
        # plt.xlim(0, 9)
        # plt.ylim(0, 100)

        plt.subplot(2, 1, 1)
        plt.title('Accuracy and Loss')
        plt.plot(x_epochs, y_train_acc, 'red', label='Training acc')
        plt.plot(x_epochs, y_val_acc, 'orange', label='Validation acc')
        plt.ylabel('Accuracy')
        plt.xlim(0, 9)
        # plt.ylim(0, 100)
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(x_epochs, y_train_loss, 'blue', label='Training loss')
        plt.plot(x_epochs, y_val_loss, 'green', label='Validation loss')
        plt.ylabel('Loss')
        plt.xlim(0, 9)
        # plt.ylim(0, 100)
        plt.legend()

        plt.xlabel('Epochs')

        plt.savefig("accuracy_loss.jpg")
        plt.show()

