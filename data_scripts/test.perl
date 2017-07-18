#!/usr/bin/perl

$filename = "test.txt";
open(my $fh, '<:encoding(UTF-8)', $filename);
@lines = <$fh>;
print "glite-transfer-cancel -s https://lcgfts3.gridpp.rl.ac.uk:8443/services/FileTransfer ";
foreach $line (@lines) {
    #print $line;
    my @words = split /\s+/, $line;
    print $words[0]." ";
}
close($filename);
