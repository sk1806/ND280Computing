#!/usr/bin/perl
#
# Extract relevant results from a processing job log file and send 
# the results to Simon's task which will fill the database. 
#
# Based on Ashok's script ashok-total-log-v9r7p1.sh*
# April 2011 - Changed to use perl instead of bash because of better string handling.
#
# Input: See subroutine "usage" below
#
# New return codes MUST be setup as follows: 
# curl --data-binary "Disk quota exceeded" -k -H 'Accept: text/plain' -X PUT 'https://procstatupdater:2aT0n8Ra@neut00.triumf.ca/t2k/processing/status/error_codes?-3'
#
# Defined return code so far
# 1  Success
# 0  Unspecified error
# -1 Error with gzip file
# -2 Segment violation
# -3 Disk quota exceeded
# -4 Disabled RooTracker module
# -5 Walltime exceeded limit (On bugaboo, logf has zero size, examine the jobOutput file instead)
# -6 Badly closed input file
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

#use strict;
use File::Basename;

sub usage() {
    my $self = basename($0);
    return <<EOF
Usage:

     $self  RUNNUMBER SUBRUN TYPE  LOG_DIR MON_DIR
         where TYPE is SPILL or COSMIC for raw data 
                      or MCP for MonteCarlo data 
               LOG_DIR is the directory where the log files produced by the job are residing
               MON_DIR is the directory where the monitoring data will be displayed by the web

  !IMPORTANT! This script will call script "post_status.sh" which MUST be executable from the PATH
              If not, you must specify the absolute path to the script in the line 
                           \$post_return_code = system("\$post_command");
               example:    \$post_return_code = system("\/home\/scripts\/\$post_command");

 Example: 
 Used on bugaboo, for production004
   ./send_mon_info.pl \${RUNNUMBER} \${SUBRUN} \${SPL_COS} output/v9r7p5  production004/B/rdp/ND280/00006000_00006999
 Used on neut14, 
  ./send_mon_info.pl 0000\$RUNN \$sub SPILL /data14b/t2ksrm/production004/A/rdp/ND280/00006000_00006999/logf/ production004/A/rdp/ND280/00006000_00006999

EOF
}

# Check number of input parameters

$numArgs = $#ARGV + 1;
if($numArgs < 5) {
    die usage();
}


my $RUN = shift;
my $SUBRUN = shift;
my $TYPE = shift;
my $LOG_DIR=shift;
my $MON_DIR=shift;


my $stage = "none";
my $output = "0 0 0 0";
my $IsMC = 0;
my $IsGenie = 0;
my $IsNeut = 0;

print "\nScan of log file for run $RUN, subrun $SUBRUN, type $TYPE\n";

my $type = "none";
if ( $TYPE eq "SPILL" ) {
    $type = "spl";
}
elsif ( $TYPE eq "COSMIC") {
    $type = "cos";
}
elsif ( $TYPE eq "MCP") {
    $type = "";
    $TYPE = "SPILL";
    $IsMC = 1;
}
else {
    print "Unknown type of data : $TYPE\n";
    exit 1;
}

###XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
sub post_status()
{
#
# Subroutine to call script post_status.sh
#
# ./post_status.sh MONDIR RUN SUBRUN RUNTYPE STAGE OUTPUT
#
# Where output is '' or 'RESULT TIME EVENTS_READ EVENTS_WRITTEN'
#
# Example:
#
# ./post_status.sh MONDAYTESTPAGE 5107 1 SPILL CALIBRATION '-1 5 6 12345'
    my $post_return_code = 0;
    my $post_command = "post_status.sh  $MON_DIR $RUN $SUBRUN $TYPE $stage '$output'";
###    print "Command: $post_command\n";
    $post_return_code = system("$post_command");
    print "post_return_code = $post_return_code\n";
    return $post_return_code;
}

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Check existence of log file
print "Log file is \n";
if ( system("ls -1 ${LOG_DIR}/oa_*_${type}*_${RUN}-${SUBRUN}*logf_*.log") ) {
    print " Log file not found. Exit on error \n";
    exit 1;
}

my $log = `ls -1 ${LOG_DIR}/oa_*_${type}*_${RUN}-${SUBRUN}*.log`;
#print "Log file is $log\n";
# Check generator if this is an MC
if ($IsMC == 1) {
    if ($log =~ /oa_nt_/ ) {
	print "This is a NEUT MC log file\n";
	$IsNeut = 1;
    }
    elsif ($log =~ /oa_gn_/ ) {
	print "This is a NEUT MC log file\n";
	$IsGenie = 1;
    }
}

#print "Curl will be sent for MON_DIR: $MON_DIR\n";

# Scan contents of log file
# We need to define variables to input in "curl"
# returnCode  , EventsIn, EventsOut ,stage  
my $InStage = 0;
my $returnCode = -1; 
my $EventsIn = 0;
my $EventsOut = 0;
my $Time = 0;

