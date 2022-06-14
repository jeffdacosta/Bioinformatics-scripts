#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run bwa mem to map paired reads to a reference genome.')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-s', type=str, metavar='sample', required=True, help='Sample name')
requiredParam.add_argument('-r1', type=str, metavar='R1_fastq', required=True, help='Name of input R1 fastq file')
requiredParam.add_argument('-r2', type=str, metavar='R2_fastq', required=True, help='Name of input R2 fastq file')
requiredParam.add_argument('-o', type=str, metavar='output', required=True, help='Name for output sam file')


optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='12:00:00', help='Walltime in hours:mintues:seconds [12:00:00]')
optionalParam.add_argument('-n', type=int, metavar='nodes', default=3, help='Number of nodes [3]')
optionalParam.add_argument('-ppn', type=int, metavar='processors_per_node', default=4, help='Number of processors per node [4]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-ref', type=str, metavar='reference_path', default='/scratch/bio4802/zebrafinch/bTaeGut1_v1', help='Path to reference genome')

args = parser.parse_args()

cwd = os.getcwd()

print('Creating pbs file to run bwa mem')

if not args.o.endswith('.sam'):
    print('ERROR: output file name must end with .sam')
    quit()

pbsfile = open(args.s+'_bwa.pbs','w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.s+'_bwa\n'+
              '#PBS -l pmem='+args.m+'gb,nodes='+str(args.n)+':ppn='+str(args.ppn)+',walltime='+args.w+'\n'+
              '#PBS -e '+args.s+'_bwa.err\n'+
              '#PBS -o '+args.s+'_bwa.out\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'bwa mem -t '+str(args.n*args.ppn)+
              ' '+args.ref+
              ' '+args.r1+
              ' '+args.r2+
              ' > '+args.o+'\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.s+'_bwa.pbs')
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
