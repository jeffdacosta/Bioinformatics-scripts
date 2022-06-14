import os, sys, random, gzip, argparse

parser = argparse.ArgumentParser(description=
                                 'This script takes as input a VCF file and converts genotype data into a NEXUS file for SNAPP. '+
                                 'It assumes that all variants are biellelic SNPs')

parser.add_argument('-i', type=str, metavar='infile', required=True, help='Name of input VCF file. Must end in .vcf or .vcf.gz')
parser.add_argument('-o', type=str, metavar='outfile', required=True, help='Name of output nexus file')
args = parser.parse_args()

print('\nGathering sample list')

sample_list = []
if args.i.endswith('.vcf'):
    infile = open(args.i,'r')
elif args.i.endswith('.vcf.gz'):
    infile = gzip.open(args.i,'rt')
else:
    print('ERROR: input file must end with .vcf or .vcf.gz')
    quit()
for line in infile:
    if line.startswith('#CHROM'):
        data = line.split()
        num_samples = len(data[9:])
        for i in range(num_samples):
            sample_list.append(data[9+i]+'_a')
            sample_list.append(data[9+i]+'_b')
        break
infile.close()

print('\nFound '+str(num_samples)+' samples')
print('Sample\t')
for sample in sample_list:
    print(sample)

print('\nGathering genotype data...')
count = 0
target = 10000
all_gens = []
if args.i.endswith('.vcf'):
    infile = open(args.i,'r')
elif args.i.endswith('.vcf.gz'):
    infile = gzip.open(args.i,'rt')
else:
    print('ERROR: input file must end with .vcf or .vcf.gz')
    quit()
for line in infile:
    if line[0] != '#':
        count += 1
        if count == target:
            print(str(count)+' variants processed')
            target += 10000
        variant_gens = []
        sampledata = line.split()[9:]
        gens = []
        for sample in sampledata:
            samplegen = sample.split(':')[0]
            gens.append(samplegen)
        for gen in gens:
            if gen == '0/0' or gen == '0|0':
                variant_gens.append('0')
                variant_gens.append('0')
            elif gen == '0':
                variant_gens.append('0')
                variant_gens.append('?')
            elif gen == '0/1' or gen == '0|1' or gen == '1/0' or gen == '1|0':
                x = random.randint(1,2)
                if x == 1:
                    variant_gens.append('0')
                    variant_gens.append('1')
                else:
                    variant_gens.append('1')
                    variant_gens.append('0')
            elif gen == '1/1' or gen == '1|1':
                variant_gens.append('1')
                variant_gens.append('1')
            elif gen == '1':
                variant_gens.append('1')
                variant_gens.append('?')
            else: #genotype == './.'
                variant_gens.append('?')
                variant_gens.append('?')
        all_gens.append(variant_gens)

num_char = len(all_gens)
print('\n'+str(num_char)+' processed\n\nWriting NEXUS file')

gen_matrix = []
for i in range(len(sample_list)):
    sample_gens = []
    for j in range(len(all_gens)):
        sample_gens.append(all_gens[j][i])
    sample_gens_join = ''.join(sample_gens)
    sample_data = sample_list[i]+'\t'+sample_gens_join+'\n'
    gen_matrix.append(sample_data)

outfile = open(args.o,'w')
outfile.write('#NEXUS\n'+
              'Begin DATA;\n'+
              '\tDimensions ntax='+str(num_samples*2)+' nchar='+str(num_char)+';\n'+
              '\tFormat datatype=standard symbols="01" gap=- missing=?;\n'+
              '\tMatrix\n\n')
for i in gen_matrix:
    outfile.write(i)
outfile.write(';\nEnd;\n')
outfile.close()

print('\nFinished!!!\n')
