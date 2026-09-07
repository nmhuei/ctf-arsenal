package defpackage;

import java.lang.reflect.Array;
import java.util.Collection;
import java.util.Iterator;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class n implements Collection {
    public final /* synthetic */ o a;

    public n(o oVar) {
        this.a = oVar;
    }

    @Override // java.util.Collection
    public final boolean add(Object obj) {
        throw new UnsupportedOperationException();
    }

    @Override // java.util.Collection
    public final boolean addAll(Collection collection) {
        throw new UnsupportedOperationException();
    }

    @Override // java.util.Collection
    public final void clear() {
        this.a.clear();
    }

    @Override // java.util.Collection
    public final boolean contains(Object obj) {
        return this.a.a(obj) >= 0;
    }

    @Override // java.util.Collection
    public final boolean containsAll(Collection collection) {
        Iterator it = collection.iterator();
        while (it.hasNext()) {
            if (!contains(it.next())) {
                return false;
            }
        }
        return true;
    }

    @Override // java.util.Collection
    public final boolean isEmpty() {
        return this.a.isEmpty();
    }

    @Override // java.util.Collection, java.lang.Iterable
    public final Iterator iterator() {
        return new k(this.a, 1);
    }

    @Override // java.util.Collection
    public final boolean remove(Object obj) {
        o oVar = this.a;
        int iA = oVar.a(obj);
        if (iA < 0) {
            return false;
        }
        oVar.j(iA);
        return true;
    }

    @Override // java.util.Collection
    public final boolean removeAll(Collection collection) {
        o oVar = this.a;
        int i = oVar.c;
        int i2 = 0;
        boolean z = false;
        while (i2 < i) {
            if (collection.contains(oVar.l(i2))) {
                oVar.j(i2);
                i2--;
                i--;
                z = true;
            }
            i2++;
        }
        return z;
    }

    @Override // java.util.Collection
    public final boolean retainAll(Collection collection) {
        o oVar = this.a;
        int i = oVar.c;
        int i2 = 0;
        boolean z = false;
        while (i2 < i) {
            if (!collection.contains(oVar.l(i2))) {
                oVar.j(i2);
                i2--;
                i--;
                z = true;
            }
            i2++;
        }
        return z;
    }

    @Override // java.util.Collection
    public final int size() {
        return this.a.c;
    }

    @Override // java.util.Collection
    public final Object[] toArray(Object[] objArr) {
        o oVar = this.a;
        int i = oVar.c;
        if (objArr.length < i) {
            objArr = (Object[]) Array.newInstance(objArr.getClass().getComponentType(), i);
        }
        for (int i2 = 0; i2 < i; i2++) {
            objArr[i2] = oVar.l(i2);
        }
        if (objArr.length > i) {
            objArr[i] = null;
        }
        return objArr;
    }

    @Override // java.util.Collection
    public final Object[] toArray() {
        o oVar = this.a;
        int i = oVar.c;
        Object[] objArr = new Object[i];
        for (int i2 = 0; i2 < i; i2++) {
            objArr[i2] = oVar.l(i2);
        }
        return objArr;
    }
}
