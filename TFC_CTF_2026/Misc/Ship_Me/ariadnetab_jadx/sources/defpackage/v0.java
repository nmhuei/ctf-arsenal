package defpackage;

import android.view.Choreographer;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public abstract class v0 {
    public static void a(final Runnable runnable) {
        Choreographer.getInstance().postFrameCallback(new Choreographer.FrameCallback() { // from class: u0
            @Override // android.view.Choreographer.FrameCallback
            public final void doFrame(long j) {
                runnable.run();
            }
        });
    }
}
