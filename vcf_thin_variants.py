#!/usr/bin/env python3

import os, sys, gzip, argparse, random
from argparse import RawTextHelpFormatter

print()

parser = argparse.ArgumentParser(description=
                                 'This program "thins" the variants in a VCF file. For each scaffold,\n'+
                                 'a variant is randomly selected and then variants that are at least \n'+
                                 'X bp up/downstream from each other are extracted.\n',
                                 formatter_class=RawTextHelpFormatter)

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-i', type=str, metavar='infile', required=True, help='Name of input VCF file')
requiredParam.add_argument('-o', type=str, metavar='outfile', required=True, help='Name for output VCF file')
requiredParam.add_argument('-bp', type=int, metavar='base_pair', required=True, help='Minimum number of bp between variants')

args = parser.parse_args()

#open outfile
if args.o.endswith('vcf'):
    outfile = open(args.o,'w')
elif args.o.endswith('vcf.gz'):
    outfile = gzip.open(args.o,'wt')
else:
    print('\nERROR: output file must end with .vcf or .vcf.gz\n\n')
    quit()

#establish scaffold and position lists
scaf_data = []
positions = []

#get name of first scaffold
if args.i.endswith('vcf'):
    infile = open(args.i,'r')
elif args.i.endswith('vcf.gz'):
    infile = gzip.open(args.i,'rt')
else:
    print('\nERROR: input file must end with .vcf or .vcf.gz\n\n')
    quit()
for line in infile:
    if line[0] != '#':
        scaf = line.split()[0]
        scaf_data.append(line)
        positions.append(line.split()[1])
        break
    else:
        outfile.write(line)

#analyze file
print('Analyzing VCF file...\n')
print('Scaffold\tNum thinned variants\n')

x = True
while x:
    line = infile.readline()
    print(line)

    if not line or line.split()[0] != scaf:
        print(positions)
        targets = []
        rand = random.randint(0,len(positions)-1)
        start = positions[rand]
        print(rand)
        print(start)
        targets.append(positions[rand])
        upstream = positions[0:rand+1]
        upstream.reverse()
        downstream = positions[rand:]

        #gather upstream thinned positions
        minbp = int(start)-args.bp
        for i in upstream:
            if int(i) <= minbp:
                targets.append(i)
                minbp = int(i)-args.bp

        #gether downstreat thinned positions
        minbp = int(start)+args.bp
        for i in downstream:
            if int(i) >= minbp:
                targets.append(i)
                minbp = int(i)+args.bp

        targets.sort()
        print(targets)
        for i in scaf_data:
            if i.split()[1] in targets:
                outfile.write(i)

        print(scaf,len(targets))
        
        if line:
            scaf = line.split()[0]
            positions = []
            scaf_data = []
            scaf_data.append(line)
            positions.append(line.split()[1])

        if not line:
            print('end')
            x = False

    else:
        scaf_data.append(line)
        positions.append(line.split()[1])


print('\nFinished!!!\n\n')       
                
        

