package defpackage;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class a {
    public static final a b;
    public static final a c;
    public final Throwable a;

    static {
        if (g.d) {
            c = null;
            b = null;
        } else {
            c = new a(false, null);
            b = new a(true, null);
        }
    }

    public a(boolean z, Throwable th) {
        this.a = th;
    }
}
