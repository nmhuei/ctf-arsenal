package defpackage;

import java.util.Iterator;
import java.util.NoSuchElementException;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class k implements Iterator {
    public int a;
    public int b;
    public boolean c;
    public final /* synthetic */ int d;
    public final /* synthetic */ o e;

    /* JADX WARN: 'this' call moved to the top of the method (can break code semantics) */
    public k(o oVar, int i) {
        this(oVar.c);
        this.d = i;
        switch (i) {
            case 1:
                this.e = oVar;
                this(oVar.c);
                break;
            default:
                this.e = oVar;
                break;
        }
    }

    @Override // java.util.Iterator
    public final boolean hasNext() {
        return this.b < this.a;
    }

    @Override // java.util.Iterator
    public final Object next() {
        Object objH;
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        int i = this.b;
        int i2 = this.d;
        o oVar = this.e;
        switch (i2) {
            case 0:
                objH = oVar.h(i);
                break;
            default:
                objH = oVar.l(i);
                break;
        }
        this.b++;
        this.c = true;
        return objH;
    }

    @Override // java.util.Iterator
    public final void remove() {
        if (!this.c) {
            throw new IllegalStateException("Call next() before removing an element.");
        }
        int i = this.b - 1;
        this.b = i;
        int i2 = this.d;
        o oVar = this.e;
        switch (i2) {
            case 0:
                oVar.j(i);
                break;
            default:
                oVar.j(i);
                break;
        }
        this.a--;
        this.c = false;
    }

    public k(int i) {
        this.a = i;
    }
}
