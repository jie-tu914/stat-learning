# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 16:13:24 2016

@author: lifu
"""

from liflib2.dl import SoftmaxNN
from liflib2.dl import DataSet
import liflib2
import numpy as np
import argparse
import timeit
import matplotlib.pyplot as plt

if __name__ == '__main__':
    prog_name = 'Softmax Neural Network Demo'
    description = 'This is a demo program for SoftmaxNN in liflib.dl.'
    
    ap = argparse.ArgumentParser(description = description, prog = prog_name)
         
    ap.add_argument('-i', '--input', dest = 'dataset', action = 'store', 
                    default = 'dataset.dat', 
                    help = 'standard dataset file generated by liflib utility')
    ap.add_argument('-t', '--tol', action = 'store', dest = 'tol', 
                    type = float, default = 1e-5,
                    help = 'tolerance for testing convergence [default:1e-5]')
    ap.add_argument('-b', '--batch', action = 'store', dest = 'batch_size',
                    type = int, default = 50,
                    help = 'batch size when doing mini-batch gradient descent [default:50]') 
    ap.add_argument('-r', '--random', action = 'store', dest = 'random', 
                    type = bool, default = True,
                    help = 'whether randomly selecting training samples [default:True]')                                
    ap.add_argument('-m', '--maxiters', action = 'store', type = int,
                    dest = 'max_iters', default = None,
                    help = 'output test result to specific path [default:None]')     
    ap.add_argument('-s', '--step', action = 'store', type = float,
                    dest = 'step', default = 1.0,
                    help = 'step size of sgd [default:1.0]')
    ap.add_argument('-a', '--anneal', action = 'store', dest = 'anneal',
                    type = int, default = 5000,
                    help = 'decrease step size every period of time [default:5000]') 
    ap.add_argument('-d', '--display', action = 'store', dest = 'display',
                    type = int, default = 100,
                    help = 'display information every period of time [default:100]') 
    ap.add_argument('-v', '--save', action = 'store', dest = 'save',
                    type = int, default = 10000,
                    help = 'save progress to cache files every period of time [default:10000]') 
    ap.add_argument('-l', '--layer', action = 'append', dest = 'layer',
                    type = int,
                    help = 'add one hidden layer with supplied size') 
    ap.add_argument('-p', '--plot', action = 'store_true', dest = 'plot',
                    help = 'plot cost function') 
    args = ap.parse_args()

    dataset = DataSet.load(args.dataset) 
    print 'Data loaded!\n(n_samples = %d, n_features = %d, n_label_classes = %d)' % (dataset.n_samples, 
                                                                                  dataset.n_features, 
                                                                                  dataset.n_label_classes)
    
    layers = [dataset.n_features]
    if args.layer:
        for h in args.layer:
            layers.append(h)
    else:
        layers.append(max(dataset.n_features, dataset.n_label_classes))
    layers.append(dataset.n_label_classes)
    nn = SoftmaxNN(tuple(layers))    
    print 'A %d-layer neural network with layer size %s has been constructed.' % (nn.n_layers, nn.layer_size)
    #liflib2.gradcheck_naive(lambda x: nn.gd_wrapper(x, dataset, 10, True), np.random.randn(nn.get_parameter_count()), verbose = False)
    
    gd_opt={'batch_size': args.batch_size, 
                        'randomized':args.random}
     
    plt.axis([0, 500, 0, 5])              
    plt.ion() 
    plt.show()
    axis = [0, 100], [0, 100]
    old_cost = None
    min_cost = float('inf')
    def callback(e):
        if e.it % args.save == 0:
            liflib2.save_params(e.it, e.x)
        if e.it % args.display == 0:
            print 'Iterateion %d: cost = %g' % (e.it, e.cost)
            if args.plot:
                global old_cost, min_cost
                if old_cost:
                    while e.it * 1.2 >= plt.xlim()[1]:
                        plt.xlim(xmax = plt.xlim()[1] * 1.2)
                    while e.cost * 1.2 >= plt.ylim()[1]:
                        plt.ylim(ymax = plt.ylim()[1] * 1.2)
                    plt.plot([e.it - args.display, e.it], 
                             [old_cost, e.cost], 'r-')
                    if e.cost < min_cost:
                        plt.plot(e.it, e.cost, 'b.')
                        min_cost = e.cost
                    
                    plt.title('cost: %g, min: %g' % (e.cost, min_cost))
                    plt.draw()
                    plt.pause(0.1)
                old_cost = e.cost
        
    f_min_opt = {'max_iters': args.max_iters,
                     'tol': args.tol, 
                     'step_size': args.step, 
                     'anneal_every': args.anneal,
                     'use_save': True,
                     'max_iters': args.max_iters,
                     'callback': callback}
    try:
        t1 = timeit.time.time()
        nn.fit(dataset, gd_wrapper_options = gd_opt, f_min_options = f_min_opt)
    except KeyboardInterrupt:
        print 'Terminated by key interrupt'
    finally:
        t2 = timeit.time.time()        
        print 'Training process last for %g seconds in total' % (t2 - t1)
    
    if nn.fitted:
        n_correct = 0
        for i in xrange(dataset.n_training_samples):
            features, label = dataset.get_training_sample()
            if np.argmax(nn.predict(features)) == label:
                n_correct += 1
                
        print 'For training set: total: %d, correct: %d, accuracy = %g%%' % (dataset.n_training_samples, n_correct, n_correct * 100.0 / dataset.n_training_samples)
        
        n_correct = 0
        
        for i in xrange(dataset.n_test_samples):
            features, label = dataset.get_test_sample()
            if np.argmax(nn.predict(features)) == label:
                n_correct += 1
                
        print 'For test set: total: %d, correct: %d, accuracy = %g%%' % (dataset.n_test_samples, n_correct, n_correct * 100.0 / dataset.n_test_samples)
