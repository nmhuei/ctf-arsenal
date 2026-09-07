package defpackage;

import android.os.Parcel;
import android.os.Parcelable;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public abstract class e1 {
    public final o a;
    public final o b;
    public final o c;

    public e1(o oVar, o oVar2, o oVar3) {
        this.a = oVar;
        this.b = oVar2;
        this.c = oVar3;
    }

    public abstract f1 a();

    public final Class b(Class cls) throws ClassNotFoundException {
        String name = cls.getName();
        o oVar = this.c;
        Class cls2 = (Class) oVar.d(name);
        if (cls2 != null) {
            return cls2;
        }
        Class<?> cls3 = Class.forName(cls.getPackage().getName() + "." + cls.getSimpleName() + "Parcelizer", false, cls.getClassLoader());
        oVar.put(cls.getName(), cls3);
        return cls3;
    }

    public final Method c(String str) throws NoSuchMethodException {
        o oVar = this.a;
        Method method = (Method) oVar.d(str);
        if (method != null) {
            return method;
        }
        System.currentTimeMillis();
        Method declaredMethod = Class.forName(str, true, e1.class.getClassLoader()).getDeclaredMethod("read", e1.class);
        oVar.put(str, declaredMethod);
        return declaredMethod;
    }

    public final Method d(Class cls) throws NoSuchMethodException, ClassNotFoundException {
        String name = cls.getName();
        o oVar = this.b;
        Method method = (Method) oVar.d(name);
        if (method != null) {
            return method;
        }
        Class clsB = b(cls);
        System.currentTimeMillis();
        Method declaredMethod = clsB.getDeclaredMethod("write", cls, e1.class);
        oVar.put(cls.getName(), declaredMethod);
        return declaredMethod;
    }

    public abstract boolean e(int i);

    public final Parcelable f(Parcelable parcelable, int i) {
        if (!e(i)) {
            return parcelable;
        }
        return ((f1) this).e.readParcelable(f1.class.getClassLoader());
    }

    public final g1 g() {
        String string = ((f1) this).e.readString();
        if (string == null) {
            return null;
        }
        try {
            return (g1) c(string).invoke(null, a());
        } catch (ClassNotFoundException e) {
            throw new RuntimeException("VersionedParcel encountered ClassNotFoundException", e);
        } catch (IllegalAccessException e2) {
            throw new RuntimeException("VersionedParcel encountered IllegalAccessException", e2);
        } catch (NoSuchMethodException e3) {
            throw new RuntimeException("VersionedParcel encountered NoSuchMethodException", e3);
        } catch (InvocationTargetException e4) {
            if (e4.getCause() instanceof RuntimeException) {
                throw ((RuntimeException) e4.getCause());
            }
            throw new RuntimeException("VersionedParcel encountered InvocationTargetException", e4);
        }
    }

    public abstract void h(int i);

    public final void i(g1 g1Var) {
        if (g1Var == null) {
            ((f1) this).e.writeString(null);
            return;
        }
        try {
            ((f1) this).e.writeString(b(g1Var.getClass()).getName());
            f1 f1VarA = a();
            try {
                d(g1Var.getClass()).invoke(null, g1Var, f1VarA);
                Parcel parcel = f1VarA.e;
                int i = f1VarA.i;
                if (i >= 0) {
                    int i2 = f1VarA.d.get(i);
                    int iDataPosition = parcel.dataPosition();
                    parcel.setDataPosition(i2);
                    parcel.writeInt(iDataPosition - i2);
                    parcel.setDataPosition(iDataPosition);
                }
            } catch (ClassNotFoundException e) {
                throw new RuntimeException("VersionedParcel encountered ClassNotFoundException", e);
            } catch (IllegalAccessException e2) {
                throw new RuntimeException("VersionedParcel encountered IllegalAccessException", e2);
            } catch (NoSuchMethodException e3) {
                throw new RuntimeException("VersionedParcel encountered NoSuchMethodException", e3);
            } catch (InvocationTargetException e4) {
                if (!(e4.getCause() instanceof RuntimeException)) {
                    throw new RuntimeException("VersionedParcel encountered InvocationTargetException", e4);
                }
                throw ((RuntimeException) e4.getCause());
            }
        } catch (ClassNotFoundException e5) {
            throw new RuntimeException(g1Var.getClass().getSimpleName().concat(" does not have a Parcelizer"), e5);
        }
    }
}
