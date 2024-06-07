#!/usr/bin/perl

{
	use CGI;
    	use CGI::Carp qw(fatalsToBrowser);
    	use DBI;
    	use lib qw(/home/robel/softwares/localmodules/share/perl5/);
   	use CGI::Session;
    	use CGI::Session::Auth::DBI;
    	require '../lib/UTIL.pm';
    	require '../lib/AUTH.pm';
    	require '../lib/Commons.pm';
    

    	our %VHASH = ();

    	$CGI::POST_MAX = 1024 * 5000;
    	our $CGI_OBJ = CGI->new();

    	LoadVariables();


	my $url1 = qq{/cgi-bin/prd/biomuta/servlet.cgi};
	my $url2 = qq{/cgi-bin/prd/biomuta/servlet.cgi?gpageid=11&searchfield1=gene_name&searchvalue1=$VHASH{GENE}};
	my $url = ($VHASH{GENE} ? $url2 : $url1);

 

	print $CGI_OBJ->header();
    	print qq{<html>
    		<meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=$url\">
    		</html>
    	};
    	exit;
}




