package defpackage;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.os.Build;
import android.util.Base64;
import android.util.Log;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Method;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.SecureRandom;
import java.security.spec.RSAKeyGenParameterSpec;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.BitSet;
import java.util.Iterator;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.Executor;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import java.util.zip.Inflater;
import org.json.JSONException;
import org.json.JSONObject;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public abstract class y {
    public static final int[] a = new int[0];
    public static final Object[] b = new Object[0];
    public static final r0 c = new r0(0);
    public static final byte[] d = {112, 114, 111, 0};
    public static final byte[] e = {112, 114, 109, 0};
    public static final byte[] f = {48, 49, 53, 0};
    public static final byte[] g = {48, 49, 48, 0};
    public static final byte[] h = {48, 48, 57, 0};
    public static final byte[] i = {48, 48, 53, 0};
    public static final byte[] j = {48, 48, 49, 0};
    public static final byte[] k = {48, 48, 49, 0};
    public static final byte[] l = {48, 48, 50, 0};
    public static long m;
    public static Method n;

    public static void A(ByteArrayOutputStream byteArrayOutputStream, b0 b0Var) throws IOException {
        int i2 = 0;
        for (Map.Entry entry : b0Var.i.entrySet()) {
            int iIntValue = ((Integer) entry.getKey()).intValue();
            if ((((Integer) entry.getValue()).intValue() & 1) != 0) {
                D(byteArrayOutputStream, iIntValue - i2);
                D(byteArrayOutputStream, 0);
                i2 = iIntValue;
            }
        }
    }

    /* JADX WARN: Code duplicated, block: B:126:0x01c8 A[Catch: all -> 0x01d6, TRY_LEAVE, TryCatch #30 {all -> 0x01d6, blocks: (B:124:0x01bc, B:126:0x01c8, B:135:0x01d9), top: B:248:0x01bc, outer: #30 }] */
    /* JADX WARN: Code duplicated, block: B:135:0x01d9 A[Catch: all -> 0x01d6, TRY_ENTER, TRY_LEAVE, TryCatch #30 {all -> 0x01d6, blocks: (B:124:0x01bc, B:126:0x01c8, B:135:0x01d9), top: B:248:0x01bc, outer: #30 }] */
    /* JADX WARN: Code duplicated, block: B:146:0x01f6  */
    /* JADX WARN: Code duplicated, block: B:150:0x0200  */
    /* JADX WARN: Code duplicated, block: B:151:0x0204  */
    /* JADX WARN: Code duplicated, block: B:159:0x021e A[Catch: all -> 0x0240, TRY_LEAVE, TryCatch #15 {all -> 0x0240, blocks: (B:156:0x0216, B:157:0x0218, B:159:0x021e), top: B:226:0x0216 }] */
    /* JADX WARN: Code duplicated, block: B:200:0x026d  */
    /* JADX WARN: Code duplicated, block: B:203:0x0276  */
    /* JADX WARN: Code duplicated, block: B:208:0x0283 A[ADDED_TO_REGION] */
    /* JADX WARN: Code duplicated, block: B:210:0x0287  */
    /* JADX WARN: Code duplicated, block: B:250:0x0208 A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:252:0x01b7 A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /* JADX WARN: Code duplicated, block: B:257:0x0223 A[SYNTHETIC] */
    /* JADX WARN: Multi-variable type inference failed */
    public static void B(Context context, Executor executor, s0 s0Var, boolean z) {
        char c2;
        FileInputStream fileInputStreamA;
        byte[] bArr;
        b0[] b0VarArrU;
        s0 s0Var2;
        b0[] b0VarArr;
        byte[] bArr2;
        byte[] bArr3;
        boolean z2;
        ByteArrayInputStream byteArrayInputStream;
        FileOutputStream fileOutputStream;
        Throwable th;
        byte[] bArr4;
        int i2;
        ByteArrayOutputStream byteArrayOutputStream;
        int i3;
        a0 a0Var;
        boolean z3;
        boolean z4;
        Context applicationContext = context.getApplicationContext();
        String packageName = applicationContext.getPackageName();
        ApplicationInfo applicationInfo = applicationContext.getApplicationInfo();
        AssetManager assets = applicationContext.getAssets();
        String name = new File(applicationInfo.sourceDir).getName();
        try {
            PackageInfo packageInfo = context.getPackageManager().getPackageInfo(packageName, 0);
            File filesDir = context.getFilesDir();
            if (!z) {
                File file = new File(filesDir, "profileinstaller_profileWrittenFor_lastUpdateTime.dat");
                if (file.exists()) {
                    try {
                        DataInputStream dataInputStream = new DataInputStream(new FileInputStream(file));
                        try {
                            long j2 = dataInputStream.readLong();
                            dataInputStream.close();
                            z4 = j2 == packageInfo.lastUpdateTime;
                            if (z4) {
                                s0Var.b(2, null);
                            }
                        } catch (Throwable th2) {
                            try {
                                dataInputStream.close();
                                throw th2;
                            } catch (Throwable th3) {
                                th2.addSuppressed(th3);
                                throw th2;
                            }
                        }
                    } catch (IOException unused) {
                        z4 = false;
                    }
                } else {
                    z4 = false;
                }
                if (z4) {
                    Log.d("ProfileInstaller", "Skipping profile installation for " + context.getPackageName());
                    a1.c(context, false);
                    return;
                }
            }
            Log.d("ProfileInstaller", "Installing profile for " + context.getPackageName());
            File file2 = new File(new File("/data/misc/profiles/cur/0", packageName), "primary.prof");
            a0 a0Var2 = new a0(assets, executor, s0Var, name, file2);
            byte[] bArr5 = a0Var2.c;
            if (bArr5 == null) {
                a0Var2.b(3, Integer.valueOf(Build.VERSION.SDK_INT));
            } else {
                try {
                    try {
                        if (file2.exists()) {
                            if (!file2.canWrite()) {
                                a0Var2.b(4, null);
                            }
                            if (z2 || !z) {
                                z3 = 0;
                            } else {
                                z3 = c2;
                            }
                            a1.c(context, z3);
                        }
                        try {
                            file2.createNewFile();
                        } catch (IOException unused2) {
                            c2 = 1;
                            a0Var2.b(4, null);
                            z2 = false;
                        }
                        fileInputStreamA = a0Var2.a(assets, "dexopt/baseline.prof");
                    } catch (FileNotFoundException e2) {
                        s0Var.b(6, e2);
                        fileInputStreamA = null;
                    } catch (IOException e3) {
                        s0Var.b(7, e3);
                        fileInputStreamA = null;
                    }
                    if (fileInputStreamA != null) {
                        try {
                            if (!Arrays.equals(bArr, o(fileInputStreamA, 4))) {
                                throw new IllegalStateException("Invalid magic");
                            }
                            b0VarArrU = u(fileInputStreamA, o(fileInputStreamA, 4), a0Var2.e);
                            try {
                                fileInputStreamA.close();
                            } catch (IOException e4) {
                                s0Var.b(7, e4);
                            }
                            a0Var2.g = b0VarArrU;
                        } catch (IOException e5) {
                            s0Var.b(7, e5);
                            try {
                                fileInputStreamA.close();
                            } catch (IOException e6) {
                                s0Var.b(7, e6);
                            }
                            b0VarArrU = null;
                        } catch (IllegalStateException e7) {
                            s0Var.b(8, e7);
                            fileInputStreamA.close();
                            b0VarArrU = null;
                        }
                    }
                    b0[] b0VarArr2 = a0Var2.g;
                    if (b0VarArr2 != null && (i3 = Build.VERSION.SDK_INT) <= 34) {
                        switch (i3) {
                            case 31:
                            case 32:
                            case 33:
                            case 34:
                                try {
                                    FileInputStream fileInputStreamA2 = a0Var2.a(assets, "dexopt/baseline.profm");
                                    if (fileInputStreamA2 != null) {
                                        try {
                                            if (!Arrays.equals(e, o(fileInputStreamA2, 4))) {
                                                throw new IllegalStateException("Invalid magic");
                                            }
                                            a0Var2.g = r(fileInputStreamA2, o(fileInputStreamA2, 4), bArr5, b0VarArr2);
                                            fileInputStreamA2.close();
                                            a0Var = a0Var2;
                                        } catch (Throwable th4) {
                                            try {
                                                fileInputStreamA2.close();
                                                throw th4;
                                            } catch (Throwable th5) {
                                                th4.addSuppressed(th5);
                                                throw th4;
                                            }
                                        }
                                    } else {
                                        if (fileInputStreamA2 != null) {
                                            fileInputStreamA2.close();
                                        }
                                        a0Var = null;
                                    }
                                } catch (FileNotFoundException e8) {
                                    s0Var.b(9, e8);
                                } catch (IOException e9) {
                                    s0Var.b(7, e9);
                                } catch (IllegalStateException e10) {
                                    a0Var2.g = null;
                                    s0Var.b(8, e10);
                                }
                                if (a0Var != null) {
                                    a0Var2 = a0Var;
                                    break;
                                }
                            default:
                                s0Var2 = a0Var2.b;
                                b0VarArr = a0Var2.g;
                                bArr2 = a0Var2.c;
                                if (b0VarArr != null && bArr2 != null) {
                                    if (a0Var2.f) {
                                        throw new IllegalStateException("This device doesn't support aot. Did you call deviceSupportsAotProfile()?");
                                    }
                                    try {
                                        byteArrayOutputStream = new ByteArrayOutputStream();
                                        try {
                                            byteArrayOutputStream.write(bArr);
                                            byteArrayOutputStream.write(bArr2);
                                            if (x(byteArrayOutputStream, bArr2, b0VarArr)) {
                                                a0Var2.h = byteArrayOutputStream.toByteArray();
                                                byteArrayOutputStream.close();
                                                a0Var2.g = null;
                                            } else {
                                                s0Var2.b(5, null);
                                                a0Var2.g = null;
                                                byteArrayOutputStream.close();
                                            }
                                        } catch (Throwable th6) {
                                            try {
                                                byteArrayOutputStream.close();
                                                throw th6;
                                            } catch (Throwable th7) {
                                                th6.addSuppressed(th7);
                                                throw th6;
                                            }
                                        }
                                    } catch (IOException e11) {
                                        s0Var2.b(7, e11);
                                    } catch (IllegalStateException e12) {
                                        s0Var2.b(8, e12);
                                    }
                                }
                                bArr3 = a0Var2.h;
                                if (bArr3 != null) {
                                    z2 = false;
                                    c2 = 1;
                                } else {
                                    try {
                                        if (a0Var2.f) {
                                            throw new IllegalStateException("This device doesn't support aot. Did you call deviceSupportsAotProfile()?");
                                        }
                                        try {
                                            try {
                                                byteArrayInputStream = new ByteArrayInputStream(bArr3);
                                                try {
                                                    fileOutputStream = new FileOutputStream(a0Var2.d);
                                                    try {
                                                        try {
                                                            bArr4 = new byte[512];
                                                            while (true) {
                                                                i2 = byteArrayInputStream.read(bArr4);
                                                                if (i2 > 0) {
                                                                    fileOutputStream.write(bArr4, 0, i2);
                                                                } else {
                                                                    c2 = 1;
                                                                    try {
                                                                        a0Var2.b(1, null);
                                                                        fileOutputStream.close();
                                                                        byteArrayInputStream.close();
                                                                        a0Var2.h = null;
                                                                        a0Var2.g = null;
                                                                        z2 = true;
                                                                    } catch (Throwable th8) {
                                                                        th = th8;
                                                                    }
                                                                }
                                                                th = th;
                                                                try {
                                                                    fileOutputStream.close();
                                                                    throw th;
                                                                } catch (Throwable th9) {
                                                                    th.addSuppressed(th9);
                                                                    throw th;
                                                                }
                                                            }
                                                        } catch (Throwable th10) {
                                                            th = th10;
                                                            Throwable th11 = th;
                                                            try {
                                                                byteArrayInputStream.close();
                                                                throw th11;
                                                            } catch (Throwable th12) {
                                                                th11.addSuppressed(th12);
                                                                throw th11;
                                                            }
                                                        }
                                                    } catch (Throwable th13) {
                                                        th = th13;
                                                    }
                                                } catch (Throwable th14) {
                                                    th = th14;
                                                }
                                            } catch (FileNotFoundException e13) {
                                                e = e13;
                                                a0Var2.b(6, e);
                                                a0Var2.h = null;
                                                a0Var2.g = null;
                                                z2 = false;
                                            } catch (IOException e14) {
                                                e = e14;
                                                a0Var2.b(7, e);
                                                a0Var2.h = null;
                                                a0Var2.g = null;
                                                z2 = false;
                                            }
                                        } catch (FileNotFoundException e15) {
                                            e = e15;
                                            c2 = 1;
                                            a0Var2.b(6, e);
                                            a0Var2.h = null;
                                            a0Var2.g = null;
                                            z2 = false;
                                        } catch (IOException e16) {
                                            e = e16;
                                            c2 = 1;
                                            a0Var2.b(7, e);
                                            a0Var2.h = null;
                                            a0Var2.g = null;
                                            z2 = false;
                                        }
                                    } catch (Throwable th15) {
                                        a0Var2.h = null;
                                        a0Var2.g = null;
                                        throw th15;
                                    }
                                }
                                if (z2) {
                                    l(packageInfo, filesDir);
                                }
                                if (z2) {
                                    z3 = 0;
                                } else {
                                    z3 = 0;
                                }
                                a1.c(context, z3);
                        }
                    }
                    s0Var2 = a0Var2.b;
                    b0VarArr = a0Var2.g;
                    bArr2 = a0Var2.c;
                    if (b0VarArr != null) {
                        if (a0Var2.f) {
                            throw new IllegalStateException("This device doesn't support aot. Did you call deviceSupportsAotProfile()?");
                        }
                        byteArrayOutputStream = new ByteArrayOutputStream();
                        byteArrayOutputStream.write(bArr);
                        byteArrayOutputStream.write(bArr2);
                        if (x(byteArrayOutputStream, bArr2, b0VarArr)) {
                            s0Var2.b(5, null);
                            a0Var2.g = null;
                            byteArrayOutputStream.close();
                        } else {
                            a0Var2.h = byteArrayOutputStream.toByteArray();
                            byteArrayOutputStream.close();
                            a0Var2.g = null;
                        }
                    }
                    bArr3 = a0Var2.h;
                    if (bArr3 != null) {
                        if (a0Var2.f) {
                            throw new IllegalStateException("This device doesn't support aot. Did you call deviceSupportsAotProfile()?");
                        }
                        byteArrayInputStream = new ByteArrayInputStream(bArr3);
                        fileOutputStream = new FileOutputStream(a0Var2.d);
                        bArr4 = new byte[512];
                        while (true) {
                            i2 = byteArrayInputStream.read(bArr4);
                            if (i2 > 0) {
                                fileOutputStream.write(bArr4, 0, i2);
                            } else {
                                c2 = 1;
                                a0Var2.b(1, null);
                                fileOutputStream.close();
                                byteArrayInputStream.close();
                                a0Var2.h = null;
                                a0Var2.g = null;
                                z2 = true;
                            }
                            th = th;
                            fileOutputStream.close();
                            throw th;
                        }
                    }
                    z2 = false;
                    c2 = 1;
                    if (z2) {
                        l(packageInfo, filesDir);
                    }
                    if (z2) {
                        z3 = 0;
                    } else {
                        z3 = 0;
                    }
                    a1.c(context, z3);
                } catch (Throwable th16) {
                    try {
                        fileInputStreamA.close();
                        throw th16;
                    } catch (IOException e17) {
                        s0Var.b(7, e17);
                        throw th16;
                    }
                }
                a0Var2.f = true;
                bArr = d;
                c2 = '\b';
            }
            c2 = 1;
            z2 = false;
            if (z2) {
                z3 = 0;
            } else {
                z3 = 0;
            }
            a1.c(context, z3);
        } catch (PackageManager.NameNotFoundException e18) {
            s0Var.b(7, e18);
            a1.c(context, false);
        }
    }

    public static void C(ByteArrayOutputStream byteArrayOutputStream, long j2, int i2) throws IOException {
        byte[] bArr = new byte[i2];
        for (int i3 = 0; i3 < i2; i3++) {
            bArr[i3] = (byte) ((j2 >> (i3 * 8)) & 255);
        }
        byteArrayOutputStream.write(bArr);
    }

    public static void D(ByteArrayOutputStream byteArrayOutputStream, int i2) throws IOException {
        C(byteArrayOutputStream, i2, 2);
    }

    public static boolean a(Object obj, Object obj2) {
        if (obj == null) {
            return obj2 == null;
        }
        return obj.equals(obj2);
    }

    public static final int b(int[] iArr, int i2, int i3) {
        int i4 = i2 - 1;
        int i5 = 0;
        while (i5 <= i4) {
            int i6 = (i5 + i4) >>> 1;
            int i7 = iArr[i6];
            if (i7 < i3) {
                i5 = i6 + 1;
            } else {
                if (i7 <= i3) {
                    return i6;
                }
                i4 = i6 - 1;
            }
        }
        return ~i5;
    }

    public static byte[] f(byte[] bArr) {
        Deflater deflater = new Deflater(1);
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        try {
            DeflaterOutputStream deflaterOutputStream = new DeflaterOutputStream(byteArrayOutputStream, deflater);
            try {
                deflaterOutputStream.write(bArr);
                deflaterOutputStream.close();
                deflater.end();
                return byteArrayOutputStream.toByteArray();
            } catch (Throwable th) {
                try {
                    deflaterOutputStream.close();
                } catch (Throwable th2) {
                    th.addSuppressed(th2);
                }
                throw th;
            }
        } catch (Throwable th3) {
            deflater.end();
            throw th3;
        }
    }

    public static byte[] g(b0[] b0VarArr, byte[] bArr) throws IOException {
        int length = 0;
        for (b0 b0Var : b0VarArr) {
            length += ((((b0Var.g * 2) + 7) & (-8)) / 8) + (b0Var.e * 2) + k(b0Var.a, b0Var.b, bArr).getBytes(StandardCharsets.UTF_8).length + 16 + b0Var.f;
        }
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream(length);
        if (Arrays.equals(bArr, h)) {
            for (b0 b0Var2 : b0VarArr) {
                y(byteArrayOutputStream, b0Var2, k(b0Var2.a, b0Var2.b, bArr));
                A(byteArrayOutputStream, b0Var2);
                int[] iArr = b0Var2.h;
                int length2 = iArr.length;
                int i2 = 0;
                int i3 = 0;
                while (i2 < length2) {
                    int i4 = iArr[i2];
                    D(byteArrayOutputStream, i4 - i3);
                    i2++;
                    i3 = i4;
                }
                z(byteArrayOutputStream, b0Var2);
            }
        } else {
            for (b0 b0Var3 : b0VarArr) {
                y(byteArrayOutputStream, b0Var3, k(b0Var3.a, b0Var3.b, bArr));
            }
            for (b0 b0Var4 : b0VarArr) {
                A(byteArrayOutputStream, b0Var4);
                int[] iArr2 = b0Var4.h;
                int length3 = iArr2.length;
                int i5 = 0;
                int i6 = 0;
                while (i5 < length3) {
                    int i7 = iArr2[i5];
                    D(byteArrayOutputStream, i7 - i6);
                    i5++;
                    i6 = i7;
                }
                z(byteArrayOutputStream, b0Var4);
            }
        }
        if (byteArrayOutputStream.size() == length) {
            return byteArrayOutputStream.toByteArray();
        }
        throw new IllegalStateException("The bytes saved do not match expectation. actual=" + byteArrayOutputStream.size() + " expected=" + length);
    }

    public static boolean h(File file) {
        if (!file.isDirectory()) {
            file.delete();
            return true;
        }
        File[] fileArrListFiles = file.listFiles();
        if (fileArrListFiles == null) {
            return false;
        }
        boolean z = true;
        for (File file2 : fileArrListFiles) {
            z = h(file2) && z;
        }
        return z;
    }

    public static String i(Object obj, String str, String str2) {
        try {
            return new JSONObject().put("id", obj).put("error", new JSONObject().put("code", str).put("message", str2)).toString();
        } catch (JSONException e2) {
            throw new IllegalStateException(e2);
        }
    }

    public static x j() {
        try {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
            keyPairGenerator.initialize(new RSAKeyGenParameterSpec(3072, RSAKeyGenParameterSpec.F4), new SecureRandom());
            KeyPair keyPairGenerateKeyPair = keyPairGenerator.generateKeyPair();
            return new x(Base64.encodeToString(keyPairGenerateKeyPair.getPrivate().getEncoded(), 2), Base64.encodeToString(keyPairGenerateKeyPair.getPublic().getEncoded(), 2));
        } catch (Exception e2) {
            throw new IllegalStateException("Unable to generate device keys", e2);
        }
    }

    public static String k(String str, String str2, byte[] bArr) {
        byte[] bArr2 = j;
        boolean zEquals = Arrays.equals(bArr, bArr2);
        byte[] bArr3 = i;
        Object obj = (zEquals || Arrays.equals(bArr, bArr3)) ? ":" : "!";
        if (str.length() <= 0) {
            if ("!".equals(obj)) {
                return str2.replace(":", "!");
            }
            if (":".equals(obj)) {
                return str2.replace("!", ":");
            }
        } else {
            if (str2.equals("classes.dex")) {
                return str;
            }
            if (str2.contains("!") || str2.contains(":")) {
                if ("!".equals(obj)) {
                    return str2.replace(":", "!");
                }
                if (":".equals(obj)) {
                    return str2.replace("!", ":");
                }
            } else if (!str2.endsWith(".apk")) {
                StringBuilder sb = new StringBuilder();
                sb.append(str);
                sb.append((Arrays.equals(bArr, bArr2) || Arrays.equals(bArr, bArr3)) ? ":" : "!");
                sb.append(str2);
                return sb.toString();
            }
        }
        return str2;
    }

    public static void l(PackageInfo packageInfo, File file) {
        try {
            DataOutputStream dataOutputStream = new DataOutputStream(new FileOutputStream(new File(file, "profileinstaller_profileWrittenFor_lastUpdateTime.dat")));
            try {
                dataOutputStream.writeLong(packageInfo.lastUpdateTime);
                dataOutputStream.close();
            } catch (Throwable th) {
                try {
                    dataOutputStream.close();
                } catch (Throwable th2) {
                    th.addSuppressed(th2);
                }
                throw th;
            }
        } catch (IOException unused) {
        }
    }

    public static byte[] o(InputStream inputStream, int i2) throws IOException {
        byte[] bArr = new byte[i2];
        int i3 = 0;
        while (i3 < i2) {
            int i4 = inputStream.read(bArr, i3, i2 - i3);
            if (i4 < 0) {
                throw new IllegalStateException("Not enough bytes to read: " + i2);
            }
            i3 += i4;
        }
        return bArr;
    }

    public static int[] p(ByteArrayInputStream byteArrayInputStream, int i2) {
        int[] iArr = new int[i2];
        int iV = 0;
        for (int i3 = 0; i3 < i2; i3++) {
            iV += (int) v(byteArrayInputStream, 2);
            iArr[i3] = iV;
        }
        return iArr;
    }

    public static byte[] q(FileInputStream fileInputStream, int i2, int i3) {
        Inflater inflater = new Inflater();
        try {
            byte[] bArr = new byte[i3];
            byte[] bArr2 = new byte[2048];
            int i4 = 0;
            int iInflate = 0;
            while (!inflater.finished() && !inflater.needsDictionary() && i4 < i2) {
                int i5 = fileInputStream.read(bArr2);
                if (i5 < 0) {
                    throw new IllegalStateException("Invalid zip data. Stream ended after $totalBytesRead bytes. Expected " + i2 + " bytes");
                }
                inflater.setInput(bArr2, 0, i5);
                try {
                    iInflate += inflater.inflate(bArr, iInflate, i3 - iInflate);
                    i4 += i5;
                } catch (DataFormatException e2) {
                    throw new IllegalStateException(e2.getMessage());
                }
            }
            if (i4 == i2) {
                if (!inflater.finished()) {
                    throw new IllegalStateException("Inflater did not finish");
                }
                inflater.end();
                return bArr;
            }
            throw new IllegalStateException("Didn't read enough bytes during decompression. expected=" + i2 + " actual=" + i4);
        } catch (Throwable th) {
            inflater.end();
            throw th;
        }
    }

    public static b0[] r(FileInputStream fileInputStream, byte[] bArr, byte[] bArr2, b0[] b0VarArr) throws IOException {
        byte[] bArr3 = k;
        if (!Arrays.equals(bArr, bArr3)) {
            if (!Arrays.equals(bArr, l)) {
                throw new IllegalStateException("Unsupported meta version");
            }
            int iV = (int) v(fileInputStream, 2);
            byte[] bArrQ = q(fileInputStream, (int) v(fileInputStream, 4), (int) v(fileInputStream, 4));
            if (fileInputStream.read() > 0) {
                throw new IllegalStateException("Content found after the end of file");
            }
            ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bArrQ);
            try {
                b0[] b0VarArrT = t(byteArrayInputStream, bArr2, iV, b0VarArr);
                byteArrayInputStream.close();
                return b0VarArrT;
            } catch (Throwable th) {
                try {
                    byteArrayInputStream.close();
                } catch (Throwable th2) {
                    th.addSuppressed(th2);
                }
                throw th;
            }
        }
        if (Arrays.equals(f, bArr2)) {
            throw new IllegalStateException("Requires new Baseline Profile Metadata. Please rebuild the APK with Android Gradle Plugin 7.2 Canary 7 or higher");
        }
        if (!Arrays.equals(bArr, bArr3)) {
            throw new IllegalStateException("Unsupported meta version");
        }
        int iV2 = (int) v(fileInputStream, 1);
        byte[] bArrQ2 = q(fileInputStream, (int) v(fileInputStream, 4), (int) v(fileInputStream, 4));
        if (fileInputStream.read() > 0) {
            throw new IllegalStateException("Content found after the end of file");
        }
        ByteArrayInputStream byteArrayInputStream2 = new ByteArrayInputStream(bArrQ2);
        try {
            b0[] b0VarArrS = s(byteArrayInputStream2, iV2, b0VarArr);
            byteArrayInputStream2.close();
            return b0VarArrS;
        } catch (Throwable th3) {
            try {
                byteArrayInputStream2.close();
            } catch (Throwable th4) {
                th3.addSuppressed(th4);
            }
            throw th3;
        }
    }

    public static b0[] s(ByteArrayInputStream byteArrayInputStream, int i2, b0[] b0VarArr) {
        if (byteArrayInputStream.available() == 0) {
            return new b0[0];
        }
        if (i2 != b0VarArr.length) {
            throw new IllegalStateException("Mismatched number of dex files found in metadata");
        }
        String[] strArr = new String[i2];
        int[] iArr = new int[i2];
        for (int i3 = 0; i3 < i2; i3++) {
            int iV = (int) v(byteArrayInputStream, 2);
            iArr[i3] = (int) v(byteArrayInputStream, 2);
            strArr[i3] = new String(o(byteArrayInputStream, iV), StandardCharsets.UTF_8);
        }
        for (int i4 = 0; i4 < i2; i4++) {
            b0 b0Var = b0VarArr[i4];
            if (!b0Var.b.equals(strArr[i4])) {
                throw new IllegalStateException("Order of dexfiles in metadata did not match baseline");
            }
            int i5 = iArr[i4];
            b0Var.e = i5;
            b0Var.h = p(byteArrayInputStream, i5);
        }
        return b0VarArr;
    }

    public static b0[] t(ByteArrayInputStream byteArrayInputStream, byte[] bArr, int i2, b0[] b0VarArr) throws IOException {
        if (byteArrayInputStream.available() == 0) {
            return new b0[0];
        }
        if (i2 != b0VarArr.length) {
            throw new IllegalStateException("Mismatched number of dex files found in metadata");
        }
        for (int i3 = 0; i3 < i2; i3++) {
            v(byteArrayInputStream, 2);
            String str = new String(o(byteArrayInputStream, (int) v(byteArrayInputStream, 2)), StandardCharsets.UTF_8);
            long jV = v(byteArrayInputStream, 4);
            int iV = (int) v(byteArrayInputStream, 2);
            b0 b0Var = null;
            if (b0VarArr.length > 0) {
                int iIndexOf = str.indexOf("!");
                if (iIndexOf < 0) {
                    iIndexOf = str.indexOf(":");
                }
                String strSubstring = iIndexOf > 0 ? str.substring(iIndexOf + 1) : str;
                for (int i4 = 0; i4 < b0VarArr.length; i4++) {
                    if (b0VarArr[i4].b.equals(strSubstring)) {
                        b0Var = b0VarArr[i4];
                        break;
                    }
                }
            }
            if (b0Var == null) {
                throw new IllegalStateException("Missing profile key: ".concat(str));
            }
            b0Var.d = jV;
            int[] iArrP = p(byteArrayInputStream, iV);
            if (Arrays.equals(bArr, j)) {
                b0Var.e = iV;
                b0Var.h = iArrP;
            }
        }
        return b0VarArr;
    }

    public static b0[] u(FileInputStream fileInputStream, byte[] bArr, String str) throws IOException {
        if (!Arrays.equals(bArr, g)) {
            throw new IllegalStateException("Unsupported version");
        }
        int iV = (int) v(fileInputStream, 1);
        byte[] bArrQ = q(fileInputStream, (int) v(fileInputStream, 4), (int) v(fileInputStream, 4));
        if (fileInputStream.read() > 0) {
            throw new IllegalStateException("Content found after the end of file");
        }
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bArrQ);
        try {
            b0[] b0VarArrW = w(byteArrayInputStream, str, iV);
            byteArrayInputStream.close();
            return b0VarArrW;
        } catch (Throwable th) {
            try {
                byteArrayInputStream.close();
            } catch (Throwable th2) {
                th.addSuppressed(th2);
            }
            throw th;
        }
    }

    public static long v(InputStream inputStream, int i2) throws IOException {
        byte[] bArrO = o(inputStream, i2);
        long j2 = 0;
        for (int i3 = 0; i3 < i2; i3++) {
            j2 += ((long) (bArrO[i3] & 255)) << (i3 * 8);
        }
        return j2;
    }

    public static b0[] w(ByteArrayInputStream byteArrayInputStream, String str, int i2) throws IOException {
        int i3 = 0;
        if (byteArrayInputStream.available() == 0) {
            return new b0[0];
        }
        b0[] b0VarArr = new b0[i2];
        for (int i4 = 0; i4 < i2; i4++) {
            int iV = (int) v(byteArrayInputStream, 2);
            int iV2 = (int) v(byteArrayInputStream, 2);
            b0VarArr[i4] = new b0(str, new String(o(byteArrayInputStream, iV), StandardCharsets.UTF_8), v(byteArrayInputStream, 4), iV2, (int) v(byteArrayInputStream, 4), (int) v(byteArrayInputStream, 4), new int[iV2], new TreeMap());
        }
        int i5 = 0;
        while (i5 < i2) {
            b0 b0Var = b0VarArr[i5];
            int iAvailable = byteArrayInputStream.available();
            int i6 = b0Var.f;
            int i7 = b0Var.g;
            TreeMap treeMap = b0Var.i;
            int i8 = iAvailable - i6;
            int iV3 = i3;
            while (byteArrayInputStream.available() > i8) {
                iV3 += (int) v(byteArrayInputStream, 2);
                treeMap.put(Integer.valueOf(iV3), 1);
                int iV4 = (int) v(byteArrayInputStream, 2);
                while (iV4 > 0) {
                    v(byteArrayInputStream, 2);
                    int iV5 = (int) v(byteArrayInputStream, 1);
                    if (iV5 != 6 && iV5 != 7) {
                        while (iV5 > 0) {
                            v(byteArrayInputStream, 1);
                            int i9 = i3;
                            int i10 = i5;
                            for (int iV6 = (int) v(byteArrayInputStream, 1); iV6 > 0; iV6--) {
                                v(byteArrayInputStream, 2);
                            }
                            iV5--;
                            i3 = i9;
                            i5 = i10;
                        }
                    }
                    iV4--;
                    i3 = i3;
                    i5 = i5;
                }
            }
            int i11 = i3;
            int i12 = i5;
            if (byteArrayInputStream.available() != i8) {
                throw new IllegalStateException("Read too much data during profile line parse");
            }
            b0Var.h = p(byteArrayInputStream, b0Var.e);
            BitSet bitSetValueOf = BitSet.valueOf(o(byteArrayInputStream, (((i7 * 2) + 7) & (-8)) / 8));
            for (int i13 = i11; i13 < i7; i13++) {
                int i14 = bitSetValueOf.get(i13) ? 2 : i11;
                if (bitSetValueOf.get(i13 + i7)) {
                    i14 |= 4;
                }
                if (i14 != 0) {
                    Integer numValueOf = (Integer) treeMap.get(Integer.valueOf(i13));
                    if (numValueOf == null) {
                        numValueOf = Integer.valueOf(i11);
                    }
                    treeMap.put(Integer.valueOf(i13), Integer.valueOf(i14 | numValueOf.intValue()));
                }
            }
            i5 = i12 + 1;
            i3 = i11;
        }
        return b0VarArr;
    }

    public static boolean x(ByteArrayOutputStream byteArrayOutputStream, byte[] bArr, b0[] b0VarArr) throws IOException {
        long j2;
        ArrayList arrayList;
        int length;
        byte[] bArr2 = f;
        int i2 = 0;
        if (!Arrays.equals(bArr, bArr2)) {
            byte[] bArr3 = g;
            if (Arrays.equals(bArr, bArr3)) {
                byte[] bArrG = g(b0VarArr, bArr3);
                C(byteArrayOutputStream, b0VarArr.length, 1);
                C(byteArrayOutputStream, bArrG.length, 4);
                byte[] bArrF = f(bArrG);
                C(byteArrayOutputStream, bArrF.length, 4);
                byteArrayOutputStream.write(bArrF);
                return true;
            }
            byte[] bArr4 = i;
            if (Arrays.equals(bArr, bArr4)) {
                C(byteArrayOutputStream, b0VarArr.length, 1);
                for (b0 b0Var : b0VarArr) {
                    int size = b0Var.i.size() * 4;
                    String strK = k(b0Var.a, b0Var.b, bArr4);
                    Charset charset = StandardCharsets.UTF_8;
                    D(byteArrayOutputStream, strK.getBytes(charset).length);
                    D(byteArrayOutputStream, b0Var.h.length);
                    C(byteArrayOutputStream, size, 4);
                    C(byteArrayOutputStream, b0Var.c, 4);
                    byteArrayOutputStream.write(strK.getBytes(charset));
                    Iterator it = b0Var.i.keySet().iterator();
                    while (it.hasNext()) {
                        D(byteArrayOutputStream, ((Integer) it.next()).intValue());
                        D(byteArrayOutputStream, 0);
                    }
                    for (int i3 : b0Var.h) {
                        D(byteArrayOutputStream, i3);
                    }
                }
                return true;
            }
            byte[] bArr5 = h;
            if (Arrays.equals(bArr, bArr5)) {
                byte[] bArrG2 = g(b0VarArr, bArr5);
                C(byteArrayOutputStream, b0VarArr.length, 1);
                C(byteArrayOutputStream, bArrG2.length, 4);
                byte[] bArrF2 = f(bArrG2);
                C(byteArrayOutputStream, bArrF2.length, 4);
                byteArrayOutputStream.write(bArrF2);
                return true;
            }
            byte[] bArr6 = j;
            if (!Arrays.equals(bArr, bArr6)) {
                return false;
            }
            D(byteArrayOutputStream, b0VarArr.length);
            for (b0 b0Var2 : b0VarArr) {
                String str = b0Var2.a;
                TreeMap treeMap = b0Var2.i;
                String strK2 = k(str, b0Var2.b, bArr6);
                Charset charset2 = StandardCharsets.UTF_8;
                D(byteArrayOutputStream, strK2.getBytes(charset2).length);
                D(byteArrayOutputStream, treeMap.size());
                D(byteArrayOutputStream, b0Var2.h.length);
                C(byteArrayOutputStream, b0Var2.c, 4);
                byteArrayOutputStream.write(strK2.getBytes(charset2));
                Iterator it2 = treeMap.keySet().iterator();
                while (it2.hasNext()) {
                    D(byteArrayOutputStream, ((Integer) it2.next()).intValue());
                }
                for (int i4 : b0Var2.h) {
                    D(byteArrayOutputStream, i4);
                }
            }
            return true;
        }
        ArrayList arrayList2 = new ArrayList(3);
        ArrayList arrayList3 = new ArrayList(3);
        ByteArrayOutputStream byteArrayOutputStream2 = new ByteArrayOutputStream();
        try {
            D(byteArrayOutputStream2, b0VarArr.length);
            int i5 = 2;
            int i6 = 2;
            for (b0 b0Var3 : b0VarArr) {
                C(byteArrayOutputStream2, b0Var3.c, 4);
                C(byteArrayOutputStream2, b0Var3.d, 4);
                C(byteArrayOutputStream2, b0Var3.g, 4);
                String strK3 = k(b0Var3.a, b0Var3.b, bArr2);
                Charset charset3 = StandardCharsets.UTF_8;
                int length2 = strK3.getBytes(charset3).length;
                D(byteArrayOutputStream2, length2);
                i6 = i6 + 14 + length2;
                byteArrayOutputStream2.write(strK3.getBytes(charset3));
            }
            byte[] byteArray = byteArrayOutputStream2.toByteArray();
            if (i6 != byteArray.length) {
                throw new IllegalStateException("Expected size " + i6 + ", does not match actual size " + byteArray.length);
            }
            h1 h1Var = new h1(1, byteArray, false);
            byteArrayOutputStream2.close();
            arrayList2.add(h1Var);
            ByteArrayOutputStream byteArrayOutputStream3 = new ByteArrayOutputStream();
            int i7 = 0;
            int i8 = 0;
            while (i7 < b0VarArr.length) {
                try {
                    b0 b0Var4 = b0VarArr[i7];
                    D(byteArrayOutputStream3, i7);
                    D(byteArrayOutputStream3, b0Var4.e);
                    i8 = i8 + 4 + (b0Var4.e * i5);
                    int[] iArr = b0Var4.h;
                    int length3 = iArr.length;
                    int i9 = i2;
                    while (i2 < length3) {
                        int i10 = iArr[i2];
                        D(byteArrayOutputStream3, i10 - i9);
                        i2++;
                        i5 = i5;
                        i9 = i10;
                    }
                    i7++;
                    i2 = 0;
                } catch (Throwable th) {
                    try {
                        byteArrayOutputStream3.close();
                        throw th;
                    } catch (Throwable th2) {
                        th.addSuppressed(th2);
                        throw th;
                    }
                }
            }
            int i11 = i5;
            byte[] byteArray2 = byteArrayOutputStream3.toByteArray();
            if (i8 != byteArray2.length) {
                throw new IllegalStateException("Expected size " + i8 + ", does not match actual size " + byteArray2.length);
            }
            h1 h1Var2 = new h1(3, byteArray2, true);
            byteArrayOutputStream3.close();
            arrayList2.add(h1Var2);
            ByteArrayOutputStream byteArrayOutputStream4 = new ByteArrayOutputStream();
            int i12 = 0;
            int i13 = 0;
            while (i12 < b0VarArr.length) {
                try {
                    b0 b0Var5 = b0VarArr[i12];
                    Iterator it3 = b0Var5.i.entrySet().iterator();
                    int iIntValue = 0;
                    while (it3.hasNext()) {
                        iIntValue |= ((Integer) ((Map.Entry) it3.next()).getValue()).intValue();
                    }
                    ByteArrayOutputStream byteArrayOutputStream5 = new ByteArrayOutputStream();
                    try {
                        z(byteArrayOutputStream5, b0Var5);
                        byte[] byteArray3 = byteArrayOutputStream5.toByteArray();
                        byteArrayOutputStream5.close();
                        ByteArrayOutputStream byteArrayOutputStream6 = new ByteArrayOutputStream();
                        try {
                            A(byteArrayOutputStream6, b0Var5);
                            byte[] byteArray4 = byteArrayOutputStream6.toByteArray();
                            byteArrayOutputStream6.close();
                            D(byteArrayOutputStream4, i12);
                            int length4 = byteArray3.length + 2 + byteArray4.length;
                            int i14 = i13 + 6;
                            ArrayList arrayList4 = arrayList3;
                            C(byteArrayOutputStream4, length4, 4);
                            D(byteArrayOutputStream4, iIntValue);
                            byteArrayOutputStream4.write(byteArray3);
                            byteArrayOutputStream4.write(byteArray4);
                            i13 = i14 + length4;
                            i12++;
                            arrayList3 = arrayList4;
                        } catch (Throwable th3) {
                            try {
                                byteArrayOutputStream6.close();
                                throw th3;
                            } catch (Throwable th4) {
                                th3.addSuppressed(th4);
                                throw th3;
                            }
                        }
                    } catch (Throwable th5) {
                        try {
                            byteArrayOutputStream5.close();
                            throw th5;
                        } catch (Throwable th6) {
                            th5.addSuppressed(th6);
                            throw th5;
                        }
                    }
                } catch (Throwable th7) {
                    try {
                        byteArrayOutputStream4.close();
                        throw th7;
                    } catch (Throwable th8) {
                        th7.addSuppressed(th8);
                        throw th7;
                    }
                }
            }
            ArrayList arrayList5 = arrayList3;
            byte[] byteArray5 = byteArrayOutputStream4.toByteArray();
            if (i13 != byteArray5.length) {
                throw new IllegalStateException("Expected size " + i13 + ", does not match actual size " + byteArray5.length);
            }
            h1 h1Var3 = new h1(4, byteArray5, true);
            byteArrayOutputStream4.close();
            arrayList2.add(h1Var3);
            long size2 = 12 + ((long) (arrayList2.size() * 16));
            C(byteArrayOutputStream, arrayList2.size(), 4);
            int i15 = 0;
            while (i15 < arrayList2.size()) {
                h1 h1Var4 = (h1) arrayList2.get(i15);
                int i16 = h1Var4.a;
                byte[] bArr7 = h1Var4.b;
                int i17 = i11;
                if (i16 == 1) {
                    j2 = 0;
                } else if (i16 == i17) {
                    j2 = 1;
                } else if (i16 == 3) {
                    j2 = 2;
                } else if (i16 == 4) {
                    j2 = 3;
                } else {
                    if (i16 != 5) {
                        throw null;
                    }
                    j2 = 4;
                }
                C(byteArrayOutputStream, j2, 4);
                C(byteArrayOutputStream, size2, 4);
                if (h1Var4.c) {
                    long length5 = bArr7.length;
                    byte[] bArrF3 = f(bArr7);
                    arrayList = arrayList5;
                    arrayList.add(bArrF3);
                    C(byteArrayOutputStream, bArrF3.length, 4);
                    C(byteArrayOutputStream, length5, 4);
                    length = bArrF3.length;
                } else {
                    arrayList = arrayList5;
                    arrayList.add(bArr7);
                    C(byteArrayOutputStream, bArr7.length, 4);
                    C(byteArrayOutputStream, 0L, 4);
                    length = bArr7.length;
                }
                size2 += (long) length;
                i15++;
                arrayList5 = arrayList;
                i11 = i17;
            }
            ArrayList arrayList6 = arrayList5;
            for (int i18 = 0; i18 < arrayList6.size(); i18++) {
                byteArrayOutputStream.write((byte[]) arrayList6.get(i18));
            }
            return true;
        } catch (Throwable th9) {
            try {
                byteArrayOutputStream2.close();
                throw th9;
            } catch (Throwable th10) {
                th9.addSuppressed(th10);
                throw th9;
            }
        }
    }

    public static void y(ByteArrayOutputStream byteArrayOutputStream, b0 b0Var, String str) throws IOException {
        Charset charset = StandardCharsets.UTF_8;
        D(byteArrayOutputStream, str.getBytes(charset).length);
        D(byteArrayOutputStream, b0Var.e);
        C(byteArrayOutputStream, b0Var.f, 4);
        C(byteArrayOutputStream, b0Var.c, 4);
        C(byteArrayOutputStream, b0Var.g, 4);
        byteArrayOutputStream.write(str.getBytes(charset));
    }

    public static void z(ByteArrayOutputStream byteArrayOutputStream, b0 b0Var) throws IOException {
        byte[] bArr = new byte[(((b0Var.g * 2) + 7) & (-8)) / 8];
        for (Map.Entry entry : b0Var.i.entrySet()) {
            int iIntValue = ((Integer) entry.getKey()).intValue();
            int iIntValue2 = ((Integer) entry.getValue()).intValue();
            if ((iIntValue2 & 2) != 0) {
                int i2 = iIntValue / 8;
                bArr[i2] = (byte) (bArr[i2] | (1 << (iIntValue % 8)));
            }
            if ((iIntValue2 & 4) != 0) {
                int i3 = iIntValue + b0Var.g;
                int i4 = i3 / 8;
                bArr[i4] = (byte) ((1 << (i3 % 8)) | bArr[i4]);
            }
        }
        byteArrayOutputStream.write(bArr);
    }

    public abstract boolean c(g gVar, c cVar);

    public abstract boolean d(g gVar, Object obj, Object obj2);

    public abstract boolean e(g gVar, f fVar, f fVar2);

    public abstract void m(f fVar, f fVar2);

    public abstract void n(f fVar, Thread thread);
}
