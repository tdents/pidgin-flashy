use Purple;
use IO::Socket::INET;

###

%PLUGIN_INFO = (
	perl_api_version => 2,
	name => "FlashyLightPlugin",
	version => "1.0",
	summary => "Flashing LED connected to USB port",
	description => "Changes value in /var/flash/status",
	author => "Me",
	url => "http://localhost/",
	load => "plugin_load",
	unload => "plugin_unload"
);

sub plugin_init {
	return %PLUGIN_INFO;
}

sub plugin_load {
	my $plugin = shift;

	my $conv_handle = Purple::Conversations::get_handle();

	Purple::Signal::connect($conv_handle, "received-im-msg", $plugin, \&update_unread_count, '');
	Purple::Signal::connect($conv_handle, "received-chat-msg", $plugin, \&update_unread_count, '');
	Purple::Signal::connect($conv_handle, "conversation-updated", $plugin, \&update_unread_count, '');
	Purple::Signal::connect($conv_handle, "conversation-created", $plugin, \&update_unread_count, '');
	Purple::Signal::connect($conv_handle, "deleting-conversation", $plugin, \&update_unread_count, '');

	update_unread_count();
}

sub total_unread_count {
	my $total_unread = 0;
	my @convs = Purple::get_conversations();

	for my $conv (@convs) {
		my $data = $conv->get_data('unseen-count');
		next unless defined($data);
		my $this_unread = $data->{_purple};
		$total_unread += $this_unread;
	}

	return $total_unread;
}

sub update_unread_count {
	my $unread = total_unread_count();
	my $code = '44231';
	my ($socket,$client_socket);
	$socket = new IO::Socket::INET (
		PeerHost => '127.0.0.1',
		PeerPort => '8888',
		Proto => 'tcp',
		) or die "ERROR in Socket Creation : $!\n”;
	$data = "$code $unread";
	print $socket $data;
	$socket->close();
}

sub plugin_unload {
	my $plugin = shift;
}
