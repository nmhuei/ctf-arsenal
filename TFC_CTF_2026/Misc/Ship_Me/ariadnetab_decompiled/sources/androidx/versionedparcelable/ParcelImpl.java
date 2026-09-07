package androidx.versionedparcelable;

import android.os.Parcel;
import android.os.Parcelable;
import defpackage.f1;
import defpackage.g1;
import defpackage.o0;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public class ParcelImpl implements Parcelable {
    public static final Parcelable.Creator<ParcelImpl> CREATOR = new o0();
    public final g1 a;

    public ParcelImpl(Parcel parcel) {
        this.a = new f1(parcel).g();
    }

    @Override // android.os.Parcelable
    public final int describeContents() {
        return 0;
    }

    @Override // android.os.Parcelable
    public final void writeToParcel(Parcel parcel, int i) {
        new f1(parcel).i(this.a);
    }
}
