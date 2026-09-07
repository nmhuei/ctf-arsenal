package defpackage;

import java.util.Arrays;
import java.util.Collection;
import java.util.ConcurrentModificationException;
import java.util.Map;
import java.util.Set;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class o implements Map {
    public int[] a = y.a;
    public Object[] b = y.b;
    public int c;
    public j d;
    public l e;
    public n f;

    public final int a(Object obj) {
        int i = this.c * 2;
        Object[] objArr = this.b;
        if (obj == null) {
            for (int i2 = 1; i2 < i; i2 += 2) {
                if (objArr[i2] == null) {
                    return i2 >> 1;
                }
            }
            return -1;
        }
        for (int i3 = 1; i3 < i; i3 += 2) {
            if (obj.equals(objArr[i3])) {
                return i3 >> 1;
            }
        }
        return -1;
    }

    public final boolean b(Object obj) {
        return f(obj) >= 0;
    }

    public final boolean c(Object obj) {
        return a(obj) >= 0;
    }

    @Override // java.util.Map
    public final void clear() {
        if (this.c > 0) {
            this.a = y.a;
            this.b = y.b;
            this.c = 0;
        }
        if (this.c > 0) {
            throw new ConcurrentModificationException();
        }
    }

    @Override // java.util.Map
    public final boolean containsKey(Object obj) {
        return b(obj);
    }

    @Override // java.util.Map
    public final boolean containsValue(Object obj) {
        return c(obj);
    }

    public final Object d(Object obj) {
        int iF = f(obj);
        if (iF >= 0) {
            return this.b[(iF << 1) + 1];
        }
        return null;
    }

    public final int e(int i, Object obj) {
        int i2 = this.c;
        if (i2 == 0) {
            return -1;
        }
        int iB = y.b(this.a, i2, i);
        if (iB < 0 || y.a(obj, this.b[iB << 1])) {
            return iB;
        }
        int i3 = iB + 1;
        while (i3 < i2 && this.a[i3] == i) {
            if (y.a(obj, this.b[i3 << 1])) {
                return i3;
            }
            i3++;
        }
        for (int i4 = iB - 1; i4 >= 0 && this.a[i4] == i; i4--) {
            if (y.a(obj, this.b[i4 << 1])) {
                return i4;
            }
        }
        return ~i3;
    }

    @Override // java.util.Map
    public final Set entrySet() {
        j jVar = this.d;
        if (jVar != null) {
            return jVar;
        }
        j jVar2 = new j(this);
        this.d = jVar2;
        return jVar2;
    }

    @Override // java.util.Map
    public final boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        try {
            if (obj instanceof o) {
                int i = this.c;
                if (i != ((o) obj).c) {
                    return false;
                }
                o oVar = (o) obj;
                for (int i2 = 0; i2 < i; i2++) {
                    Object objH = h(i2);
                    Object objL = l(i2);
                    Object objD = oVar.d(objH);
                    if (objL == null) {
                        if (objD != null || !oVar.b(objH)) {
                            return false;
                        }
                    } else if (!objL.equals(objD)) {
                        return false;
                    }
                }
                return true;
            }
            if (!(obj instanceof Map) || this.c != ((Map) obj).size()) {
                return false;
            }
            int i3 = this.c;
            for (int i4 = 0; i4 < i3; i4++) {
                Object objH2 = h(i4);
                Object objL2 = l(i4);
                Object obj2 = ((Map) obj).get(objH2);
                if (objL2 == null) {
                    if (obj2 != null || !((Map) obj).containsKey(objH2)) {
                        return false;
                    }
                } else if (!objL2.equals(obj2)) {
                    return false;
                }
            }
            return true;
        } catch (ClassCastException | NullPointerException unused) {
        }
        return false;
    }

    public final int f(Object obj) {
        return obj == null ? g() : e(obj.hashCode(), obj);
    }

    public final int g() {
        int i = this.c;
        if (i == 0) {
            return -1;
        }
        int iB = y.b(this.a, i, 0);
        if (iB < 0 || this.b[iB << 1] == null) {
            return iB;
        }
        int i2 = iB + 1;
        while (i2 < i && this.a[i2] == 0) {
            if (this.b[i2 << 1] == null) {
                return i2;
            }
            i2++;
        }
        for (int i3 = iB - 1; i3 >= 0 && this.a[i3] == 0; i3--) {
            if (this.b[i3 << 1] == null) {
                return i3;
            }
        }
        return ~i2;
    }

    @Override // java.util.Map
    public final Object get(Object obj) {
        return d(obj);
    }

    @Override // java.util.Map
    public final Object getOrDefault(Object obj, Object obj2) {
        int iF = f(obj);
        return iF >= 0 ? this.b[(iF << 1) + 1] : obj2;
    }

    public final Object h(int i) {
        if (i >= 0 && i < this.c) {
            return this.b[i << 1];
        }
        i.a(i);
        return null;
    }

    @Override // java.util.Map
    public final int hashCode() {
        int[] iArr = this.a;
        Object[] objArr = this.b;
        int i = this.c;
        int i2 = 1;
        int i3 = 0;
        int iHashCode = 0;
        while (i3 < i) {
            Object obj = objArr[i2];
            iHashCode += (obj != null ? obj.hashCode() : 0) ^ iArr[i3];
            i3++;
            i2 += 2;
        }
        return iHashCode;
    }

    public final Object i(Object obj) {
        int iF = f(obj);
        if (iF >= 0) {
            return j(iF);
        }
        return null;
    }

    @Override // java.util.Map
    public final boolean isEmpty() {
        return this.c <= 0;
    }

    public final Object j(int i) {
        int i2;
        if (i < 0 || i >= (i2 = this.c)) {
            i.a(i);
            return null;
        }
        Object[] objArr = this.b;
        int i3 = i << 1;
        Object obj = objArr[i3 + 1];
        if (i2 <= 1) {
            clear();
            return obj;
        }
        int i4 = i2 - 1;
        int[] iArr = this.a;
        if (iArr.length <= 8 || i2 >= iArr.length / 3) {
            if (i < i4) {
                int i5 = i + 1;
                System.arraycopy(iArr, i5, iArr, i, i2 - i5);
                Object[] objArr2 = this.b;
                int i6 = i5 << 1;
                System.arraycopy(objArr2, i6, objArr2, i3, (i2 << 1) - i6);
            }
            Object[] objArr3 = this.b;
            int i7 = i4 << 1;
            objArr3[i7] = null;
            objArr3[i7 + 1] = null;
        } else {
            int i8 = i2 > 8 ? i2 + (i2 >> 1) : 8;
            this.a = Arrays.copyOf(iArr, i8);
            this.b = Arrays.copyOf(this.b, i8 << 1);
            if (i2 != this.c) {
                throw new ConcurrentModificationException();
            }
            if (i > 0) {
                System.arraycopy(iArr, 0, this.a, 0, i);
                System.arraycopy(objArr, 0, this.b, 0, i3);
            }
            if (i < i4) {
                int i9 = i + 1;
                System.arraycopy(iArr, i9, this.a, i, i2 - i9);
                int i10 = i9 << 1;
                System.arraycopy(objArr, i10, this.b, i3, (i2 << 1) - i10);
            }
        }
        if (i2 != this.c) {
            throw new ConcurrentModificationException();
        }
        this.c = i4;
        return obj;
    }

    public final Object k(int i, Object obj) {
        if (i < 0 || i >= this.c) {
            i.a(i);
            return null;
        }
        int i2 = (i << 1) + 1;
        Object[] objArr = this.b;
        Object obj2 = objArr[i2];
        objArr[i2] = obj;
        return obj2;
    }

    @Override // java.util.Map
    public final Set keySet() {
        l lVar = this.e;
        if (lVar != null) {
            return lVar;
        }
        l lVar2 = new l(this);
        this.e = lVar2;
        return lVar2;
    }

    public final Object l(int i) {
        if (i >= 0 && i < this.c) {
            return this.b[(i << 1) + 1];
        }
        i.a(i);
        return null;
    }

    @Override // java.util.Map
    public final Object put(Object obj, Object obj2) {
        int i = this.c;
        int iHashCode = obj != null ? obj.hashCode() : 0;
        int iE = obj != null ? e(iHashCode, obj) : g();
        if (iE >= 0) {
            int i2 = (iE << 1) + 1;
            Object[] objArr = this.b;
            Object obj3 = objArr[i2];
            objArr[i2] = obj2;
            return obj3;
        }
        int i3 = ~iE;
        int[] iArr = this.a;
        if (i >= iArr.length) {
            int i4 = 8;
            if (i >= 8) {
                i4 = (i >> 1) + i;
            } else if (i < 4) {
                i4 = 4;
            }
            this.a = Arrays.copyOf(iArr, i4);
            this.b = Arrays.copyOf(this.b, i4 << 1);
            if (i != this.c) {
                throw new ConcurrentModificationException();
            }
        }
        if (i3 < i) {
            int[] iArr2 = this.a;
            int i5 = i3 + 1;
            System.arraycopy(iArr2, i3, iArr2, i5, i - i3);
            Object[] objArr2 = this.b;
            int i6 = i3 << 1;
            System.arraycopy(objArr2, i6, objArr2, i5 << 1, (this.c << 1) - i6);
        }
        int i7 = this.c;
        if (i == i7) {
            int[] iArr3 = this.a;
            if (i3 < iArr3.length) {
                iArr3[i3] = iHashCode;
                Object[] objArr3 = this.b;
                int i8 = i3 << 1;
                objArr3[i8] = obj;
                objArr3[i8 + 1] = obj2;
                this.c = i7 + 1;
                return null;
            }
        }
        throw new ConcurrentModificationException();
    }

    @Override // java.util.Map
    public final void putAll(Map map) {
        int size = map.size() + this.c;
        int i = this.c;
        int[] iArr = this.a;
        if (iArr.length < size) {
            this.a = Arrays.copyOf(iArr, size);
            this.b = Arrays.copyOf(this.b, size * 2);
        }
        if (this.c != i) {
            throw new ConcurrentModificationException();
        }
        for (Map.Entry entry : map.entrySet()) {
            put(entry.getKey(), entry.getValue());
        }
    }

    @Override // java.util.Map
    public final Object putIfAbsent(Object obj, Object obj2) {
        Object objD = d(obj);
        return objD == null ? put(obj, obj2) : objD;
    }

    @Override // java.util.Map
    public final boolean remove(Object obj, Object obj2) {
        int iF = f(obj);
        if (iF < 0 || !y.a(obj2, l(iF))) {
            return false;
        }
        j(iF);
        return true;
    }

    @Override // java.util.Map
    public final boolean replace(Object obj, Object obj2, Object obj3) {
        int iF = f(obj);
        if (iF < 0 || !y.a(obj2, l(iF))) {
            return false;
        }
        k(iF, obj3);
        return true;
    }

    @Override // java.util.Map
    public final int size() {
        return this.c;
    }

    public final String toString() {
        if (isEmpty()) {
            return "{}";
        }
        StringBuilder sb = new StringBuilder(this.c * 28);
        sb.append('{');
        int i = this.c;
        for (int i2 = 0; i2 < i; i2++) {
            if (i2 > 0) {
                sb.append(", ");
            }
            Object objH = h(i2);
            if (objH != sb) {
                sb.append(objH);
            } else {
                sb.append("(this Map)");
            }
            sb.append('=');
            Object objL = l(i2);
            if (objL != sb) {
                sb.append(objL);
            } else {
                sb.append("(this Map)");
            }
        }
        sb.append('}');
        return sb.toString();
    }

    @Override // java.util.Map
    public final Collection values() {
        n nVar = this.f;
        if (nVar != null) {
            return nVar;
        }
        n nVar2 = new n(this);
        this.f = nVar2;
        return nVar2;
    }

    @Override // java.util.Map
    public final Object remove(Object obj) {
        return i(obj);
    }

    @Override // java.util.Map
    public final Object replace(Object obj, Object obj2) {
        int iF = f(obj);
        if (iF >= 0) {
            return k(iF, obj2);
        }
        return null;
    }
}
