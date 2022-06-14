#!/usr/bin/env python3

import os, sys, argparse, subprocess, gzip

print()

parser = argparse.ArgumentParser(description=
                                 'This script parses the variants in a VCF file to separate files for each chromosome/scaffold\n')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='input_vcf', required=True, help='Name of input vcf file. Must have extension .vcf or .vcf.gz (gzip)')
requiredParam.add_argument('-p', type=str, metavar='output_prefix', required=True, help='Prefix for names of output files')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='1:00:00', help='Walltime in hours:minutes:seconds')
optionalParam.add_argument('-e', type=str, metavar='email', default='', help='Email address if you want notifications []')
optionalParam.add_argument('-min', type=int, metavar='min_length', default=0, help='Minimum chromosome/scaffold length needed for processing')

args = parser.parse_args()

cwd = os.getcwd()

print('Gathering chromosome/scaffold info...')
if args.i.endswith('.vcf'):
    infile = open(args.i,'r')
elif args.i.endswith('.vcf.gz'):
    infile = gzip.open(args.i,'rt')
else:
    print('ERROR: input vcf file does not end in .vcf or .vcf.gz')
    quit()
chrom_list = []
for line in infile:
    if line.startswith('#'):
        if line.startswith('##contig'):
            chrom = line.split('=<ID=')[1].split(',')[0]
            length = line.split('length=')[1].split(',')[0]
            if int(length) >= args.min:
                chrom_list.append(chrom)
    else:
        break
infile.close()

print('\nFound '+str(len(chrom_list))+' chromosomes/scaffolds in reference used for mapping that meet length requirement')

print('\nCreating pbs files to run VCFtools to parse variants for each chromosome/scaffold:')

for chrom in chrom_list:
    print('\n'+chrom)
    pbsfile = open(args.p+'_'+chrom+'_vcftools.pbs','w')
    pbsfile.write('#!/bin/tcsh\n'+
                  '#PBS -N '+chrom+'\n'+
                  '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
                  '#PBS -e '+args.p+'_'+chrom+'_vcftools.err\n'+
                  '#PBS -o '+args.p+'_'+chrom+'_vcftools.out\n'+
                  '\nmodule load dacosta/1.0\n'+
                  'cd '+cwd+'\n\n')
    if args.i.endswith('.vcf'):
        pbsfile.write('vcftools --vcf '+args.i+
                      ' --chr '+chrom+
                      ' --recode --stdout | gzip -c > '+args.p+'_'+chrom+'.vcf.gz\n\n')
    if args.i.endswith('.vcf.gz'):
        pbsfile.write('vcftools --gzvcf '+args.i+
                      ' --chr '+chrom+
                      ' --recode --stdout | gzip -c > '+args.p+'_'+chrom+'.vcf.gz\n\n')
    pbsfile.close()

    command = ('qsub '+args.p+'_'+chrom+'_vcftools.pbs')
    p = subprocess.Popen(command, shell=True)
    sts = os.waitpid(p.pid, 0)[1]

print('\nFinished!!!\n\n')


