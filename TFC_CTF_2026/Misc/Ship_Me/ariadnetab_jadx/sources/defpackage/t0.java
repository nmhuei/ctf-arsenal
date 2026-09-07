package defpackage;

import android.content.Context;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import androidx.profileinstaller.ProfileInstallerInitializer;
import java.util.Random;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public final /* synthetic */ class t0 implements Runnable {
    public final /* synthetic */ int a;
    public final /* synthetic */ Context b;

    public /* synthetic */ t0(ProfileInstallerInitializer profileInstallerInitializer, Context context) {
        this.a = 0;
        this.b = context;
    }

    @Override // java.lang.Runnable
    public final void run() {
        int i = this.a;
        Context context = this.b;
        switch (i) {
            case 0:
                (Build.VERSION.SDK_INT >= 28 ? x0.a(Looper.getMainLooper()) : new Handler(Looper.getMainLooper())).postDelayed(new t0(context, 1), new Random().nextInt(Math.max(1000, 1)) + 5000);
                break;
            case 1:
                new ThreadPoolExecutor(0, 1, 0L, TimeUnit.MILLISECONDS, new LinkedBlockingQueue()).execute(new t0(context, 2));
                break;
            default:
                y.B(context, new q0(), y.c, false);
                break;
        }
    }

    public /* synthetic */ t0(Context context, int i) {
        this.a = i;
        this.b = context;
    }
}
