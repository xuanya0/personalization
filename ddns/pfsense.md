

## Services -> BIND -> Settings -> Advanced Features -> Global settings
Use the folloinwg to allow additional keys for client DDNS update, you can generate the key on pfS using tsig-keygen
```
key "<keyname>" {
        algorithm hmac-sha256;
        secret "<key>";
};
```
## Services -> BIND -> Zones
Name Server
```
127.0.0.1 
```

Enable update-policy
Add the following to update-policy
```
grant rndc-key zonesub any;
grant <additional_keyname> name <FQDN> any;
```

# include this for DHCP hostname registration
## Services -> DHCP/v6
ipv4 or ipv6
```
DDNS Domain Key name: rndc-key
Key algorithm: <typically hmac-sha256>
Key secret: <secret>
DDNS Client Updates: Ignore
```

-----
copied from reddit: https://www.reddit.com/r/PFSENSE/comments/tb875o/finally_got_hostname_resolution_working_for_ipv6/

Finally got hostname resolution working for IPv6 LAN devices! here's how
Spent almost 24 hours doing research, went from zero knowledge of BIND to a working BIND+DDNS

Here's what I gathered

The ISC DHCPD doesn't seem able to generate a lease file to record the hostnames so unbound is unable to add DHCPv6 clients to its cache, but it can do DDNS, so we go with that.
NOTE: enter your pfsense webui using ip addr instead of fqdn
* download BIND from packages, disable DNS resolver + forwarder
* * Services->BIND->Settings:
* * * Settings: enable; listen on your choice of IFs or all IFs (firewal rules still prevent outside from querying your BIND)
* * * Views: Add a view to enable your BIND as a recursive resolver just like unbound{ match-clients: any, allow-recursion: any}
* * * Zones: {Zone Name: example.com} or whatever you purchased from registrar; {View: <your_created_view>, Name server: 127.0.0.1} IMPORTANT : {allow-update: localhost} or any if you want clients to directly update using DDNS {allow-query: any}To enable access of your pf via hostname Zone Domain records: {<hostname_of_pfsense>: A, 192.168.1.1, <hostname_of_pfsense>: AAAA, fe80::1:1}

* hopefully BIND can still correctly run DNS for you if things go wellEnter DHCP v6 settings
* * Hit Dynamic DNS display and enable DHCP registration
* * {DDNS Domain: example.com} or your domain name; {primary DDNS address: 127.0.0.1}
* * Looks like the web ui requires a DDNS key, I went with the rndc-key. view your key at: /var/etc/named/etc/namedb/named.conf and enter the following:{key name: rndc-key, algorithm: <hmac-sha256 or whatever in named.conf>, secret: <secret from named.conf>}
* * Add fe80::1:1 as a DNS server (without unbound/forwarder, DHCPs won't send out DNS).You have these options it seems, DHCPv4, DHCPv6, or Router Advertisement. I think as long as you get a DNS (either v4 or v6) from any of the options it's fine.Note: link local address seems very broken, despite getting a client assigned the address and to send DNS query, there's no response from BIND, just go with DNS on IPv4
* * Repeat for DHCPv4

now you should have a working dhcpv4/6 + DNS + hostname resolution; On a systemd linux, do `#systemctl restart NetworkManager`. This should restart the DHCP client

Some debugging methods:
* Services->BIND->Settings: you can increase logging level and add options to see what BIND is printing
* ssh into pfsense, create a file "record.txt" and run "nsupdate record.txt" no error should return. Then run the following to see if a record is inserted in BIND database:"/var/etc/named/etc/namedb: rndc dumpdb -zones && less named_dump.db"
* Finally, do a hostname lookup from any LAN dev, see if A/AAAA records show up

record.txt example:
```
server 127.0.0.1
zone example.com
update add abcdefg.example.com. 86400 A 1.2.3.4
show
send
```

One more optional step:

Although LAN devs should all have DNS working well and fine. But on pfsense, it might only work with FQDN instead of a simple hostname due to dhcp client overriding your search domain to the ISP's
disable it by unchecking System->General Setup->DNS Server Override

Caveats:

Of course a client has to have DHCPv6 support and send its hostname (Option 39)
So far I have only observed my linux machines working, no MacOS/iOS
