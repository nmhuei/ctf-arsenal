package defpackage;

import android.content.Context;
import android.os.Bundle;
import android.os.Trace;
import android.util.Log;
import androidx.profileinstaller.ProfileInstallerInitializer;
import com.tfcctf.ariadnetab.R;
import java.lang.reflect.InvocationTargetException;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class h {
    public static volatile h d;
    public static final Object e = new Object();
    public final Context c;
    public final HashSet b = new HashSet();
    public final HashMap a = new HashMap();

    public h(Context context) {
        this.c = context.getApplicationContext();
    }

    public final void a(Bundle bundle) {
        HashSet hashSet;
        String string = this.c.getString(R.string.androidx_startup);
        if (bundle != null) {
            try {
                HashSet hashSet2 = new HashSet();
                Iterator<String> it = bundle.keySet().iterator();
                while (true) {
                    boolean zHasNext = it.hasNext();
                    hashSet = this.b;
                    if (!zHasNext) {
                        break;
                    }
                    String next = it.next();
                    if (string.equals(bundle.getString(next, null))) {
                        Class<?> cls = Class.forName(next);
                        if (ProfileInstallerInitializer.class.isAssignableFrom(cls)) {
                            hashSet.add(cls);
                        }
                    }
                }
                Iterator it2 = hashSet.iterator();
                while (it2.hasNext()) {
                    b((Class) it2.next(), hashSet2);
                }
            } catch (ClassNotFoundException e2) {
                throw new c1(e2);
            }
        }
    }

    public final void b(Class cls, HashSet hashSet) {
        boolean zBooleanValue;
        HashMap map = this.a;
        try {
            if (y.n == null) {
                zBooleanValue = Trace.isEnabled();
            } else {
                try {
                    if (y.n == null) {
                        y.m = Trace.class.getField("TRACE_TAG_APP").getLong(null);
                        y.n = Trace.class.getMethod("isTagEnabled", Long.TYPE);
                    }
                    zBooleanValue = ((Boolean) y.n.invoke(null, Long.valueOf(y.m))).booleanValue();
                } catch (Exception e2) {
                    if (e2 instanceof InvocationTargetException) {
                        Throwable cause = e2.getCause();
                        if (!(cause instanceof RuntimeException)) {
                            throw new RuntimeException(cause);
                        }
                        throw ((RuntimeException) cause);
                    }
                    Log.v("Trace", "Unable to call isTagEnabled via reflection", e2);
                    zBooleanValue = false;
                }
            }
        } catch (NoClassDefFoundError | NoSuchMethodError unused) {
        }
        if (zBooleanValue) {
            try {
                Trace.beginSection(cls.getSimpleName());
            } catch (Throwable th) {
                Trace.endSection();
                throw th;
            }
        }
        if (hashSet.contains(cls)) {
            throw new IllegalStateException("Cannot initialize " + cls.getName() + ". Cycle detected.");
        }
        if (map.containsKey(cls)) {
            map.get(cls);
        } else {
            hashSet.add(cls);
            try {
                ProfileInstallerInitializer profileInstallerInitializer = (ProfileInstallerInitializer) cls.getDeclaredConstructor(null).newInstance(null);
                profileInstallerInitializer.getClass();
                List<Class> list = Collections.EMPTY_LIST;
                if (!list.isEmpty()) {
                    for (Class cls2 : list) {
                        if (!map.containsKey(cls2)) {
                            b(cls2, hashSet);
                        }
                    }
                }
                v0.a(new t0(profileInstallerInitializer, this.c.getApplicationContext()));
                r0 r0Var = new r0(2);
                hashSet.remove(cls);
                map.put(cls, r0Var);
            } catch (Throwable th2) {
                throw new c1(th2);
            }
        }
        Trace.endSection();
    }
}
