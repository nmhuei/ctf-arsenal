package defpackage;

import android.content.ComponentName;
import android.os.Bundle;
import android.os.RemoteException;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class w {
    public final Object a = new Object();
    public final k0 b;
    public final t c;
    public final ComponentName d;

    public w(k0 k0Var, t tVar, ComponentName componentName) {
        this.b = k0Var;
        this.c = tVar;
        this.d = componentName;
    }

    public final void a(String str) {
        Bundle bundle = new Bundle();
        synchronized (this.a) {
            try {
                try {
                    ((i0) this.b).d(this.c, str, bundle);
                } catch (RemoteException unused) {
                }
            } catch (Throwable th) {
                throw th;
            }
        }
    }
}
