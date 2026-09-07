.class public Lme/ship/Exfil;
.super Ljava/lang/Object;
.source "Exfil.java"

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static dumpIntent(Landroid/content/Intent;)V
    .registers 3
    invoke-static {p0}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v1
    const-string v0, "TFCCTF_FLAG"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    return-void
.end method

.method public static send(Ljava/lang/String;)V
    .registers 2
    if-eqz p0, :done
    const-string v0, "TFCCTF_FLAG"
    invoke-static {v0, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
:done
    return-void
.end method
