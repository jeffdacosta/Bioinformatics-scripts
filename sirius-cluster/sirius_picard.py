#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run picard to remove PCR duplicates')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_sorted_bam', required=True, help='Name of input (sorted) bam file')
requiredParam.add_argument('-s', type=str, metavar='sample', required=True, help='Sample name')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='6:00:00', help='Walltime in hours:mintues:seconds [4:00:00]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')

args = parser.parse_args()

cwd = os.getcwd()

print('Creating pbs file to run picard')

if not args.i.endswith('.bam'):
    print('ERROR: input file name does not end with .bam')
    quit()

pbsfile = open(args.i.replace('.bam','_picard.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -N '+args.i.replace('.bam','_picard')+'\n'+
              '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
              '#PBS -e '+args.i.replace('.bam','_picard.err')+'\n'+
              '#PBS -o '+args.i.replace('.bam','_picard.out')+'\n')

if args.e != '':
    pbsfile.write('#PBS -m abe -M '+args.e+'\n')

pbsfile.write('\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n'+
              'java -Xmx'+str(int(args.m)-2)+'G -jar /usr/public/dacosta/picard_bin//picard-2.8.2.jar MarkDuplicates '+
              'I='+args.i+' '+
              'O='+args.i.replace('.bam','_dedup.bam')+' '+
              'M='+args.i.replace('.bam','_dedup.stats')+' '+
              'REMOVE_DUPLICATES=true\n'+
              'java -Xmx10G -jar /usr/public/dacosta/picard_bin//picard-2.8.2.jar AddOrReplaceReadGroups '+
              'I='+args.i.replace('.bam','_dedup.bam')+' '+
              'O='+args.i.replace('.bam','_dedupF.bam')+' '+
              'SORT_ORDER=coordinate CREATE_INDEX=True VALIDATION_STRINGENCY=LENIENT '+
              'RGLB='+args.s+'_AR RGPL=illumina RGPU=AAAAAA RGSM='+args.s+'_AR\n\n\n')
pbsfile.close()

print('\nSubmitting pbs file')
command = ('qsub '+args.i.replace('.bam','_picard.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')

