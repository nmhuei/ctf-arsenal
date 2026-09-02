When you connect to a website over HTTPS, the first TLS message sent by the server is the ServerHello containing the server TLS certificate. Your browser verifies that the TLS certificate is valid, and if not, will terminate the TLS handshake. Verification includes ensuring that:
  
  

* the name on the certificate matches the domain
* the certificate has not expired
* the certificate is ultimately signed (via a "chain of trust") by a root key of a Certificate Authority (CA) that's trusted by your browser or operating system

  
  
Since CAs have the power to sign any certificate, the security of the internet depends upon these organisations to issue TLS certificates to the correct people: they must only issue certificates to the real domain owners. However with Windows trusting root certificates from over 100 organisations by default, there's a number of opportunities for hackers, politics, or incompetence to break the whole model. If you could trick just a single CA to issue you a certificate for microsoft.com, you could use the corresponding private key to sign malware and bypass trust controls on Windows. CAs are strongly incentivised to be careful since their business depends upon people trusting them, however in practice they have failed several times.
  
  
In 2011
[Comodo CA was compromised](https://arstechnica.com/information-technology/2011/03/independent-iranian-hacker-claims-responsibility-for-comodo-hack/)
and the hacker was able to issue certificates for Gmail and other services. In 2016,
[Symantec was found](https://security.googleblog.com/2015/10/sustaining-digital-certificate-security.html)
to have issued over 150 certificates without the domain owner's knowledge, as well as 2400 certificates for domains that were never registered.
  
  
Due to such events, together with the fact that fraudulent certificates can take a long time to be discovered, since 2018 Certificate Transparency has been enforced by Google Chrome. Every CA must publish all certificates that they issue to a log, which anyone can search.
  
  
Attached is an RSA public key in PEM format. Find the subdomain of cryptohack.org which uses these parameters in its TLS certificate, and visit that subdomain to obtain the flag.
  
  
**Challenge files:**
  
-
[transparency.pem](/static/challenges/transparency_afff0345c6f99bf80eab5895458d8eab.pem)
