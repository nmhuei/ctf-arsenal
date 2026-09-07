# Micro-step 3A

Scope: local data parsing only from apbq-rsa-iv.py and INVENTORY.md. No factorization, decryption, secret recovery, security analysis, network use, or external lookup was performed.

Created:
- INSTANCE.json with keys n, c, hints extracted from the embedded public instance.
- validate_instance.py containing only format, size, and exact source-value checks.

Validation command:

 python3 validate_instance.py

Result: PASS

Validator output:

 PASS: INSTANCE.json format, size, and source-value checks

STEP3A_COMPLETE
