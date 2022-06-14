import os, sys, argparse, subprocess

print()

parser = argparse.ArgumentParser(description=
                                 'This script uses samtools to extract reads from a bam file that match a specified scaffold.\n'+
                                 'Run must include EITHER the -b (process single bam) OR -all (process all bams in directory) optional parameters')

requiredParam = parser.add_argument_group('required parameters')
requiredParam.add_argument('-s', type=str, metavar='scaffold', required=True, help='Scaffold to extract')

optionalParam = parser.add_argument_group('optional parameters')
optionalParam.add_argument('-b', type=str, metavar='input_bam', help='Input bam file')
optionalParam.add_argument('-all', type=bool, metavar='all_bams', default=False, help='True/False: Gather and process all files in directory with extension .bam [False]')
optionalParam.add_argument('-m', type=str, metavar='memory', default='12', help='Memory in Gb [12]')
optionalParam.add_argument('-w', type=str, metavar='walltime', default='1:00:00', help='Walltime in hours:mintues:seconds [12:00:00]')

args = parser.parse_args()
cwd = os.getcwd()

if args.b == None and args.all == False:
    print('ERROR: need to specify EITHER -b OR -all parameter')
    quit()

if args.b != None and args.all != True:
    print('ERROR: need to specify EITHER -b OR -all parameter (not both)')
    quit()

if args.all == False:
    bam_pbs = open(args.b.replace('.bam','_'+args.s+'.pbs'),'w')
    bam_pbs.write('#!/bin/tcsh\n'+
                  '#PBS -N '+args.s+'_samtools\n'+
                  '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
                  '#PBS -e '+args.b.replace('.bam','_'+args.s+'.err')+'\n'+
                  '#PBS -o '+args.b.replace('.bam','_'+args.s+'.out')+'\n'+
                  '\nmodule load dacosta/1.0\n'+
                  'cd '+cwd+'\n\n'+
                  'samtools view -b '+args.b+' '+args.s+' > '+args.b.replace('.bam','_'+args.s+'.bam\n\n\n'))
    bam_pbs.close()
                  
    command = ('qsub '+args.b.replace('.bam','_'+args.s+'.pbs'))
    p = subprocess.Popen(command, shell=True)
    sts = os.waitpid(p.pid, 0)[1]

if args.b == None:
    bam_list = []
    for file in os.listdir():
        if file.endswith('.bam'):
            bam_list.append(file)

    for bam in bam_list:
        bam_pbs = open(bam.replace('.bam','_'+args.s+'.pbs'),'w')
        bam_pbs.write('#!/bin/tcsh\n'+
                      '#PBS -N '+args.s+'_samtools\n'+
                      '#PBS -l pmem='+args.m+'gb,nodes=1:ppn=1,walltime='+args.w+'\n'+
                      '#PBS -e '+bam.replace('.bam','_'+args.s+'.err')+'\n'+
                      '#PBS -o '+bam.replace('.bam','_'+args.s+'.out')+'\n'+
                      '\nmodule load dacosta/1.0\n'+
                      'cd '+cwd+'\n\n'+
                      'samtools view -b '+bam+' '+args.s+' > '+bam.replace('.bam','_'+args.s+'.bam\n\n\n'))
        bam_pbs.close()
                      
        command = ('qsub '+bam.replace('.bam','_'+args.s+'.pbs'))
        p = subprocess.Popen(command, shell=True)
        sts = os.waitpid(p.pid, 0)[1]
        

