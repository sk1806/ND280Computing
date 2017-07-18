#!/usr/bin/perl
#
# Extract relevant results from a processing job log file and send 
# the results to Simon's task which will fill the database. 
#
# April 2011 - Use perl instead of bash because of better string handling.
#
# Updated November 2011 by S.C. and R.P.
#  * use post_status.py instead of post_status.sh
#  * add $Site attribute
#  * make $STAGE primary key match new values expected by post_status.py 
#    (nd280MC, elecSim, cali, reco, anal)


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
# -4 Disabled module
# -5 Walltime exceeded limit (On bugaboo, logf has zero size, examine the jobOutput file instead)
# -6 Badly closed input file
# -7 Memory allocation failure
# -8 No database for spillnum
# -9 Error with connection to MySQL server.
# -10 No pass through info
# -11 EProductionException

#####
#
# DATABASE NOTES:
#
# {MON_DIR RUN SUBRUN TRIGTYPE STAGE} is a COMPOSITE PRIMARY KEY uniquely
# identifying a processing job.
#
#  Site, ReturnCode, Time, EventsIn & EventsOut are NON-KEY ATTRIBUTES of a processing job. 
#
#####

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

#use strict;
use File::Basename;

sub usage() {
    my $self = basename($0);
    return <<EOF
Usage:

     $self  SITE TYPE FILENAME MON_DIR
         where SITE is a string identifying the site where the processing took place
               TYPE is a string identifying the type of processing
                      SPILL or COSMIC for raw data 
                      or MCP for MonteCarlo data (beam triggers)
                      or MCCOS for cosmic MonteCarlo
	       FILENAME is the name of a log file
               MON_DIR (optional) is the directory where the monitoring data will be displayed by the web
                   If MON_DIR is not specified, the script post_status won't be called. 

  !IMPORTANT! This script will call script "post_status.py" which MUST be executable from the PATH
              If not, you must specify the absolute path to the script in the line 
                           \$post_return_code = system("\$post_command");
               example:    \$post_return_code = system("\/home\/scripts\/\$post_command");

 Example:
A) No info sent to the monitoring database  
   ./check_mon_info.pl TRIUMF MCCOS logf_cosmicnew/oa_cs_mu_00000977-0000_ousy5alxrroc_logf_000_basecosmiccorsikanew.log

B)Info sent to database for MON_DIR 
   ./check_mon_info.pl TRIUMF SPILL logf/oa_nd_spl_00006965-0096_og4cmgx6amy7_logf_000_v9r7p3triumf.log production004/A/rdp/ND280/00006000_00006999

EOF
}

# Check number of input parameters

$numArgs = $#ARGV + 1;
if($numArgs < 3) {
    die usage();
}

my $Site = shift;
my $TYPE = shift;
my $FILENAME=shift;
my $MON_DIR=shift;

if ($MON_DIR eq ""){
print "\n !!! MON_DIR is not defined. No monitoring info will be sent to processing DB!!!\n\n";
}
my $STAGE = "none";
my $IsMC = 0;
my $IsGenie = 0;
my $IsNeut = 0;
my $script_dir = $ENV{'SCRIPT_DIR'};

# Check existence of log file
unless (-e $FILENAME)  {
    print " Log file $FILENAME not found. Exit on error \n";
    exit 1;
}

