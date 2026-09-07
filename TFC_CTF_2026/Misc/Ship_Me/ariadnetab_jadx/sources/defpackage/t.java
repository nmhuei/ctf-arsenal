package defpackage;

import android.net.Uri;
import android.os.Binder;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Parcel;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class t extends Binder implements h0 {
    public final Handler d;
    public final /* synthetic */ d0 e;

    public t(d0 d0Var) {
        this.e = d0Var;
        attachInterface(this, h0.a);
        this.d = new Handler(Looper.getMainLooper());
    }

    @Override // defpackage.h0
    public final void a(String str, Bundle bundle) {
        this.d.post(new s(this, str, bundle));
    }

    @Override // defpackage.h0
    public final void b(Bundle bundle) {
        this.d.post(new r(this, bundle));
    }

    @Override // android.os.Binder
    public final boolean onTransact(int i, Parcel parcel, Parcel parcel2, int i2) {
        String str = h0.a;
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
        Handler handler = this.d;
        switch (i) {
            case 2:
                handler.post(new q(parcel.readInt(), this, (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 3:
                handler.post(new p(this, parcel.readString(), (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 4:
                b((Bundle) parcel.readTypedObject(Bundle.CREATOR));
                parcel2.writeNoException();
                return true;
            case 5:
                a(parcel.readString(), (Bundle) parcel.readTypedObject(Bundle.CREATOR));
                parcel2.writeNoException();
                return true;
            case 6:
                handler.post(new p(this, parcel.readInt(), (Uri) parcel.readTypedObject(Uri.CREATOR), parcel.readInt() != 0, (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 7:
                parcel.readString();
                parcel2.writeNoException();
                parcel2.writeTypedObject(null, 1);
                return true;
            case 8:
                handler.post(new p(this, parcel.readInt(), parcel.readInt(), (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 9:
                handler.post(new p(4, this, (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 10:
                handler.post(new p(this, parcel.readInt(), parcel.readInt(), parcel.readInt(), parcel.readInt(), parcel.readInt(), (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 11:
                handler.post(new p(6, this, (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            case 12:
                handler.post(new p(0, this, (Bundle) parcel.readTypedObject(Bundle.CREATOR)));
                return true;
            default:
                return super.onTransact(i, parcel, parcel2, i2);
        }
    }

    @Override // android.os.IInterface
    public final IBinder asBinder() {
        return this;
    }
}
