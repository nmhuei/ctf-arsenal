package defpackage;

import android.app.Activity;
import android.app.ActivityOptions;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.IBinder;
import android.os.IInterface;
import android.os.LocaleList;
import android.os.RemoteException;
import android.text.TextUtils;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class c0 implements ServiceConnection {
    public Context a;
    public final /* synthetic */ Uri b;
    public final /* synthetic */ e0 c;

    public c0(e0 e0Var, Uri uri) {
        this.c = e0Var;
        this.b = uri;
    }

    @Override // android.content.ServiceConnection
    public final void onServiceConnected(ComponentName componentName, IBinder iBinder) {
        k0 k0Var;
        w wVar;
        ActivityOptions activityOptionsMakeBasic;
        if (this.a == null) {
            throw new IllegalStateException("Custom Tabs Service connected before an applicationcontext has been provided.");
        }
        int i = j0.d;
        if (iBinder == null) {
            k0Var = null;
        } else {
            IInterface iInterfaceQueryLocalInterface = iBinder.queryLocalInterface(k0.b);
            if (iInterfaceQueryLocalInterface == null || !(iInterfaceQueryLocalInterface instanceof k0)) {
                i0 i0Var = new i0();
                i0Var.d = iBinder;
                k0Var = i0Var;
            } else {
                k0Var = (k0) iInterfaceQueryLocalInterface;
            }
        }
        try {
            ((i0) k0Var).g();
        } catch (RemoteException unused) {
        }
        e0 e0Var = this.c;
        d0 d0Var = e0Var.g;
        Activity activity = e0Var.a;
        t tVar = new t(d0Var);
        try {
            wVar = !((i0) k0Var).c(tVar) ? null : new w(k0Var, tVar, componentName);
        } catch (RemoteException unused2) {
        }
        e0Var.c = wVar;
        if (wVar == null) {
            activity.finish();
            return;
        }
        if (e0Var.f) {
            e0.a(e0Var);
        }
        w wVar2 = e0Var.c;
        Intent intent = new Intent("android.intent.action.VIEW");
        if (wVar2 != null) {
            intent.setPackage(wVar2.d.getPackageName());
            t tVar2 = wVar2.c;
            Bundle bundle = new Bundle();
            bundle.putBinder("android.support.customtabs.extra.SESSION", tVar2);
            intent.putExtras(bundle);
        }
        if (!intent.hasExtra("android.support.customtabs.extra.SESSION")) {
            Bundle bundle2 = new Bundle();
            bundle2.putBinder("android.support.customtabs.extra.SESSION", null);
            intent.putExtras(bundle2);
        }
        intent.putExtra("android.support.customtabs.extra.EXTRA_ENABLE_INSTANT_APPS", true);
        intent.putExtras(new Bundle());
        intent.putExtra("androidx.browser.customtabs.extra.SHARE_STATE", 0);
        LocaleList adjustedDefault = LocaleList.getAdjustedDefault();
        String languageTag = adjustedDefault.size() > 0 ? adjustedDefault.get(0).toLanguageTag() : null;
        if (!TextUtils.isEmpty(languageTag)) {
            Bundle bundleExtra = intent.hasExtra("com.android.browser.headers") ? intent.getBundleExtra("com.android.browser.headers") : new Bundle();
            if (!bundleExtra.containsKey("Accept-Language")) {
                bundleExtra.putString("Accept-Language", languageTag);
                intent.putExtra("com.android.browser.headers", bundleExtra);
            }
        }
        int i2 = Build.VERSION.SDK_INT;
        if (i2 >= 34) {
            activityOptionsMakeBasic = ActivityOptions.makeBasic();
            u.a(activityOptionsMakeBasic);
        } else {
            activityOptionsMakeBasic = null;
        }
        if (i2 >= 36) {
            if (activityOptionsMakeBasic == null) {
                activityOptionsMakeBasic = ActivityOptions.makeBasic();
            }
            v.a(activityOptionsMakeBasic, !intent.getBooleanExtra("androidx.browser.customtabs.extra.DISABLE_BACKGROUND_INTERACTION", false));
        }
        Bundle bundle3 = activityOptionsMakeBasic != null ? activityOptionsMakeBasic.toBundle() : null;
        intent.setData(this.b);
        activity.startActivity(intent, bundle3);
    }

    @Override // android.content.ServiceConnection
    public final void onServiceDisconnected(ComponentName componentName) {
        this.c.c = null;
    }
}
