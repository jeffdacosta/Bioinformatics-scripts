BIOINFORMATICS PIPELINE: FASTQ TO GENOTYPES

INITIAL DATA

Short read fastq data. Typically paired-end reads for a set of samples.

STEP #1

Run fastQC to explore raw data.

script: sirius_fastqc.py
input file type: fastq
output file type: html

STEP #2

If adapter sequences are detected then trim them from data with AdapterRemoval. Re-run
fastQC to ensure that adapters were removed.

script: sirius_AdapterRemoval.py
input file type: fastq
output file type: fastq

STEP #3

For each sample, map reads to a reference genome using bwa.

script: sirius_bwa.py
input file type: fastq
output file type: sam

STEP #4

For each sample, use samtools compress, sort, index, and summarize results from bwa.

script: sirius_samtools.py
input file type: sam
output file type: bam

STEP #5

For each sample, remove PCR duplicates and re-format using picard tools.

script: sirius_picard.py
input file type: bam
output file type: bam

STEP #6

For each sample, use HaplotypeCaller in GATK to preliminarily genotype samples.

script: sirius_gatk_HaplotypeCaller.py
input file type: bam
output file type: gvcf

STEP #7

Combine genotype gvcf files for each sample using CombineGVCFs in GATK.

script: sirius_gatk_CombineGVCFs.py
input file type: gvcf
output file type: gvcf

STEP #8

Joint genotype samples using GenotypeGVCFs in GATK.

script: sirius_gatk_GenotypeGVCFs.py
input file type: gvcf
output file type: vcf

STEP #9

Use SelectVariants in GATK to retain only biallelic SNPs.

script: sirius_gatk_SelectVariants_BI.py
input file type: vcf
output file type: vcf

STEP #10

Use VariantFiltration in GATK to perform "hard filtering" of SNPs.

script: sirius_gatk_VariantFiltration.py
input file type: vcf
output file type: vcf

STEP #11

Retain only SNPs that pass filtering with SelectVariants in GATK.

script: sirius_gatk_SelectVariants_PASS.py
input file type: vcf
output file type: vcf

STEP #12

If needed, perform further filtering with vcftools.