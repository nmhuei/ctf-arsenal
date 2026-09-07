package defpackage;

import java.util.Locale;
import java.util.concurrent.CancellationException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicReferenceFieldUpdater;
import java.util.concurrent.locks.LockSupport;
import java.util.logging.Level;
import java.util.logging.Logger;

/* JADX INFO: compiled from: r8-map-id-4a208f9004bc1f0f4dafeaa79198ab0076ee4b0cab8b03d820e7580917904a42 */
/* JADX INFO: loaded from: classes.dex */
public abstract class g implements Future {
    public static final boolean d = Boolean.parseBoolean(System.getProperty("guava.concurrent.generate_cancellation_cause", "false"));
    public static final Logger e = Logger.getLogger(g.class.getName());
    public static final y f;
    public static final Object g;
    public volatile Object a;
    public volatile c b;
    public volatile f c;

    static {
        y eVar;
        try {
            eVar = new d(AtomicReferenceFieldUpdater.newUpdater(f.class, Thread.class, "a"), AtomicReferenceFieldUpdater.newUpdater(f.class, f.class, "b"), AtomicReferenceFieldUpdater.newUpdater(g.class, f.class, "c"), AtomicReferenceFieldUpdater.newUpdater(g.class, c.class, "b"), AtomicReferenceFieldUpdater.newUpdater(g.class, Object.class, "a"));
            th = null;
        } catch (Throwable th) {
            th = th;
            eVar = new e();
        }
        f = eVar;
        if (th != null) {
            e.log(Level.SEVERE, "SafeAtomicHelper is broken!", th);
        }
        g = new Object();
    }

    public static void b(g gVar) {
        f fVar;
        c cVar;
        do {
            fVar = gVar.c;
        } while (!f.e(gVar, fVar, f.c));
        while (fVar != null) {
            Thread thread = fVar.a;
            if (thread != null) {
                fVar.a = null;
                LockSupport.unpark(thread);
            }
            fVar = fVar.b;
        }
        do {
            cVar = gVar.b;
        } while (!f.c(gVar, cVar));
        c cVar2 = null;
        while (cVar != null) {
            c cVar3 = cVar.a;
            cVar.a = cVar2;
            cVar2 = cVar;
            cVar = cVar3;
        }
        while (cVar2 != null) {
            cVar2 = cVar2.a;
            try {
                throw null;
            } catch (RuntimeException e2) {
                e.log(Level.SEVERE, "RuntimeException while executing runnable null with executor null", (Throwable) e2);
            }
        }
    }

    public static Object c(Object obj) throws ExecutionException {
        if (obj instanceof a) {
            Throwable th = ((a) obj).a;
            CancellationException cancellationException = new CancellationException("Task was cancelled.");
            cancellationException.initCause(th);
            throw cancellationException;
        }
        if (obj instanceof b) {
            throw new ExecutionException((Throwable) null);
        }
        if (obj == g) {
            return null;
        }
        return obj;
    }

    public static Object d(g gVar) {
        Object obj;
        boolean z = false;
        while (true) {
            try {
                obj = gVar.get();
                break;
            } catch (InterruptedException unused) {
                z = true;
            } catch (Throwable th) {
                if (z) {
                    Thread.currentThread().interrupt();
                }
                throw th;
            }
        }
        if (z) {
            Thread.currentThread().interrupt();
        }
        return obj;
    }

    public final void a(StringBuilder sb) {
        try {
            Object objD = d(this);
            sb.append("SUCCESS, result=[");
            sb.append(objD == this ? "this future" : String.valueOf(objD));
            sb.append("]");
        } catch (CancellationException unused) {
            sb.append("CANCELLED");
        } catch (RuntimeException e2) {
            sb.append("UNKNOWN, cause=[");
            sb.append(e2.getClass());
            sb.append(" thrown from get()]");
        } catch (ExecutionException e3) {
            sb.append("FAILURE, cause=[");
            sb.append(e3.getCause());
            sb.append("]");
        }
    }

    @Override // java.util.concurrent.Future
    public final boolean cancel(boolean z) {
        a aVar;
        Object obj = this.a;
        if (obj != null) {
            return false;
        }
        if (d) {
            aVar = new a(z, new CancellationException("Future.cancel() was called."));
        } else {
            aVar = z ? a.b : a.c;
        }
        if (!f.d(this, obj, aVar)) {
            return false;
        }
        b(this);
        return true;
    }

    public final void e(f fVar) {
        fVar.a = null;
        while (true) {
            f fVar2 = this.c;
            if (fVar2 == f.c) {
                return;
            }
            f fVar3 = null;
            while (fVar2 != null) {
                f fVar4 = fVar2.b;
                if (fVar2.a != null) {
                    fVar3 = fVar2;
                } else if (fVar3 != null) {
                    fVar3.b = fVar4;
                    if (fVar3.a == null) {
                    }
                } else if (!f.e(this, fVar2, fVar4)) {
                }
                fVar2 = fVar4;
            }
            return;
        }
    }

