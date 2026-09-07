package com.ariadnetab.mobile;

import android.app.Activity;
import android.os.Bundle;
import defpackage.c0;
import defpackage.e0;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class MainActivity extends Activity {
    public e0 a;

    @Override // android.app.Activity
    public final void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        e0 e0Var = new e0(this);
        this.a = e0Var;
        e0Var.b("https://ariadnetab.xyz/", false);
    }

    @Override // android.app.Activity
    public final void onDestroy() {
        e0 e0Var = this.a;
        c0 c0Var = e0Var.d;
        if (c0Var != null) {
            e0Var.a.unbindService(c0Var);
            e0Var.d = null;
        }
        super.onDestroy();
    }
}
