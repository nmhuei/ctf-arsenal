To recap, the TLS handshake can be split up into four main stages. Despite changes in TLS 1.3, these high-level stages remain:

1. Client and server exchange capabilities, and agree upon connection parameters.
2. Certificate(s) presented are verified, or authentication occurs using other means.
3. A shared master secret is agreed upon that will be used to derive encryption keys for the connection.
4. Both sides verify that no handshake messages have been tampered with.

  
  
As we just saw, in the old days of RSA key exchanges, having your RSA private key compromised was really quite bad. If an attacker could observe TLS network traffic, and either access the RSA key or crack the RSA parameters directly from the certificate, they could compromise not just present and future network traffic, but also past traffic. There were suspicions that intelligence agencies were doing just that - recording all traffic that they could in order to break it one day. Therefore a drive began to make forward secrecy a requirement of modern TLS.
  
  
In a TLS connection using Ephemeral Diffie-Hellmann key exchange, when a client connects, the server generates an ephemeral key pair. This ephemeral key pair is used in the key exchange with the client to generate a session key for the connection. The server's certificate key pair (usually RSA, for performance reasons) is now used only to authenticate the TLS handshake. After the connection ends, the server should delete its ephemeral key pair, although in practice it may remain in server memory for awhile.
  
  
To decrypt TLS 1.3 connections we need the parameters that were used to generate the shared master secret. Attached is a keylogfile.txt which contains these Diffie-Hellman parameters, recorded by a client connecting to "tls3.cryptohack.org". Once again, decrypt this traffic to find the flag in the HTTP/2 stream.
  
  
**Challenge files:**
  
-
[tls3.cryptohack.org.pcapng](/static/challenges/tls3_871583423e02a66acd81eb34ed967489.cryptohack.org.pcapng)
  
-
[keylogfile.txt](/static/challenges/keylogfile_c86a7e105b820e0780e903b0d8388fa3.txt)
  
  
**Resources:**
  
-
[Wireshark: TLS Decryption](https://wiki.wireshark.org/TLS#tls-decryption)
  
-
[NSS Key Log Format](https://web.archive.org/web/20230322192727/https://firefox-source-docs.mozilla.org/security/nss/legacy/key_log_format/index.html)
  
-
[Industry Concerns about TLS 1.3](https://mailarchive.ietf.org/arch/msg/tls/CzjJB1g0uFypY8UDdr6P9SCQBqA/)
