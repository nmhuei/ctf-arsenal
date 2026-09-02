#!/usr/local/bin/python3
from picklescan.scanner import scan_pickle_bytes, SafetyLevel
import modelscan.settings
import modelscan.modelscan
import fickling
import base64
import pickle
import io

open('/tmp/malicious.pkl', 'wb').write(bytes.fromhex(input('one pickle > ')))

# setup stolen from jailCTF 2025 "modelscanjail"
scan = modelscan.modelscan.ModelScan(settings=modelscan.settings.DEFAULT_SETTINGS)
result = scan.scan('/tmp/malicious.pkl')
if result['issues'] or result['errors']:
    print('no')
    exit()

# setup stolen from ImaginaryCTF Round 39 "Safe Pickle"
# original bug is patched now though :)
result = scan_pickle_bytes(open('/tmp/malicious.pkl', 'rb'), 1337)
if (
    result.scan_err
    or result.issues_count > 0
    or not all([g.safety == SafetyLevel.Innocuous for g in result.globals])
):
    print("Dangerous pickle!")
    exit()

# lets check with fickling, just in case ...
if not fickling.is_likely_safe('/tmp/malicious.pkl'):
    print('malicious pickle!!!')
    exit()

pickle.load(open('/tmp/malicious.pkl', 'rb'))

