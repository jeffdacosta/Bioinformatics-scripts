#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run GATK CombineGVCFs.\n '+
                                 'The script collects filenames in the directory that end with vcf.gz, '+
                                 'and creates a single pbs file/job that will combine these files using GATK.')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-o', type=str, metavar='output_vcf', required=True, help='Name of output vcf file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='3:00:00', help='Walltime in hours:mintues:seconds [3:00:00]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-ref', type=str, metavar='reference_path', default='/scratch/bio4802/zebrafinch/bTaeGut1_v1.fa', help='Path to reference genome')

args = parser.parse_args()

cwd = os.getcwd()

print('Gathering vcf files...')
vcf_list = []
for file in os.listdir():
    if file.endswith('vcf.gz'):
        vcf_list.append(file)
vcf_list.sort()
print('\nFound '+str(len(vcf_list))+' vcf files:')
for i in vcf_list:
    print('\t'+i)

pbsfile = open(args.o.replace('.vcf.gz','.combine.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.o.replace('.vcf.gz','.combine')+'\n'+
              '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
              '#PBS -e '+args.o.replace('.vcf.gz','.combine.err')+'\n'+
              '#PBS -o '+args.o.replace('.vcf.gz','.combine.out')+'\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'gatk CombineGVCFs '+
              '-R '+args.ref+' '+
              '-O '+args.o+' ')
for vcf in vcf_list:
    pbsfile.write(' --variant '+vcf)
pbsfile.write('\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.o.replace('.vcf.gz','.combine.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
