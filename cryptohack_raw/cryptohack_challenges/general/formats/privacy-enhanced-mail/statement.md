As we've seen in the encoding section, cryptography involves dealing with data in a wide variety of formats: big integers, raw bytes, hex strings and more. A few structured formats have been standardised to help send and receive cryptographic data. It helps to be able to recognise and manipulate these common data formats.
  
  
PEM is a popular format for sending keys, certificates, and other cryptographic material. It looks like:
  
  

-----BEGIN RSA PUBLIC KEY-----
  
MIIBCgKC...
*(a whole bunch of base64)*
  
-----END RSA PUBLIC KEY-----
  
  
It wraps base64-encoded data by a one-line header and footer to indicate how to parse the data within. Perhaps unexpectedly, it's important for there to be the correct number of hyphens in the header and footer, otherwise cryptographic tools won't be able to recognise the file.
  
  
The data that gets base64-encoded is DER-encoded ASN.1 values. Confused? The resources linked below have more information about what these acronyms mean but the complexity is there for historical reasons and going too deep into the details may drive you insane.
  
  
Extract the private key
*d*
as a decimal integer from this PEM-formatted RSA key.
  
  


There are two main approaches for solving this challenge. The data in the certificate can be read with the openssl command line tool, or in Python using PyCryptodome. We recommend using PyCryptodome: first import the RSA module with
`from Crypto.PublicKey import RSA`
and you can read the key data using
`RSA.importKey()`
.
  
  
**Challenge files:**
  
-
[privacy\_enhanced\_mail.pem](/static/challenges/privacy_enhanced_mail_1f696c053d76a78c2c531bb013a92d4a.pem)
  
  
**Resources:**
  
-
[ASN.1 vs DER vs PEM vs x509 vs PKCS#7 vs ....](https://www.cryptologie.net/article/260/asn1-vs-der-vs-pem-vs-x509-vs-pkcs7-vs/)
  
-
[A Warm Welcome to ASN.1 and DER](https://letsencrypt.org/docs/a-warm-welcome-to-asn1-and-der/)
