package defpackage;

import android.net.Uri;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Parcel;
import android.os.RemoteException;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final class i0 implements k0 {
    public IBinder d;

    @Override // android.os.IInterface
    public final IBinder asBinder() {
        return this.d;
    }

    public final boolean c(t tVar) {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(k0.b);
            parcelObtain.writeStrongInterface(tVar);
            if (!this.d.transact(3, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method newSession is unimplemented.");
            }
            parcelObtain2.readException();
            boolean z = parcelObtain2.readInt() != 0;
            parcelObtain2.recycle();
            parcelObtain.recycle();
            return z;
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }

    public final int d(t tVar, String str, Bundle bundle) {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(k0.b);
            parcelObtain.writeStrongInterface(tVar);
            parcelObtain.writeString(str);
            parcelObtain.writeTypedObject(bundle, 0);
            if (!this.d.transact(8, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method postMessage is unimplemented.");
            }
            parcelObtain2.readException();
            int i = parcelObtain2.readInt();
            parcelObtain2.recycle();
            parcelObtain.recycle();
            return i;
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }

    public final boolean e(t tVar, Uri uri) {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(k0.b);
            parcelObtain.writeStrongInterface(tVar);
            parcelObtain.writeTypedObject(uri, 0);
            if (!this.d.transact(7, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method requestPostMessageChannel is unimplemented.");
            }
            parcelObtain2.readException();
            boolean z = parcelObtain2.readInt() != 0;
            parcelObtain2.recycle();
            parcelObtain.recycle();
            return z;
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }

    public final boolean f(t tVar, Uri uri, Bundle bundle) {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(k0.b);
            parcelObtain.writeStrongInterface(tVar);
            parcelObtain.writeTypedObject(uri, 0);
            parcelObtain.writeTypedObject(bundle, 0);
            if (!this.d.transact(11, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method requestPostMessageChannelWithExtras is unimplemented.");
            }
            parcelObtain2.readException();
            boolean z = parcelObtain2.readInt() != 0;
            parcelObtain2.recycle();
            parcelObtain.recycle();
            return z;
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }

    public final boolean g() {
        Parcel parcelObtain = Parcel.obtain();
        Parcel parcelObtain2 = Parcel.obtain();
        try {
            parcelObtain.writeInterfaceToken(k0.b);
            parcelObtain.writeLong(0L);
            if (!this.d.transact(2, parcelObtain, parcelObtain2, 0)) {
                throw new RemoteException("Method warmup is unimplemented.");
            }
            parcelObtain2.readException();
            boolean z = parcelObtain2.readInt() != 0;
            parcelObtain2.recycle();
            parcelObtain.recycle();
            return z;
        } catch (Throwable th) {
            parcelObtain2.recycle();
            parcelObtain.recycle();
            throw th;
        }
    }
}
