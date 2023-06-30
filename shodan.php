<?php

function usage( $err=null ) {
    echo 'Usage: '.$_SERVER['argv'][0]." <search> [shodan_api_key]\n";
    if( $err ) {
        echo 'Error: '.$err."\n";
    }
    exit();
}

if( $_SERVER['argc']<2 || $_SERVER['argc']>3 ) {
    usage();
}

if( $_SERVER['argc'] == 3 ) {
    $_api_key = trim($_SERVER['argv'][2]);
} else {
    $_api_key = getenv('SHODAN_KEY');
}
if( !$_api_key ) {
    usage('API key nmot found');
}

$search = urlencode( $_SERVER['argv'][1] );
$page = 1;
$run = true;
$t_result = [];

echo "Searching: ".$search."\n\n";

do
{
	$url = 'https://api.shodan.io/shodan/host/search?query='.$search.'&page='.$page.'&key='.$_api_key;
	echo $url."\n";
	$c = @file_get_contents( $url );
	if( !$c ) {
		exit( "Err: cannot connect to Shodan, check your API key!\n" );
	}

	$t_json = json_decode( $c, true );

	if( !count($t_json['matches']) ) {
		$run = false;
	} else {
		$t_result = array_merge( $t_result, $t_json['matches'] );
		$page++;
		//$run = false;
	}
}
while( $run );


echo "\n".count($t_result)." results found.\n\n";

foreach( $t_result as $r )
{
	echo $r['ip_str'].':'.$r['port']."\n";
}

exit();

?>
