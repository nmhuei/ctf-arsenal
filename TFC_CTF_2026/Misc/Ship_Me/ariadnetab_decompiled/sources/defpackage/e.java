package defpackage;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class e extends y {
    @Override // defpackage.y
    public final boolean c(g gVar, c cVar) {
        c cVar2 = c.b;
        synchronized (gVar) {
            try {
                if (gVar.b != cVar) {
                    return false;
                }
                gVar.b = cVar2;
                return true;
            } catch (Throwable th) {
                throw th;
            }
        }
    }

    @Override // defpackage.y
    public final boolean d(g gVar, Object obj, Object obj2) {
        synchronized (gVar) {
            try {
                if (gVar.a != obj) {
                    return false;
                }
                gVar.a = obj2;
                return true;
            } catch (Throwable th) {
                throw th;
            }
        }
    }

    @Override // defpackage.y
    public final boolean e(g gVar, f fVar, f fVar2) {
        synchronized (gVar) {
            try {
                if (gVar.c != fVar) {
                    return false;
                }
                gVar.c = fVar2;
                return true;
            } catch (Throwable th) {
                throw th;
            }
        }
    }

    @Override // defpackage.y
    public final void m(f fVar, f fVar2) {
        fVar.b = fVar2;
    }

    @Override // defpackage.y
    public final void n(f fVar, Thread thread) {
        fVar.a = thread;
    }
}
