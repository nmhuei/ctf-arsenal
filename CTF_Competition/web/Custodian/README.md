# Custodian

| Property | Value |
| :--- | :--- |
| **Category** | `web` |
| **Points** | `233` |
| **Author** | fg0x0 |
| **Solves** | 52 |

## 🔌 Connection / Service
- URL: [https://custodian-4gyrjvn4.challenge.2026.haruulzangi.mn](https://custodian-4gyrjvn4.challenge.2026.haruulzangi.mn)

## 📝 Description

Half the traffic on this node is human and half is not, so the node trusts
neither. Every request to a counterpart surface carries a Parity Signature.
The scheme is published. The node key is not.

Behind the signature sits the custodian: the runtime that decides what a
counterpart is allowed to touch. Agents submit capability policies as
bytecode and the custodian runs them on a tagged-value machine. The tags
exist so that a policy can never turn a number it computed into a handle on
registry memory.

That is the whole security model for every agent on this node, and it is
documented in full at `/docs`. Nothing is hidden from you except the
implementation.

The Registry keeps something above the policy window.

Your terminal is an observer. Observers cannot submit.

> [!CONNECTION]
> https://custodian-4gyrjvn4.challenge.2026.haruulzangi.mn


## 📦 Files & Resources

*No file attachments associated with this challenge.*

### 🔗 External Links in Description

- [https://custodian-4gyrjvn4.challenge.2026.haruulzangi.mn](https://custodian-4gyrjvn4.challenge.2026.haruulzangi.mn) (`generic_url`)

## 🚩 Flag & Solution

- [ ] Solved

```
FLAG{...}
```

### Writeup / Notes

*(Write your solution steps and notes here)*
