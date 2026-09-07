package defpackage;

import android.os.Bundle;
import org.json.JSONException;
import org.json.JSONObject;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class s implements Runnable {
    public final /* synthetic */ String a;
    public final /* synthetic */ t b;

    public s(t tVar, String str, Bundle bundle) {
        this.b = tVar;
        this.a = str;
    }

    @Override // java.lang.Runnable
    public final void run() {
        String strI;
        d0 d0Var = this.b.e;
        String str = this.a;
        e0 e0Var = (e0) d0Var.a;
        w wVar = e0Var.c;
        if (wVar == null) {
            return;
        }
        x xVar = e0Var.b;
        try {
            JSONObject jSONObject = new JSONObject(str);
            int i = jSONObject.getInt("id");
            if ("key.get".equals(jSONObject.optString("method")) && (jSONObject.opt("params") instanceof JSONObject)) {
                strI = new JSONObject().put("id", i).put("result", new JSONObject().put("privateKey", xVar.a).put("publicKey", xVar.b)).toString();
            } else {
                strI = y.i(Integer.valueOf(i), "method_not_found", "Unknown method");
            }
        } catch (JSONException unused) {
            strI = y.i(JSONObject.NULL, "invalid_request", "Invalid request");
        }
        wVar.a(strI);
    }
}
