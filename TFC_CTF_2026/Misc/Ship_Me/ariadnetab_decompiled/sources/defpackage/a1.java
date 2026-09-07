package defpackage;

import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import java.io.File;
import java.io.IOException;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public abstract class a1 {
    public static final b1 a = new b1();
    public static final Object b = new Object();
    public static r0 c = null;

    public static long a(Context context) {
        PackageManager packageManager = context.getApplicationContext().getPackageManager();
        return Build.VERSION.SDK_INT >= 33 ? y0.a(packageManager, context).lastUpdateTime : packageManager.getPackageInfo(context.getPackageName(), 0).lastUpdateTime;
    }

    public static r0 b() {
        r0 r0Var = new r0(3);
        c = r0Var;
        b1 b1Var = a;
        b1Var.getClass();
        if (g.f.d(b1Var, null, r0Var)) {
            g.b(b1Var);
        }
        return c;
    }

    public static void c(Context context, boolean z) {
        z0 z0VarA;
        int i;
        if (z || c == null) {
            synchronized (b) {
                if (!z) {
                    try {
                        if (c != null) {
                            return;
                        }
                    } catch (Throwable th) {
                        throw th;
                    }
                }
                int i2 = Build.VERSION.SDK_INT;
                if (i2 >= 28 && i2 != 30) {
                    File file = new File(new File("/data/misc/profiles/ref/", context.getPackageName()), "primary.prof");
                    long length = file.length();
                    int i3 = 0;
                    boolean z2 = file.exists() && length > 0;
                    File file2 = new File(new File("/data/misc/profiles/cur/0/", context.getPackageName()), "primary.prof");
                    long length2 = file2.length();
                    boolean z3 = file2.exists() && length2 > 0;
                    try {
                        long jA = a(context);
                        File file3 = new File(context.getFilesDir(), "profileInstalled");
                        if (file3.exists()) {
                            try {
                                z0VarA = z0.a(file3);
                            } catch (IOException unused) {
                                b();
                                return;
                            }
                        } else {
                            z0VarA = null;
                        }
                        if (z0VarA != null && z0VarA.c == jA && (i = z0VarA.b) != 2) {
                            i3 = i;
                        } else if (z2) {
                            i3 = 1;
                        } else if (z3) {
                            i3 = 2;
                        }
                        if (z && z3 && i3 != 1) {
                            i3 = 2;
                        }
                        if (z0VarA != null && z0VarA.b == 2 && i3 == 1 && length < z0VarA.d) {
                            i3 = 3;
                        }
                        z0 z0Var = new z0(1, i3, jA, length2);
                        if (z0VarA == null || !z0VarA.equals(z0Var)) {
                            try {
                                z0Var.b(file3);
                            } catch (IOException unused2) {
                            }
                        }
                        b();
                        return;
                    } catch (PackageManager.NameNotFoundException unused3) {
                        b();
                        return;
                    }
                }
                b();
            }
        }
    }
}
