#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run GATK SelectVariants.\n '+
                                 'The command will retain only biallelic SNPs from an input vcf file.')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_vcf', required=True, help='Name of input vcf file')
requiredParam.add_argument('-o', type=str, metavar='output_vcf', required=True, help='Name of output vcf file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-t', type=int, metavar='threads', default=4, help='Number of threads [4]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='3:00:00', help='Walltime in hours:mintues:seconds [3:00:00]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-ref', type=str, metavar='reference_path', default='/scratch/bio4802/zebrafinch/bTaeGut1_v1.fna', help='Path to reference genome')

args = parser.parse_args()

cwd = os.getcwd()

if args.t % 4 == 0:
    if args.t > 11:
        n = str(int(args.t/3))
    else:
        n = str(int(args.t/2))
else:
    print('ERROR: number of threads must be divisible by 4')
    quit()
    
pbsfile = open(args.o.replace('.vcf.gz','.select.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.o.replace('.vcf.gz','.combine')+'\n'+
              '#PBS -l pmem='+args.m+'gb,nodes='+n+':ppn=4,walltime='+args.w+'\n'+
              '#PBS -e '+args.o.replace('.vcf.gz','.select.err')+'\n'+
              '#PBS -o '+args.o.replace('.vcf.gz','.select.out')+'\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'gatk SelectVariants '+
              '-R '+args.ref+' '+
              '-V '+args.i+' '+
              '-O '+args.o+' '+
              '--restrict-alleles-to BIALLELIC '+
              '--select-type-to-exclude INDEL '+
              '--select-type-to-exclude MIXED '+
              '--select-type-to-exclude SYMBOLIC '+
              '--exclude-non-variants\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.o.replace('.vcf.gz','.select.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
