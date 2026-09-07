# littlefs

| Property | Value |
| :--- | :--- |
| **Category** | `misc` |
| **Points** | `500` |
| **Author** | simen |
| **Solves** | 0 |

## 📝 Description

I found this device with a NOR flash to that just prints out the flag.
Unfortunately, I could not read the terminal output.

However, I was able to connect my logic analyser. That is a tool that can record the communication between different components in the device.
You can open the `.logicdata` file using Saleae Logic.
To make the recording, channel 0 was connected to MOSI, channel 1 to CS, channel 2 to SCK and channel 3 to MISO.


## 📦 Files & Resources

| File / Resource | Source | Status | Local Path / URL |
| :--- | :--- | :--- | :--- |
| `misc_littlefs.tar.gz` | `platform_attachment` | ✅ Downloaded | [misc_littlefs.tar.gz](misc_littlefs.tar.gz) |

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
