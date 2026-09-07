package defpackage;

import android.os.Binder;
import android.os.Bundle;
import android.os.IBinder;
import android.os.IInterface;
import android.os.Parcel;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class p0 extends Binder implements l0 {
    @Override // android.os.Binder
    public final boolean onTransact(int i, Parcel parcel, Parcel parcel2, int i2) {
        String str = l0.c;
        if (i >= 1 && i <= 16777215) {
            parcel.enforceInterface(str);
        }
        if (i == 1598968902) {
            parcel2.writeString(str);
            return true;
        }
        if (i == 16777215) {
            parcel2.writeNoException();
            parcel2.writeInt(1);
            return true;
        }
        h0 h0Var = null;
        h0 h0Var2 = null;
        if (i == 2) {
            IBinder strongBinder = parcel.readStrongBinder();
            if (strongBinder != null) {
                IInterface iInterfaceQueryLocalInterface = strongBinder.queryLocalInterface(h0.a);
                if (iInterfaceQueryLocalInterface == null || !(iInterfaceQueryLocalInterface instanceof h0)) {
                    g0 g0Var = new g0();
                    g0Var.d = strongBinder;
                    h0Var = g0Var;
                } else {
                    h0Var = (h0) iInterfaceQueryLocalInterface;
                }
            }
            h0Var.b((Bundle) parcel.readTypedObject(Bundle.CREATOR));
            parcel2.writeNoException();
            return true;
        }
        if (i != 3) {
            return super.onTransact(i, parcel, parcel2, i2);
        }
        IBinder strongBinder2 = parcel.readStrongBinder();
        if (strongBinder2 != null) {
            IInterface iInterfaceQueryLocalInterface2 = strongBinder2.queryLocalInterface(h0.a);
            if (iInterfaceQueryLocalInterface2 == null || !(iInterfaceQueryLocalInterface2 instanceof h0)) {
                g0 g0Var2 = new g0();
                g0Var2.d = strongBinder2;
                h0Var2 = g0Var2;
            } else {
                h0Var2 = (h0) iInterfaceQueryLocalInterface2;
            }
        }
        h0Var2.a(parcel.readString(), (Bundle) parcel.readTypedObject(Bundle.CREATOR));
        parcel2.writeNoException();
        return true;
    }

    @Override // android.os.IInterface
    public final IBinder asBinder() {
        return this;
    }
}
