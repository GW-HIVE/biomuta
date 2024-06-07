#!/usr/bin/perl
{
	use CGI;
    	use CGI::Carp qw(fatalsToBrowser);
    	use DBI;
   	use CGI::Session;
    	use CGI::Session::Auth::DBI;
    	use JSON;
	require '../lib/UTIL.pm';
    	require '../lib/AUTH.pm';
    	require '../lib/Global.pm';    




    	our %VHASH = ();
    	our %CHASH = ();
    	our %SHASH = ();
    	our %GHASH = ();
    	our %SECID2NAME = ();
	our %GSECID2NAME = ();

    	$CGI::POST_MAX = 1024 * 5000;
    	our $CGI_OBJ = CGI->new();


	our $configJson;
	our $GPHASH,$PHASH;
	our $SERVER;

	$configJson->{global} = LoadConfig("../conf/global.config.json");
	$configJson->{local} = LoadConfig("conf/config.json");
	$GPHASH = $configJson->{global};
	$PHASH = $configJson->{local};
	$SERVER =  $configJson->{local}{server};
       

	LoadVariables();
	$GPHASH->{device} = GetDeviceType();
        
	my $dns = qq{dbi:mysql:database=$GPHASH->{$SERVER}{dbinfo}{dbname};};
	$dns .= qq{host=$GPHASH->{$SERVER}{dbinfo}{dbhost};user=$GPHASH->{$SERVER}{dbinfo}{dbuserid};};
    	$dns .= qq{password=$GPHASH->{$SERVER}{dbinfo}{dbpassword}};
    	
	our $SESSION = new CGI::Session(undef, $CGI_OBJ, {Directory=>'/tmp'});
    	our $AUTH = new CGI::Session::Auth::DBI({CGI => $CGI_OBJ, Session => $SESSION, DSN => "$dns",});
	our $DBH = DBI->connect($dns) or die("Couldn't connect to database");

    	print $SESSION->header();
    	if($CGI_OBJ->param('log_password')){
       		$CGI_OBJ->param(-name=>'log_password', -value=> $AUTH->_encpw($CGI_OBJ->param('log_password')));
    	}
	$AUTH->authenticate();
    	$VHASH{USERNAME} = $AUTH->profile('username');
   	$VHASH{USERID} = $AUTH->profile('userid');
    	$VHASH{FULLNAME} = $AUTH->profile('fname') . " " . $AUTH->profile('lname');
    	if(!Trim($VHASH{FULLNAME})){ $AUTH->logout();}
    	LoadUserGroups();


	my $loginStatus = $AUTH->loggedIn();
	$VHASH{READONLY} = ($loginStatus ? 0 : 1);



        $VHASH{GPAGEID} = $PHASH->{firstgpageid};

        
        $VHASH{PAGEID} = ($VHASH{PAGEID} ? $VHASH{PAGEID} : $PHASH->{firstpageid});
	$VHASH{MODE} = (!$VHASH{MODE}  ? "html" : $VHASH{MODE});

    	if($VHASH{MODE} eq "json"){ #Construct and return json text
       		if($VHASH{SVC} eq "getStats"){
                        my $cmd = qq{python $PHASH->{$SERVER}{pathinfo}{cgipath}/svc/getStats.py -j '$VHASH{INJSON}'};
                        my $jsonText = `$cmd`;
                        print "$jsonText";
                        exit;
                }
		elsif ($VHASH{SVC} eq "searchBioMuta"){
                        my $cmd = qq{python $PHASH->{$SERVER}{pathinfo}{cgipath}/svc/searchBioMuta.py -j '$VHASH{INJSON}'};
                        #print "{\"cmd\":\"$cmd\"}";
			my $jsonText = `$cmd`;
                        print "$jsonText";
                        exit;
                }
		elsif ($VHASH{SVC} eq "getProteinData"){
                        my $cmd = qq{python $PHASH->{$SERVER}{pathinfo}{cgipath}/svc/getProteinData.py -j '$VHASH{INJSON}'};
                        #print "{\"cmd\":\"$cmd\"}";
                        my $jsonText = `$cmd`;
                        print "$jsonText";
                        exit;
                }
                elsif ($VHASH{SVC} eq "checkAccession"){
                        my $cmd = qq{python $PHASH->{$SERVER}{pathinfo}{cgipath}/svc/checkAccession.py -j '$VHASH{INJSON}'};
                        #print "{\"cmd\":\"$cmd\"}";
                        my $jsonText = `$cmd`;
                        print "$jsonText";
                        exit;
                }
	}




	my %jsParHash = (
                "deviceType"=> "device"
                ,"moduleName" => "module"
                ,"moduleBase" => "baseurl"
                ,"ghtmlRoot" => "ghtmlroot"
                ,"gcgiRoot" => "gcgiroot"
                ,"htmlRoot" => "htmlroot"
                ,"jsonPath" => "jsonpath"
		,"svcPath" => "svcpath"
                ,"cgiRoot" => "cgiroot"
                ,"baseUrl" => "baseurl"
        	,"moduleMenuBg" => "modulemenubg"
                ,"moduleMenuFg" => "modulemenufg"
		,"pageBase" => "pagebase"
                ,"downloadBase" => "downloadbase"
                ,"moduleRelease" => "release"
		,"bioxpressUrl" => "bioxpressurl"
		,"oncomxUrl" => "oncomxurl"
                ,"proteinviewUrl" => "proteinviewurl"
	);
        my %jsVarHash = (
                "gpageId" => "GPAGEID"
                ,"pageId" => "PAGEID"
		,"readOnly" => "READONLY"
        );

         
	my @gjsFiles = ('jquery-1.11.1.min.js', 'bootstrap.bundle.min.js', 'common.js', 'loader.js',
		'highcharts.js', 'exporting.js', 'data.js', 'highchartsMore.js', 
		'heatmap.js', 'vjHighCharts.js', 'vjGoogleChart.js');
        my @gcssFiles = ('bootstrap.min.css', 'global.css', 'googlefonts.css');
        my @jsFiles = ('module.js');
        my @cssFiles = ();

	my $gheadLinks = GetGlobalHeadLinks(\@gcssFiles, \@gjsFiles);
	my $headLinks = GetModuleHeadLinks(\@cssFiles, \@jsFiles, \%jsParHash, \%jsVarHash);
	my $headerDivOne = getHeaderDivOne();        
        my $headerDivTwo = getHeaderDivTwo();  
	my $footer = GetFooter();



	print qq{<html>
                <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                        $gheadLinks $headLinks
                </head>
                <BODY>
		<form name=form1 method=POST action=biomuta enctype="multipart/form-data">
                        $headerDivOne
                        $headerDivTwo
			<div class=pagewrapper>
                        	<div class=pagecn id=pagecn></div>
			</div>
			<input type=hidden name=gpageid value="$VHASH{GPAGEID}">
                        <input type=hidden name=action value="">
		</form>

		<div class="footnote">
                        $footer
                </div>

                </BODY>
                </html>
        };
        $DBH->disconnect();
    	exit;
}










