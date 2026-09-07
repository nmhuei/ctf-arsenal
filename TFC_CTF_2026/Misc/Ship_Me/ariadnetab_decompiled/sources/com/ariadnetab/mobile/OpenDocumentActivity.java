package com.ariadnetab.mobile;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Toast;
import com.tfcctf.ariadnetab.R;
import defpackage.c0;
import defpackage.e0;
import java.util.Locale;
import java.util.UUID;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class OpenDocumentActivity extends Activity {
    public e0 a;

    @Override // android.app.Activity
    public final void onCreate(Bundle bundle) {
        boolean zEquals;
        super.onCreate(bundle);
        this.a = new e0(this);
        if (!"com.tfcctf.ariadnetab.OPEN_DOCUMENT".equals(getIntent().getAction())) {
            Toast.makeText(this, R.string.invalid_action, 0).show();
            finish();
            return;
        }
        String stringExtra = getIntent().getStringExtra("document_id");
        if (stringExtra == null) {
            zEquals = false;
        } else {
            try {
                zEquals = UUID.fromString(stringExtra).toString().equals(stringExtra.toLowerCase(Locale.ROOT));
            } catch (IllegalArgumentException unused) {
                zEquals = false;
            }
        }
        if (!zEquals) {
            Toast.makeText(this, R.string.invalid_document_id, 0).show();
            finish();
            return;
        }
        String lowerCase = stringExtra.toLowerCase(Locale.ROOT);
        this.a.b("https://ariadnetab.xyz/#/open/" + lowerCase, true);
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
