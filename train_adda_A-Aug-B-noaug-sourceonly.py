import os
from os.path import join

from cycada.tools.train_task_net import train as train_source
from cycada.tools.test_task_net import load_and_test_net
from cycada.tools.train_adda_net import train_adda
import torch
import numpy as np



if __name__ == '__main__':
                # set random seed to 4325 
        # to reproduce the exact numbers
        np.random.seed(4325)

        ###################################
        # Set to your preferred data path #
        ###################################
        datadir = 'FY/'
        ###################################

        # Choose GPU ID
        os.environ['CUDA_VISIBLE_DEVICES'] = '0' 

        # Problem Params
        src = 'icdar2013_A_Aug_B_noaug_ds'
        tgt = 'icdar2015_A_Aug_B_noaug_ds'
        iteration = 1 #'no_cycle' 

        base_src = src.split('2')[0]

        model = 'LeNet'
        num_cls = 2

        # Output directory
        outdir = 'results/{}_to_{}/iter_{}'.format(src, tgt, iteration)
        #outdir = 'results/{}_to_{}'.format(src, tgt)

        # Optimization Params
        betas = (0.9, 0.999) # Adam default
        weight_decay = 0 # Adam default
        batch = 128

        src_lr = 1e-4
        src_num_epoch = 100
        src_datadir = join(datadir, src)
        src_net_file = join(outdir, '{}_net_{}.pth'.format(model, src)) 
        adda_num_epoch =100
        adda_lr = 1e-5
        adda_net_file = join(outdir, 'adda_{:s}_net_{:s}_{:s}.pth'
                .format(model, src, tgt))
        #######################
        # 1. Train Source Net #
        #######################
        if os.path.exists(src_net_file):
                print('Skipping source net training, exists:', src_net_file)
        else:
                print("this is num_epoch ",src_num_epoch)
                train_source(src, src_datadir, model, num_cls, 
                outdir=outdir, num_epoch=src_num_epoch, batch=batch, 
                lr=src_lr, betas=betas, weight_decay=weight_decay)


        #####################
        # 2. Train Adda Net #
        #####################
        print ()
        if os.path.exists(adda_net_file):
                print('Skipping adda training, exists:', adda_net_file)
        else:
                print("this is num_epoch ",adda_num_epoch)
                train_adda(src, tgt, model, num_cls, num_epoch=adda_num_epoch, 
                batch=batch, datadir=datadir,
                outdir=outdir, src_weights=src_net_file, 
                lr=adda_lr, betas=betas, weight_decay=weight_decay)

        ##############################
        # 3. Evalute source and adda #
        ##############################
        tgt_datadir = join(datadir, tgt)
        print()
        if src == base_src:
                print('________________')
                print('Test set:', src)
                print('________________')
                print('Evaluating {} source model: {}'.format(src, src_net_file))
                load_and_test_net(src, src_datadir, src_net_file, model, num_cls, 
                        dset='test', base_model=None)


        print('________________')
        print('Test set:', tgt)
        print('________________')
        print('Evaluating {} source model: {}'.format(src, src_net_file))
        cm = load_and_test_net(tgt, tgt_datadir, src_net_file, model, num_cls, 
                dset='test', base_model=None)

        print(cm)

        print('Evaluating {}_>{} adda model: {}'.format(src, tgt, adda_net_file))
        cm = load_and_test_net(tgt, tgt_datadir, adda_net_file, 'AddaNet', num_cls, 
                dset='test', base_model=model)
        print(cm)
