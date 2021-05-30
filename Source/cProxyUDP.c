#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>

int bindsocket( char* ip, int port );
int main( int argc, char* argv[] );

int bindsocket( char* ip, int port ) {
	int fd;
	struct sockaddr_in addr;

	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr( ip );
	addr.sin_port = htons( port );

	fd = socket( PF_INET, SOCK_DGRAM, IPPROTO_IP );
	if( -1 == bind( fd, (struct sockaddr*)&addr, sizeof( addr ) ) ) {
		fprintf( stderr, "Cannot bind address (%s:%d)\n", ip, port );
		exit( 1 );
	}

	return fd;
}

int main( int argc, char* argv[] ) {
	int i, listen, output;
	char *inip, *inpt, *srcip, *dstip, *dstpt;
	struct sockaddr_in src;
	struct sockaddr_in dst;
	struct sockaddr_in ret;

	if( 3 != argc && 5 != argc && 6 != argc ) {
		fprintf( stderr, "Usage: %s <listen-ip> <listen-port> [[source-ip] <destination-ip> <destination-port>]\n", argv[ 0 ] );
		exit( 1 );
	}

	i = 1;
	inip = argv[ i++ ];		/* 1 */
	inpt = argv[ i++ ];		/* 2 */
	if( 6 == argc )
		srcip = argv[ i++ ];	/* 3 */
	if( 3 != argc ) {
		dstip = argv[ i++ ];	/* 3 or 4 */
		dstpt = argv[ i++ ];	/* 4 or 5 */
	}
	
	listen = bindsocket( inip, atoi( inpt ) );
	if( 6 == argc ) {
		output = bindsocket( srcip, atoi( inpt ) );
	} else {
		output = listen;
	}

	if( 3 != argc ) {
		dst.sin_family = AF_INET;
		dst.sin_addr.s_addr = inet_addr( dstip );
		dst.sin_port = htons( atoi( dstpt ) );
	}
	ret.sin_addr.s_addr = 0;

	while( 1 ) {
		char buffer[65535];
		unsigned int size = sizeof( src );
		int length = recvfrom( listen, buffer, sizeof( buffer ), 0, (struct sockaddr*)&src, &size );
		if( length <= 0 )
			continue;

		if( 3 == argc ) {
			/* echo, without tracking return packets */
			sendto( listen, buffer, length, 0, (struct sockaddr*)&src, size );
		} else if( ( src.sin_addr.s_addr == dst.sin_addr.s_addr ) && ( src.sin_port == dst.sin_port ) ) {
			/* If we receive a return packet back from our destination ... */
			if( ret.sin_addr.s_addr )
				/* ... and we've previously remembered having sent packets to this location,
				   then return them to the original sender */
				sendto( output, buffer, length, 0, (struct sockaddr*)&ret, sizeof( ret ) );
		} else {
			sendto( output, buffer, length, 0, (struct sockaddr*)&dst, sizeof( dst ) );
			/* Remeber original sender to direct return packets towards */
			ret = src;
		}
	}
}