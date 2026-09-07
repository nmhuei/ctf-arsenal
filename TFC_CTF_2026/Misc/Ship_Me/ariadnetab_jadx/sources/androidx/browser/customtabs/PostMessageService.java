package androidx.browser.customtabs;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import defpackage.l0;
import defpackage.p0;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public class PostMessageService extends Service {
    public final p0 a;

    public PostMessageService() {
        p0 p0Var = new p0();
        p0Var.attachInterface(p0Var, l0.c);
        this.a = p0Var;
    }

    @Override // android.app.Service
    public final IBinder onBind(Intent intent) {
        return this.a;
    }
}
