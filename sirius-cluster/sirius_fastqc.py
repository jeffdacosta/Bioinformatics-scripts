#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run fastQC on a fastq file.')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='infile', required=True, help='Name of input fastq file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='8', help='Memory in Gb [8]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='1:00:00', help='Walltime in hours:mintues:seconds [1:00:00]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')

args = parser.parse_args()

if args.i.endswith('.fastq'):
    base = args.i.strip('.fastq')
elif args.i.endswith('.fastq.gz'):
    base = args.i.strip('.fastq.gz')
elif args.i.endswith('.fq'):
    base = args.i.strip('.fq')
elif args.i.endswith('.fq.gz'):
    base = args.i.strip('.fq.gz')
else:
    print('ERROR: input file does not end with fastq, fastq.gz, fq, or fq.gz\n\n')
    quit()

cwd = os.getcwd()

print('Creating pbs file to run fastQC')

pbsfile = open(base+'_fastqc.pbs','w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+base+'fastQC\n'+
              '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
              '#PBS -e '+base+'_fastqc.err\n'+
              '#PBS -o '+base+'_fastqc.out\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'fastqc '+args.i+'\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+base+'_fastqc.pbs')
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