    @Override // java.util.concurrent.Future
    public final Object get(long j, TimeUnit timeUnit) throws InterruptedException, TimeoutException {
        f fVar = f.c;
        long nanos = timeUnit.toNanos(j);
        if (Thread.interrupted()) {
            throw new InterruptedException();
        }
        Object obj = this.a;
        if (obj != null) {
            return c(obj);
        }
        long jNanoTime = nanos > 0 ? System.nanoTime() + nanos : 0L;
        if (nanos >= 1000) {
            f fVar2 = this.c;
            if (fVar2 != fVar) {
                f fVar3 = new f();
                while (true) {
                    y yVar = f;
                    yVar.m(fVar3, fVar2);
                    if (yVar.e(this, fVar2, fVar3)) {
                        do {
                            LockSupport.parkNanos(this, nanos);
                            if (Thread.interrupted()) {
                                e(fVar3);
                                throw new InterruptedException();
                            }
                            Object obj2 = this.a;
                            if (obj2 != null) {
                                return c(obj2);
                            }
                            nanos = jNanoTime - System.nanoTime();
                        } while (nanos >= 1000);
                        e(fVar3);
                        break;
                    }
                    fVar2 = this.c;
                    if (fVar2 == fVar) {
                    }
                }
            }
            return c(this.a);
        }
        while (nanos > 0) {
            Object obj3 = this.a;
            if (obj3 != null) {
                return c(obj3);
            }
            if (Thread.interrupted()) {
                throw new InterruptedException();
            }
            nanos = jNanoTime - System.nanoTime();
        }
        String string = toString();
        String string2 = timeUnit.toString();
        Locale locale = Locale.ROOT;
        String lowerCase = string2.toLowerCase(locale);
        String strConcat = "Waited " + j + " " + timeUnit.toString().toLowerCase(locale);
        if (nanos + 1000 < 0) {
            String strConcat2 = strConcat.concat(" (plus ");
            long j2 = -nanos;
            long jConvert = timeUnit.convert(j2, TimeUnit.NANOSECONDS);
            long nanos2 = j2 - timeUnit.toNanos(jConvert);
            boolean z = jConvert == 0 || nanos2 > 1000;
            if (jConvert > 0) {
                String strConcat3 = strConcat2 + jConvert + " " + lowerCase;
                if (z) {
                    strConcat3 = strConcat3.concat(",");
                }
                strConcat2 = strConcat3.concat(" ");
            }
            if (z) {
                strConcat2 = strConcat2 + nanos2 + " nanoseconds ";
            }
            strConcat = strConcat2.concat("delay)");
        }
        if (isDone()) {
            throw new TimeoutException(strConcat.concat(" but future completed as timeout expired"));
        }
        throw new TimeoutException(strConcat + " for " + string);
    }

    @Override // java.util.concurrent.Future
    public final boolean isCancelled() {
        return this.a instanceof a;
    }

    @Override // java.util.concurrent.Future
    public final boolean isDone() {
        return this.a != null;
    }

    /* JADX WARN: Multi-variable type inference failed */
    public final String toString() {
        String str;
        StringBuilder sb = new StringBuilder();
        sb.append(super.toString());
        sb.append("[status=");
        if (this.a instanceof a) {
            sb.append("CANCELLED");
        } else if (isDone()) {
            a(sb);
        } else {
            try {
                if (this instanceof ScheduledFuture) {
                    str = "remaining delay=[" + ((ScheduledFuture) this).getDelay(TimeUnit.MILLISECONDS) + " ms]";
                } else {
                    str = null;
                }
            } catch (RuntimeException e2) {
                str = "Exception thrown from implementation: " + e2.getClass();
            }
            if (str != null && !str.isEmpty()) {
                sb.append("PENDING, info=[");
                sb.append(str);
                sb.append("]");
            } else if (isDone()) {
                a(sb);
            } else {
                sb.append("PENDING");
            }
        }
        sb.append("]");
        return sb.toString();
    }

    @Override // java.util.concurrent.Future
    public final Object get() throws InterruptedException {
        Object obj;
        f fVar = f.c;
        if (!Thread.interrupted()) {
            Object obj2 = this.a;
            if (obj2 != null) {
                return c(obj2);
            }
            f fVar2 = this.c;
            if (fVar2 != fVar) {
                f fVar3 = new f();
                do {
                    y yVar = f;
                    yVar.m(fVar3, fVar2);
                    if (yVar.e(this, fVar2, fVar3)) {
                        do {
                            LockSupport.park(this);
                            if (!Thread.interrupted()) {
                                obj = this.a;
                            } else {
                                e(fVar3);
                                throw new InterruptedException();
                            }
                        } while (obj == null);
                        return c(obj);
                    }
                    fVar2 = this.c;
                } while (fVar2 != fVar);
            }
            return c(this.a);
        }
        throw new InterruptedException();
    }
}
