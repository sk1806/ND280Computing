#!/usr/bin/perl
# 

use File::Basename;
use Cwd;

############## begin subroutines

sub usage() {
    my $self = basename($0);
    return <<EOF
Usage:

      $self  SOFTWARE_VERSION SCRIPT TRIGGER DIR_PATH FILE_LIST LOCATION

 Opens a file FILE_LIST with list of input files  to process in subdirectory DIR_PATH
 
 Ex ./gen_qsub.pl  v10r3  nd280_rdp_verify_all.pbs  SPILL  production005/A/rdp/verify/v10r3/ND280  run_test_files.list  wg-bugaboo

 Will generate a command similar to:
qsub -N rdp00004165_0001  -j oe  -o b0:/global/scratch/t2k/production005/A/rdp/verify/v10r3/ND280/jobOutput/00004165_0001  -v INPUT_FILE=nd280_00004165_0001.daq.mid.gz,DIR_PATH=production005/A/rdp/verify/v10r3/ND280,SOFTWARE_VERSION=v10r3,TRIGGER=SPILL,LOCATION=westgrid-bugaboo,SCRIPT_DIR=/home/t2k/production/production005/A/rdp/scripts  nd280_rdp_verify_all.pbs

EOF
}

sub getjobssubmitted {

    my $njobs = `qstat | grep -c t2k`;
    chomp $njobs;
    return $njobs;

}

############ main

# Definitions
my $scratch_base = "/global/scratch/t2k";
my $home_base = "/home/t2k/production";
my $thisDir = getcwd();

my $maxjobssubmitted = 498;
my $sleeptime = 600;

# Check number of input parameters

my $numArgs = $#ARGV + 1;
if($numArgs < 6) {
    print "\n\n!!! MISSING ARGUMENTS !!!\n\n";
    die usage();
}

#Input values
my $nd280_soft_version = shift;
my $script = shift;
my $trigger = shift;
my $dir_path = shift;
my $list_file= shift;
my $location = shift;


open(IFILE,"$list_file") or die "cannot open file $list_file";
my $njobs = 0;
my $qjobs = 0;

$qjobs = &getjobssubmitted;
print "There are $qjobs T2K jobs on the queue currently\n";

while (<IFILE>)
{    
    while ($qjobs >= $maxjobssubmitted) {
	print &getjobssubmitted," jobs submitted >= $maxjobssubmitted; sleeping for $sleeptime seconds\n";
	sleep $sleeptime;
	$qjobs = &getjobssubmitted;
    }

    chop; # To remove the trailing CR
    my $input_file = $_;
    print " \n";
#    if ( $_ =~ /_(.*?)_(.*?)_(.*?)_/ ) {
    if ( $_ =~ /_(.*?)_/ ) {
	my @ichunks = split( /_/, $_);
	my $runn =$ichunks[1];
	my $run = $runn;
        $run =~ s/000//;
	my @ichunk = split( /\./, $ichunks[2]);
	my $subrun = $ichunk[0];	
	print "Run $runn, Subrun $subrun\n";
# Create the qsub command options
	my $minusN="-N rdp_${run}_${subrun}_${trigger}";
	my $minusj="-j oe ";
	my $minuso="-o $scratch_base/$dir_path/jobOutput/${trigger}_${runn}_${subrun} ";
	if ( $location =~ /bugaboo/ ) {
	    $minuso="-o b0:$scratch_base/$dir_path/jobOutput/${trigger}_${runn}_${subrun} ";
	}
	my $minusv="-v INPUT_FILE=$input_file,DIR_PATH=$dir_path,SOFTWARE_VERSION=$nd280_soft_version,TRIGGER=$trigger,LOCATION=$location,SCRIPT_DIR=$thisDir";
	my $command="qsub $minusN $minusj $minuso $minusv  $script";
	print "$command\n";
	$result = system($command);
	if ( $result) { 
	    print "Command failed: $command\n";
	} else {
	    $njobs = $njobs +1;
	    $qjobs = $qjobs +1;
	}
	sleep 1;
    }
    else {
	print "Cannot submit job for input file $input_file\n";
	print "Could not find RUNN and SUBRUN in expected location\n";
    }
}
close(IFILE);
print "Submitted $njobs jobs\n";


