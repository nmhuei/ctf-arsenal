package defpackage;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.RemoteException;
import android.widget.Toast;
import com.tfcctf.ariadnetab.R;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class e0 {
    public static final Uri h = Uri.parse("https://ariadnetab.xyz");
    public final Activity a;
    public final x b;
    public w c;
    public c0 d;
    public boolean e;
    public boolean f;
    public final d0 g = new d0(this);

    public e0(Activity activity) {
        x xVarJ;
        this.a = activity;
        synchronized (y.class) {
            SharedPreferences sharedPreferences = activity.getSharedPreferences("device", 0);
            xVarJ = null;
            String string = sharedPreferences.getString("rsa_private_pkcs8", null);
            String string2 = sharedPreferences.getString("rsa_public_spki", null);
            if (string != null && string2 != null) {
                xVarJ = new x(string, string2);
            }
            if (xVarJ == null) {
                xVarJ = y.j();
                if (!sharedPreferences.edit().putString("rsa_private_pkcs8", xVarJ.a).putString("rsa_public_spki", xVarJ.b).commit()) {
                    throw new IllegalStateException("Unable to persist device keys");
                }
            }
        }
        this.b = xVarJ;
    }

    public static void a(e0 e0Var) {
        w wVar = e0Var.c;
        if (wVar == null || e0Var.e) {
            return;
        }
        e0Var.e = true;
        Bundle bundle = new Bundle();
        t tVar = wVar.c;
        k0 k0Var = wVar.b;
        try {
            Bundle bundle2 = new Bundle();
            if (bundle2.isEmpty()) {
                bundle2 = null;
            }
            Uri uri = h;
            if (bundle2 == null) {
                ((i0) k0Var).e(tVar, uri);
            } else {
                bundle.putAll(bundle2);
                ((i0) k0Var).f(tVar, uri, bundle);
            }
        } catch (RemoteException unused) {
        }
    }

    public final void b(String str, boolean z) {
        Uri uri = Uri.parse(str);
        Uri uri2 = h;
        if (!uri2.getScheme().equals(uri.getScheme()) || !uri2.getHost().equals(uri.getHost()) || uri2.getPort() != uri.getPort()) {
            throw new IllegalArgumentException("Untrusted URL");
        }
        this.f = z;
        this.e = false;
        c0 c0Var = new c0(this, uri);
        this.d = c0Var;
        Activity activity = this.a;
        c0Var.a = activity.getApplicationContext();
        Intent intent = new Intent("android.support.customtabs.action.CustomTabsService");
        intent.setPackage("com.android.chrome");
        if (activity.bindService(intent, c0Var, 33)) {
            return;
        }
        this.d = null;
        Toast.makeText(activity, R.string.chrome_unavailable, 0).show();
        activity.finish();
    }
}
