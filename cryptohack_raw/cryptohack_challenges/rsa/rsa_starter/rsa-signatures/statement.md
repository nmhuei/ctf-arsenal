How can you ensure that the person receiving your message knows that you wrote it?
  
  
You've been asked out on a date, and you want to send a message telling them that you'd love to go, however a jealous lover isn't so happy about this.
  
  
When you send your message saying yes, your jealous lover intercepts the message and corrupts it so it now says no!
  
  
We can protect against these attacks by cryptographically signing the message.
  
  
Imagine you write a message

m

m





m
. You encrypt this message with your
**friend's public key**
:

c

=


m


e

0






m

o

d


N

0

c = m^{e\_{0}} \mod N\_{0}





c



=






m











e










0

​







mod






N










0

​

.
  
  
To sign this message, you calculate the hash of the message:

H

(

m

)

H(m)





H

(

m

)
and "encrypt" this with
**your private key**
:

S

=

H

(

m


)


d

1






m

o

d


N

1

S = H(m)^{d\_{1}} \mod N\_{1}





S



=





H

(

m


)











d










1

​







mod






N










1

​

.
  
  


In real cryptosystems, it's
[best practice to use separate keys](https://crypto.stackexchange.com/a/12138)
for encrypting and signing messages.
  
  
Your friend can decrypt the message using
**their private key**
:

m

=


c


d

0






m

o

d


N

0

m = c^{d\_{0}} \mod N\_{0}





m



=






c











d










0

​







mod






N










0

​

. Using your public key they calculate

s

=


S


e

1






m

o

d


N

1

s = S^{e\_{1}} \mod N\_{1}





s



=






S











e










1

​







mod






N










1

​

.
  
  
Now by computing

H

(

m

)

H(m)





H

(

m

)
and comparing it to

s

s





s
:
`assert H(m) == s`
, they can ensure that the message you sent them, is the message that they received! As long as your private key is safe, no one else could have signed this message!
  
  
Sign the flag
`crypto{Immut4ble_m3ssag1ng}`
using your private key and the
`SHA256`
hash function.
  
  


The output of the hash function needs to be converted into a number that can be used with RSA math. Remember the helpful
`bytes_to_long()`
function that can be imported from
`Crypto.Util.number`
.
  
  
**Challenge files:**
  
-
[private.key](/static/challenges/private_0a1880d1fffce9403686130a1f932b10.key)
