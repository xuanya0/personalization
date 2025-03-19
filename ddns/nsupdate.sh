# for FreeBSD only
#!/bin/sh
ipv6=`ifconfig | grep inet6.*autoconf | awk '{ print $2 }'`

echo "
server <dns server>
zone <zonename>
key hmac-sha256:<keyname> <key>
update del <fqdn> AAAA
update add <fqdn> 86400 AAAA $ipv6
show
send
" | nsupdate
