#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run GATK VariantFiltration '+
                                 'using the starting set of multiple expressions in GATK best practices.')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_vcf', required=True, help='Name of input vcf file')
requiredParam.add_argument('-o', type=str, metavar='output_vcf', required=True, help='Name of output vcf file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='6:00:00', help='Walltime in hours:mintues:seconds [6:00:00]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-ref', type=str, metavar='reference_path', default='/scratch/bio4802/zebrafinch/bTaeGut1_v1.fa', help='Path to reference genome [/scratch/bio4802/zebrafinch/bTaeGut1_v1.fa]')

args = parser.parse_args()

cwd = os.getcwd()
    
pbsfile = open(args.i.replace('.vcf.gz','.filter.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.i.replace('.vcf.gz','.filter')+'\n'+
              '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
              '#PBS -e '+args.o.replace('.vcf.gz','.filter.err')+'\n'+
              '#PBS -o '+args.o.replace('.vcf.gz','.filter.out')+'\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n')

pbsfile.write('gatk VariantFiltration '+
              '-R '+args.ref+' '+
              '-V '+args.i+' '+
              '-O '+args.o+' '+
              '-filter "QD < 2.0" --filter-name "QD2" '+
              '-filter "QUAL < 30.0" --filter-name "QUAL30" '+
              '-filter "SOR > 3.0" --filter-name "SOR3" '+
              '-filter "FS > 60.0" --filter-name "FS60" '+
              '-filter "MQ < 40.0" --filter-name "MQ40" '+
              '-filter "MQRankSum < -12.5" --filter-name "MQRankSum-12.5" '+
              '-filter "ReadPosRankSum < -8.0" --filter-name "ReadPosRankSum-8"\n\n')

pbsfile.write('\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.i.replace('.vcf.gz','.filter.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')
