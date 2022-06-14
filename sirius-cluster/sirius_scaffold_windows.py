import os, sys, gzip, subprocess, math

command = ('zcat '+sys.argv[1]+' | tail -n1 > temp')
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

infile = open('temp','r')
last_variant = int(infile.readline().split()[1])

num_windows = math.floor(last_variant/100000)

begin = 0
end = 100001

cwd = os.getcwd()

pbsfile = open(sys.argv[1].replace('.vcf.gz','_win.pbs'),'w')
pbsfile.write('#!/bin/tcsh\n'+
              '#PBS -l pmem=8b,nodes=1:ppn=1,walltime=23:00:00\n'+
              '#PBS -e '+sys.argv[1].replace('.vcf.gz','_win.err')+'\n'+
              '#PBS -o '+sys.argv[1].replace('.vcf.gz','_win.out')+'\n'+
              '\nmodule load dacosta/1.0\n'+
              'cd '+cwd+'\n\n')

for i in range(num_windows):
    pbsfile.write('vcftools --gzvcf '+sys.argv[1]+
                  ' --chr '+sys.argv[1].replace('genotype_auto_biSNP_filt2_','').replace('.vcf.gz','')+
                  ' --from-bp '+str(begin)+
                  ' --to-bp '+str(end)+
                  ' --recode --stdout | gzip -c > '+sys.argv[1].replace('.vcf.gz','_win'+str(i+1)+'.vcf.gz')+'\n')
    begin += 100000
    end += 100000
pbsfile.write('\n\n')
pbsfile.close()

command = ('qsub '+sys.argv[1].replace('.vcf.gz','_win.pbs'))
p = subprocess.Popen(command, shell=True)
sts = os.waitpid(p.pid, 0)[1]

