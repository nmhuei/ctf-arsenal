package defpackage;

import android.os.Bundle;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class q implements Runnable {
    public final /* synthetic */ int a;
    public final /* synthetic */ t b;

    public q(int i, t tVar, Bundle bundle) {
        this.b = tVar;
        this.a = i;
    }

    @Override // java.lang.Runnable
    public final void run() {
        d0 d0Var = this.b.e;
        if (this.a == 2) {
            e0 e0Var = (e0) d0Var.a;
            if (e0Var.f) {
                return;
            }
            e0.a(e0Var);
        }
    }
}