my $RUN = " ";
my $SUBRUN = " ";
# Extract run and subrun numbers
my @ichunks = split ( "/" , $FILENAME);
my $filename = $ichunks[$#ichunks];
#print "Filename is $filename \n";

if ( $filename =~ /_(.*?)_(.*?)_(.*?)_/ ) {
    my @fchunks = split( /-/, $3);
    $RUN =$fchunks[0];
    $SUBRUN = $fchunks[1];
}
else {
    print "Cannot find the run and subrun numbers were expected in $filename\n";
    exit -1;
}

print "Starting to scan file $filename\n";
print "for run $RUN, subrun $SUBRUN, type $TYPE\n";

my $TRIGTYPE = "none";
if ( $TYPE eq "SPILL" ) {
    $TRIGTYPE = "spill";
}
elsif ( $TYPE eq "COSMIC") {
    $TRIGTYPE = "cosmic";
}
elsif ( $TYPE eq "MCP") {
    $TRIGTYPE = "spill";
    $IsMC = 1;
}
elsif ( $TYPE eq "MCCOS") {
    $TRIGTYPE = "all";
    $IsMC = 1;
}
else {
    print "Unknown type of data : $TYPE\n";
    exit 1;
}

# Check generator if this is a beam MC
if ($IsMC == 1) {
    if ($filename =~ /oa_nt_/ ) {
	print "This is a NEUT MC log file\n";
	$IsNeut = 1;
    }
    elsif ($filename =~ /oa_gn_/ ) {
	print "This is a GENIE MC log file\n";
	$IsGenie = 1;
    }
}

# Scan contents of log file
# We need to define variables to send out via the script post_status.py
#  ReturnCode, Time, EventsIn, EventsOut  
my $InStage = 0;
my $ReturnCode = -1; 
my $EventsIn = 0;
my $EventsOut = 0;
my $Time = 0;

#================================================================
sub reset_variables() {
    $InStage = 0;
    $STAGE = "none";
    $ReturnCode = 1; 
    $EventsIn = 0;
    $EventsOut = 0;
    $Time = 0;
}    
#================================================================


#================================================================
sub post_status()
{
#
# Subroutine to call script post_status.py
#
# SYNTAX is 
#  ./post_status.py [options] MON_DIR RUN SUBRUN TRIGTYPE STAGE
#
# Where options are NOT optional and MUST be submitted
# Currently there is NO check for this in post_status.py
# --site=2 --result=1 --time=1577 --read=5062 --written=310
# 
# EXIT codes:        0 - Request succeeded 
#                   >0 - error
#
# Example:
#
# ./post_status.py --site=SITESTRING --result=1 --time=1577 --read=5062 --written=310 production004/B/rdp/ND280/00005000_00005999 5012 6 SPILL RECONSTRUCTION
#
#    print "MON_DIR is $MON_DIR\n";

    my $post_return_code = 0;
    my $cpk_attr = "$MON_DIR $RUN $SUBRUN $TRIGTYPE $STAGE";
    my $attr = "--site=$Site --result=$ReturnCode --time=$Time --read=$EventsIn --written=$EventsOut";
    print "Result for $RUN $SUBRUN $TRIGTYPE $STAGE is: $Site, $ReturnCode, $Time, $EventsIn, $EventsOut\n";
    if($MON_DIR eq ""){
	print "No monitoring info sent because MON_DIR is not defined\n";
	return;
    }
    else {
	$post_return_code = 0;
	my $post_command = "$script_dir/post_status.py $attr $cpk_attr";
	print "Command:$post_command\n";
	$post_return_code = system("$post_command");
	if ( $post_return_code > 0) {
	    print "Posting FAILED, post_return_code = $post_return_code\n";
	}
	return;
    }
}
#================================================================


open(IFILE,"<$FILENAME") or die "Cannot open file $log";
#print "\nStarting to scan file $FILENAME\n";

my $line = "empty";

# At the moment, this script only checks for errors 
# once the nd280MC stage is started. 
#
 
$STAGE = "preMC";
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
	$ReturnCode = -1;
	$STAGE = "cali";
	post_status();
	$InStage = 0;
	last;
    }
    elsif ($line =~ /Starting job for nd280MC/){
	$InStage = 1;
	$STAGE = "nd280MC";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for elecSim/){
	$InStage = 1;
	$STAGE = "elecSim";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for oaCosmicTrigger/){
	$InStage = 1;
	$STAGE = "COSMICTRIG";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for oaCalib/){
	$InStage = 1;
	$STAGE = "cali";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for oaRecon/){
	$InStage = 1;
	$STAGE = "reco";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for oaAnalysis/){
	$InStage = 1;
	$STAGE = "anal";
	print "\n$line\n";
    }
    elsif ($line =~ /Starting job for /){
	print "\n$line\n";
    }
    elsif ($line =~ /Found Command event_select /){
	print "\n$line\n";
	my @ichunks = split( / /, $line);
#	printf "Chunks $ichunks[4] $ichunks[5]\n";
	$TRIGTYPE = $ichunks[5];
    }
    elsif ($InStage ==1) {
	if ($line =~ /Segmentation fault/){
	    printf "$line\n";
	    if ($line =~ /"oaCherryPicker-geo_v5mr.bat: line 7"/){
		printf "This is an acceptable error - ignore it\n";
	    }
	    else {
		$ReturnCode = -2;
		post_status();
		$InStage = 0;
		last;
	    }
	}
	elsif ($line =~ /Disk quota exceeded/){
	    printf "$line\n";
	    $ReturnCode = -3;
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ( $line =~ / ERROR: No database for spillnum/ ){
	    printf "$line\n";
	    $ReturnCode = -8;
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ( $line =~ / No BSD data available/ ){
	    printf "$line\n";
	    $ReturnCode = -8;
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ( $line =~ /No pass through information could be found/ ){
	    printf "$line\n";
	    $ReturnCode = -10;
	    post_status();
	    $InStage = 0;
	    last;
	}
	elsif ( $line =~ /Disabling module / ){
	    printf "IsMC = $IsMC\n";
	    if ( $IsMC == 1 ){
		printf "After testing IsMC = $IsMC\n";		
		if ( ($line =~ /Disabling module GRooTrackerVtx/) && $IsGenie){
		    printf "Atest $line\n";
		    $ReturnCode = -4;
		    post_status();
		    $InStage = 0;
		    last;
		}
		elsif ( ($line =~ /Disabling module NRooTrackerVtx/) && $IsNeut){
		    printf "Btest $line\n";
		    $ReturnCode = -4;
		    post_status();
		    $InStage = 0;
		    last;
		}
		elsif ( ! ($line =~ /RooTracker/)  ){
		    printf "Ctest $line\n";
		    $ReturnCode = -4;
		    post_status();
		    $InStage = 0;
		    last;
		}
	    }
	}
	elsif ($line =~ /probably not closed, trying to recover/){
	    printf "$line\n";
	    $ReturnCode = -6;
	    post_status();
	    $InStage = 0;
	    last;
	}
        elsif ($line =~ /St9bad_alloc/){
            printf "$line\n";
            $ReturnCode = -7;
            post_status();
            $InStage = 0;
            last;
        }
 	elsif ($line =~ /No luck connecting to GSC MySQL server/){
	    printf "$line\n";
	    $ReturnCode = -9;
	    post_status();
	    $InStage = 0;
	    last;
	}
        elsif ($line =~ /EProductionException/){
            printf "$line\n";
            $ReturnCode = -11;
            post_status();
            $InStage = 0;
            last;
        }
	elsif ($line =~ /Total Events Read/){
	    my @ichunks = split /\s+/, $line;
#	    printf "Chunks $ichunks[2] $ichunks[3]\n";
	    $EventsIn = $ichunks[3];
	}
	elsif ($line =~ /Total Events Written/) {
	    my @ichunks = split /\s+/, $line;
#	    printf "Chunks $ichunks[2] $ichunks[3]\n";
###	    if ( ($STAGE eq "CALIBRATION") || ($STAGE eq "RECONSTRUCTION") ||  ($STAGE eq "elecSIM") ||  ($STAGE eq "COSMICTRIG") ){
		$EventsOut = $ichunks[3];
###	    }
	}
	elsif ($line =~ /Number of events =/) {
	    my @ichunks = split /\s+/, $line;
#	    printf "Chunks $ichunks[4] $ichunks[5]\n";
	    if ( $STAGE eq "nd280MC" ){
		$EventsOut = $ichunks[5];
	    }
	}
	
	elsif ($line =~ /Total number of events processed in Analysis/){
	    my @ichunks = split /\s+/, $line;
#	printf "Chunks $ichunks[8] $ichunks[9]\n";
	    $EventsOut = $ichunks[9];
	}
	elsif ($line =~ /Job Completed Successfully/){
	    print "$line\n";
	    $nextline = <IFILE>;
	    if ($nextline =~ /Run time/){
		my @ichunks = split /\s+/, $nextline;
		$Time = $ichunks[6];
		my @ichunks = split /\./, $Time;
#	    printf "Chunks $ichunks[0] $ichunks[1]\n";
		$Time = $ichunks[0];
	    }
	    $ReturnCode = 1;
	    if ($STAGE eq "COSMICTRIG")	{
		print "Not sure what this stage is yet - no call to post_status\n";
	    } else {
		post_status();
	    }
	    reset_variables();
	}
    }
}
if ($InStage == 1) {
    print "The stage $STAGE has not completed succesfully, Error is unknown\n";
    $ReturnCode = 0;
    post_status();
}

close(IFILE);

print "\nFinished scanning the log file. Last check return code posted is $ReturnCode\n";
exit $ReturnCode;
