package defpackage;

import android.os.Bundle;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class r implements Runnable {
    public final /* synthetic */ t a;

    public r(t tVar, Bundle bundle) {
        this.a = tVar;
    }

    @Override // java.lang.Runnable
    public final void run() {
        w wVar = ((e0) this.a.e.a).c;
        if (wVar != null) {
            wVar.a("");
        }
    }
}
