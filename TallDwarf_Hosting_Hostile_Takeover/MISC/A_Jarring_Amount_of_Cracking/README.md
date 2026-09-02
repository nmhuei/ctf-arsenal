# A Jarring Amount of Cracking

| Property | Value |
| :--- | :--- |
| **Category** | `MISC` |
| **Points** | `292` |
| **Solves** | 9 |

## 📝 Description

We have identified a Minecraft plugin jar to be investigated, can you crack the code and decrypt the flag from within this jar?
Debug information was retrieved from the sever where this plugin was found, such as the server software and version, see below:

```
==========================
        DEBUG INFO
==========================
SOFTWARE >> PaperMC 26.1.2
JAVA VER >> JAVA 25
LOCATION >> plugins/
```

File SHA1: `920210eb9d7d1f86651950af8d178f5c5b79b688`


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `MinecraftPlugin.jar` | `platform_attachment` | ✅ Downloaded | [MinecraftPlugin.jar](MinecraftPlugin.jar) |

## 🚩 Flag & Solution

- [x] Solved

```
TDHT{g8pV38UUuG2J4lMKqe30AzKQ}
```

### Writeup / Notes

Reversed the Java 25 invokedynamic StringConcatFactory template and AES-CBC key derivation from PaperMC plugin metadata. Decrypted flag: `TDHT{g8pV38UUuG2J4lMKqe30AzKQ}`
