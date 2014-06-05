#!/usr/bin/perl -nl
use strict;

# quick nmap gnmap parser for command line foo
# -kitkat 

next if ( $_!~m/Ports\:/i );
chomp();
my @toks=split( /Ports\:\s*/i, $_ );

my $host=$toks[0];
$host=~s/\s*Host\s*\:\s*(.*?)\s*\(.*?\).*/$1/ig;

my $rest=@toks[1 .. $#toks];
foreach my $port ( split(/,/,$rest ) ) {
    $port=~s/\s*(.*?)\s*/$1/ig;
    $port=~s/\//,/g;
    print "$host,$port";
}
