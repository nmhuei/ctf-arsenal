package defpackage;

import android.os.Bundle;
import android.os.IBinder;
import android.os.Parcel;
import android.os.RemoteException;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class g0 implements h0 {
    public IBinder d;

    @Override // defpackage.h0
    public final void a(String str, Bundle bundle) {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(h0.a);
            parcelObtain.writeString(str);
            parcelObtain.writeTypedObject(bundle, 0);
            if (!this.d.transact(5, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method onPostMessage is unimplemented.");
            }
            parcelObtain2.readException();
            parcelObtain2.recycle();
            parcelObtain.recycle();
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }

    @Override // android.os.IInterface
    public final IBinder asBinder() {
        return this.d;
    }

    @Override // defpackage.h0
    public final void b(Bundle bundle) {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(h0.a);
            parcelObtain.writeTypedObject(bundle, 0);
            if (!this.d.transact(4, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method onMessageChannelReady is unimplemented.");
            }
            parcelObtain2.readException();
            parcelObtain2.recycle();
            parcelObtain.recycle();
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }
}
