package defpackage;

import android.content.res.AssetManager;
import android.os.Build;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.Serializable;
import java.util.concurrent.Executor;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class a0 {
    public final Executor a;
    public final s0 b;
    public final byte[] c;
    public final File d;
    public final String e;
    public boolean f = false;
    public b0[] g;
    public byte[] h;

    public a0(AssetManager assetManager, Executor executor, s0 s0Var, String str, File file) {
        this.a = executor;
        this.b = s0Var;
        this.e = str;
        this.d = file;
        int i = Build.VERSION.SDK_INT;
        byte[] bArr = null;
        if (i <= 34) {
            switch (i) {
                case 26:
                    bArr = y.i;
                    break;
                case 27:
                    bArr = y.h;
                    break;
                case 28:
                case 29:
                case 30:
                    bArr = y.g;
                    break;
                case 31:
                case 32:
                case 33:
                case 34:
                    bArr = y.f;
                    break;
            }
        }
        this.c = bArr;
    }

    public final FileInputStream a(AssetManager assetManager, String str) {
        try {
            return assetManager.openFd(str).createInputStream();
        } catch (FileNotFoundException e) {
            String message = e.getMessage();
            if (message == null || !message.contains("compressed")) {
                return null;
            }
            this.b.a();
            return null;
        }
    }

    public final void b(final int i, final Serializable serializable) {
        this.a.execute(new Runnable() { // from class: z
            @Override // java.lang.Runnable
            public final void run() {
                this.a.b.b(i, serializable);
            }
        });
    }
}
