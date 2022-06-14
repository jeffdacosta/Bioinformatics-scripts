#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run vcftools to filter '+
                                 'variants in a vcf file')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_vcf', required=True, help='Name of input vcf file')
requiredParam.add_argument('-o', type=str, metavar='output_vcf', required=True, help='Name of output vcf file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='6:00:00', help='Walltime in hours:mintues:seconds [6:00:00]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-mm', type=str, metavar='max_missing', default='0', help='Maximum proportion of missing samples [0]')
optionalParam.add_argument('-mac', type=str, metavar='minor_allele_count', default='2', help='Minimum minor allele count [2]')
optionalParam.add_argument('-thin', type=str, metavar='thin', default='1000', help='Minimum distance between variants for thinning [1000]')

args = parser.parse_args()

cwd = os.getcwd()

pbsfile = open(args.i.replace('.vcf.gz','.vcftools.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.i.replace('.vcf.gz','.vcftools')+'\n'+
              '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
              '#PBS -e '+args.o.replace('.vcf.gz','.vcftools.err')+'\n'+
              '#PBS -o '+args.o.replace('.vcf.gz','.vcftools.out')+'\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'vcftools '+
              '--gzvcf '+args.i+' '+
              '--max-missing '+args.mm+' '+
              '--mac '+args.mac+' '+
              '--thin '+args.thin+' '+
              '--recode --stdout | gzip -c > '+
              args.o+'\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.i.replace('.vcf.gz','.vcftools.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
