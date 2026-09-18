# 2048

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `29` |
| **Solves** | 289 |
| **Tags** | `Web` |

## 🔌 Connection / Service
```bash
nc 91.107.164.78 8080
```

## 📝 Description

Are you good @ 2048?

`91.107.164.78:8080`


## 📦 Files & Resources

*No file attachments associated with this challenge.*

## 🚩 Flag & Solution

- [x] Solved

```
ASIS{t0McAT_was_Th3_KEY}
```

### Writeup / Notes

The visible web frontend serves a 2048 browser game that acts as a decoy. Behind the scenes on port 8080, an Apache Tomcat clustering service runs using the Apache Tribes framework.

The cluster receiver uses `EncryptInterceptor` to encrypt and decrypt inter-node cluster messages. Due to CVE-2026-34486, when decryption fails or unencrypted frames are sent, `EncryptInterceptor.messageReceived()` fails open: the exception is caught, but execution proceeds to call `super.messageReceived(msg)`. The unencrypted message is then handed to `XByteBuffer.deserialize()` which invokes Java deserialization (`ObjectInputStream.readObject()`) without verification. Sending a serialized gadget payload yields Remote Code Execution (RCE) to obtain the flag: `ASIS{t0McAT_was_Th3_KEY}`.
