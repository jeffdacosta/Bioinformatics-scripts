#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run samtools to convert and sort a sam file')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_sam', required=True, help='Name of input sam file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='10', help='Memory in Gb [10]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='6:00:00', help='Walltime in hours:mintues:seconds [6:00:00]')
optionalParam.add_argument('-t', type=int, metavar='threads', default=4, help='Number of threads [4]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')

args = parser.parse_args()

cwd = os.getcwd()

print('Creating pbs file to run samtools')

if not args.i.endswith('.sam'):
    print('ERROR: input file name does not end with .sam')
    quit()

pbsfile = open(args.i.replace('.sam','_samtools.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.i.replace('.sam','_samtools')+'\n'+
              '#PBS -l pmem='+args.m+'gb,nodes=1:ppn='+str(args.t)+',walltime='+args.w+'\n'+
              '#PBS -e '+args.i.replace('.sam','_samtools.err')+'\n'+
              '#PBS -o '+args.i.replace('.sam','_samtools.out')+'\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'samtools view -@ '+str(args.t)+' -bS '+args.i+' > '+args.i.replace('.sam','.bam')+'\n'+
              'samtools sort -@ '+str(args.t)+' '+args.i.replace('.sam','.bam')+' -o '+args.i.replace('.sam','_sort.bam')+'\n'+
              'samtools index '+args.i.replace('.sam','_sort.bam')+'\n'+
              'samtools flagstat '+args.i.replace('.sam','_sort.bam')+' > '+args.i.replace('.sam','_sort.flagstat')+'\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.i.replace('.sam','_samtools.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')

