#!/usr/bin/env python3

import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script creates and submits pbs files to run GATK HaplotypeCaller.\n '+
                                 'A separate pbs file/job is created for each scaffold in the genome')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_bam', required=True, help='Name of input bam file')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-ref', type=str, metavar='reference_path', default='/scratch/bio4802/zebrafinch/bTaeGut1_v1.fa', help='Path to reference genome')
optionalParam.add_argument('-scaf', type=str, metavar='scaffold_list_path', default='/scratch/bio4802/zebrafinch/bTaeGut1_v1.fa.scaffolds', help='Path to list of scaffolds in reference genome')

args = parser.parse_args()

cwd = os.getcwd()

print('Gathering scaffold info...')
scaf_list = []
scaf_file = open(args.scaf,'r')
for line in scaf_file:
    data = line.split()
    scaf_list.append(data)
scaf_file.close()
print('Found '+str(len(scaf_list))+' scaffolds')

print('\nCreating pbs files to run GATK HaplotypeCaller on each scaffold in reference genome...\n')

for i in scaf_list:
    if float(i[2]) < 50000000:
        w = '23:00:00'
    elif float(i[2]) < 75000000:
        w = '48:00:00'
    elif float(i[2]) < 100000000:
        w = '72:00:00'
    else:
        w = '96:00:00'
        
    print('\nScaffold: '+i[0])
    pbsfile = open(args.i.replace('.bam','_'+i[0]+'.pbs'),'w')
    pbsfile.write('#!/bin/tcsh\n'+
                  '#PBS -N '+i[0]+'\n'+
                  '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+w+'\n'+
                  '#PBS -e '+args.i.replace('.bam','_'+i[0]+'.err')+'\n'+
                  '#PBS -o '+args.i.replace('.bam','_'+i[0]+'.out')+'\n')

    if args.e != '':
        pbsfile.write('#PBS -m abe -M '+args.e+'\n')

    pbsfile.write('\nmodule load dacosta/1.0\n'+
                  'cd '+cwd+'\n\n'+
                  'gatk HaplotypeCaller '+
                  '-R '+args.ref+' '+
                  '--min-pruning 1 '+
                  '--min-dangling-branch-length 1 '+
                  '--emit-ref-confidence GVCF '+
                  '-L '+i[0]+' '+
                  '-I '+args.i+' '+
                  '-O '+args.i.replace('.bam','_'+i[0]+'_raw.g.vcf.gz')+'\n\n')
    pbsfile.close()

    print('Submitting pbs file')
    command = ('qsub '+args.i.replace('.bam','_'+i[0]+'.pbs'))
    p = subprocess.Popen(command, shell=True)
    sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')

