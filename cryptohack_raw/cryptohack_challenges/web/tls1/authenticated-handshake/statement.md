Authentication occurs in the TLS handshake in three messages:

1. **Certificate**
   . Contains the identity of the server, with signatures on the certificate chaining up to a certificate authority trusted by the client. In mutual TLS, the client also sends a certificate of its own identity for the server to verify. We'll talk about certificates more in TLS Part 2.
2. **CertificateVerify**
   . The server makes a signature over the entire handshake so far using the private key corresponding to the public key in the Certificate message. This proves that the server owns the private key corresponding to that Certificate. Yet another weakness of TLS 1.2 is that not all parts of the handshake were included in this message, which was fixed in TLS 1.3.
3. **Finished**
   . At the end of the TLS handshake, both client and server authenticate the messages sent so far in the
   *Finished*
   message. This authenticates the whole handshake, and is important because any of the TLS messages could have been tampered with on the network, potentially in an attempt to downgrade the connection to use weaker cipher suites.

  
  
In the PCAP dumps, you can see that both client and server send the
*Finished*
messages just before switching over to sending encrypted HTTP. The TLS 1.3 spec says that this verification data is calculated as follows:
  
  
`verify_data = HMAC(finished_key, Transcript-Hash(Handshake Context, Certificate*, CertificateVerify*))`
  
  

* The
  `HMAC`
  function uses the last algorithm specified in the agreed cipher suite, usually SHA256 or SHA384.
* The
  `finished_key`
  is the relevant handshake\_traffic\_secret, the
  `CLIENT_HANDSHAKE_TRAFFIC_SECRET`
  seen in the keylogfile.txt in the case for the client's
  *Finished*
  .
* The
  `Transcript-Hash`
  function works by concatenating together TLS messages (not including record layer headers) and hashing the result using the hash algorithm in the cipher suite.

  
  
In this challenge, we've included a PCAP dump of a connection, up until the point that the client sends its
*ChangeCipherSpec*
and
*Finished*
messages. Fill in the blanks in the "client\_finished.py" script to calculate what the
`verify_data`
in the Client
*Finished*
message should look like, and submit that as your answer.
  
  
**Challenge files:**
  
-
[client\_finished.py](/static/challenges/client_finished_7be8188c90a19caa197cdc07982f17cb.py)
  
-
[keylogfile.txt](/static/challenges/keylogfile_8f26cf82ed35e28b7c8151bbb764f267.txt)
  
-
[no-finished-tls3.cryptohack.org.pcapng](/static/challenges/no-finished-tls3_642a73844a64e902ef6c8564972e98ca.cryptohack.org.pcapng)
  
  
**Resources:**
  
-
[RFC 8446 - The Transport Layer Security (TLS) Protocol Version 1.3](https://datatracker.ietf.org/doc/rfc8446/)
  
-
[The Illustrated TLS 1.3 connection](https://tls13.xargs.org/)
  
-
[NSS Key Log Format](https://web.archive.org/web/20230322192727/https://firefox-source-docs.mozilla.org/security/nss/legacy/key_log_format/index.html)
