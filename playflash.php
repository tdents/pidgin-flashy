#!/usr/bin/php
<?php
$delay=50000;
$light=50000;
$d=0;
if(isset($argv[1])) {
	if(strlen($argv[1]) > 0) {
		$file = $argv[1];
	}
}
$program=file_get_contents($file);
//init
$dVendor=''; #device vendor id
$dProduct=''; #device product id
$devicepath=exec("ls /sys/bus/usb/devices/*/idVendor | xargs grep -rl ".$dVendor." | awk -F '/idVendor' '{ print $1\"/idProduct\" }' | xargs grep -rl ".$dProduct." | awk -F '/idProduct' '{ print $1 }'");
if(!strpos($devicepath,'sys/bus/usb/devices')) { echo "No device\r\n"; die; }
echo $devicepath."\r\n";
exec('echo 0 > '.$devicepath.'/power/autosuspend_delay_ms');

$powerlevel=$devicepath.'/power/level';
global $powerlevel,$devicepath;

function on() {
	global $powerlevel;
	system('echo on > '.$powerlevel);
}
function off() {
	global $powerlevel;
	system('echo auto > '.$powerlevel);
}
off();

$str = $program;
$i = 0;

do {
	if($str{$i} > 0) {
		$sleeptime=$light*$str{$i};
		on(); usleep($sleeptime);off();
	}
	if($str{$i} == '0') {
		usleep($delay);
	}
	echo $str{$i};
    ++$i;
} while (isset($str{$i}));

off();

?>

