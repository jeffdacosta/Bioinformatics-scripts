#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run AdapterRemoval on paired fastq files.')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-r1', type=str, metavar='R1_fastq', required=True, help='Name of input R1 fastq file')
requiredParam.add_argument('-r2', type=str, metavar='R2_fastq', required=True, help='Name of input R2 fastq file')
requiredParam.add_argument('-s', type=str, metavar='sample', required=True, help='Sample name')


optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='8', help='Memory in Gb [8]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='1:00:00', help='Walltime in hours:mintues:seconds [1:00:00]')
optionalParam.add_argument('-t', type=int, metavar='threads', default=12, help='Number of threads [12]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')

args = parser.parse_args()

cwd = os.getcwd()

print('Creating pbs file to run AdapterRemoval')

if args.t % 4 == 0:
    nodes = '4'
    ppn = str(int(args.t/4))
elif args.t % 3 == 0:
    nodes = '3'
    ppn = str(int(args.t/3))
elif args.t % 2 == 0:
    nodes = '2'
    ppn = str(int(args.t/2))
else:
    print('ERROR: number of threads not divisible by 4, 3, or 2')
    quit()

pbsfile = open(args.s+'_AR.pbs','w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.s+'_AR\n'+
              '#PBS -l pmem='+args.m+'gb,nodes='+nodes+':ppn='+ppn+',walltime='+args.w+'\n'+
              '#PBS -e '+args.s+'_AR.err\n'+
              '#PBS -o '+args.s+'_AR.out\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'AdapterRemoval --threads '+str(args.t)+
              ' --adapter-list /scratch/bio4802/nextera_adapters.txt --gzip'+
              ' --file1 '+args.r1+
              ' --file2 '+args.r2+
              ' --basename '+args.s+'_trimmed'+
              ' --output1 '+args.s+'_AR_R1.fastq.gz'+
              ' --output2 '+args.s+'_AR_R2.fastq.gz\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.s+'_AR.pbs')
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