#================================================================
sub reset_variables() {
    $InStage = 0;
    $stage = "none";
    $returnCode = -1; 
    $EventsIn = 0;
    $EventsOut = 0;
    $Time = 0;
    $output = "0 0 0 0";
}    
#================================================================

open(IFILE,"<$log") or die "Cannot open file $log";
print "\nStarting to scan the log file\n";

my $line = "empty";

# At the moment, this script only checks for errors 
# one of CALIBRATION, RECONSTRUCTION or ANALYSIS stage
# is started. 
# We should be dealing with the ND280MC stage but the
# processing data base is not ready for this yet.  
# 
$stage = "PRECALIB";
$InStage = 0;

while(<IFILE>)
{
 #  Store $_ value 
    $line = $_;

 # Good practice to always strip the trailing
 # newline from the line.
    chomp($line);
    if ( ($line =~ /Midas File/ ) && ($line =~ /has been truncated/) ) {
	printf "$line\n";
	printf "Midas File probably missing\n";
	$returnCode = -1;
	$stage = "CALIBRATION";
        $output ="$returnCode $Time $EventsIn $EventsOut";
	post_status();
	$InStage = 0;
	last;
    }
    elsif ($line =~ /Starting job for oaCalib/){
	$InStage = 1;
	$stage = "CALIBRATION";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for oaRecon/){
	$InStage = 1;
	$stage = "RECONSTRUCTION";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for oaAnalysis/){
	$InStage = 1;
	$stage = "ANALYSIS";
	print "\n$line\n";
    }
    elsif ($InStage ==1) {
	if ($line =~ /Segmentation fault/){
	    printf "$line\n";
	    if ($line =~ /"oaCherryPicker-geo_v5mr.bat: line 7"/){
		printf "This is an acceptable error - ignore it\n";
	    }
	    else {
		$returnCode = -2;
		$output ="$returnCode $Time $EventsIn $EventsOut";
		post_status();
		$InStage = 0;
		last;
	    }
	}
	elsif ($line =~ /Disk quota exceeded/){
	    printf "$line\n";
	    $returnCode = -3;
	    $output ="$returnCode $Time $EventsIn $EventsOut";
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ( ($line =~ /Disabling module GRooTrackerVtx/) && $IsGenie){
	    printf "$line\n";
	    $returnCode = -4;
	    $output ="$returnCode $Time $EventsIn $EventsOut";
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ( ($line =~ /Disabling module NRooTrackerVtx/) && $IsNeut){
	    printf "$line\n";
	    $returnCode = -4;
	    $output ="$returnCode $Time $EventsIn $EventsOut";
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ($line =~ /probably not closed, trying to recover/){
	    printf "$line\n";
	    $returnCode = -6;
	    $output ="$returnCode $Time $EventsIn $EventsOut";
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ($line =~ /Total Events Read/){
#	print "$line\n";
	    my @ichunks = split /\s+/, $line;
#	printf "Chunks $ichunks[2] $ichunks[3]\n";
	    $EventsIn = $ichunks[3];
	}
	elsif ($line =~ /Total Events Written/){
#	print "$line\n";
	    my @ichunks = split /\s+/, $line;
#	printf "Chunks $ichunks[2] $ichunks[3]\n";
	    if ( ($stage eq "CALIBRATION") || ($stage eq "RECONSTRUCTION") ){
		$EventsOut = $ichunks[3];
	    }
	}
	elsif ($line =~ /Total number of events processed in Analysis/){
#	print "$line\n";
	    my @ichunks = split /\s+/, $line;
#	printf "Chunks $ichunks[8] $ichunks[9]\n";
	    $EventsOut = $ichunks[9];
	}
	elsif ($line =~ /Job Completed Successfully/){
	    print "$line\n";
	    $nextline = <IFILE>;
#	print "$nextline";
	    if ($nextline =~ /Run time/){
		my @ichunks = split /\s+/, $nextline;
		$Time = $ichunks[6];
		my @ichunks = split /\./, $Time;
#	    printf "Chunks $ichunks[0] $ichunks[1]\n";
		$Time = $ichunks[0];
	    }
	    $returnCode = 1;
	    $output ="$returnCode $Time $EventsIn $EventsOut";
#	print "Calling curl with $MONDIR $RUN $SUBRUN $TYPE $stage $output\n";
	    post_status();
	    reset_variables();
	}
    }
}
if ($InStage == 1) {
    print "The stage $stage has not completed succesfully, Error is unknown\n";
    $returnCode = 0;
    $output ="$returnCode $Time $EventsIn $EventsOut";
    print "Calling curl with $MONDIR $RUN $SUBRUN $TYPE $stage $output\n";
    post_status();
}

close(IFILE);

print "\nFinished scanning the log file\n";
exit 0;
