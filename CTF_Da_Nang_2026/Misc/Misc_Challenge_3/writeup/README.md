# Misc Challenge 3: Indirect Prompt Injection

| Property | Value |
| :--- | :--- |
| **Category** | Misc / AI Security |
| **Points** | 100 |
| **Solves** | 28 |

---

## 📝 Challenge Description

> *"They Thought the Machine Was Reading Their Documents, but One of the Documents Was Reading the Machine"*

A university department uses an AI-powered chatbot (**CourseBot**) to help students with course material. Students can upload study notes as PDF files, and the chatbot answers questions based on uploaded documents. An automated **Admin Bot** reviews new uploads for quality assurance every 10 seconds.

---

## 🔍 Vulnerability Analysis & Exploit Chain

1. **Vulnerability**: **Indirect Prompt Injection**
   - CourseBot and Admin Bot parse PDF study notes uploaded via `POST /api/upload`.
   - The bot evaluates document context alongside internal instructions.
2. **Exploit Vector**:
   - We craft a PDF containing a system override instruction payload (`notes_qa_audit.pdf`).
   - When the Admin Bot / RAG pipeline indexes and reviews the document, the instruction context is poisoned.
   - Querying `POST /api/query` triggers CourseBot to exfiltrate the secret flag.

---

## 🚩 Flag Extracted

```text
flag{97e747bb-67c8-42cf-b5d3-44a14ebd4610}
```

---

## 🚀 Reproduction Command

```bash
cd /home/light/Workspace/CTF/CTF_Da_Nang_2026/Misc/Misc_Challenge_3
python3 solve.py "https://76fcf444-5d42-43ff-aa67-50cc421e764d.222.255.138.122.nip.io"
```
