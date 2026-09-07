.class final synthetic Lme/ship/PackageCrypto$key$2;
.super Lkotlin/jvm/internal/FunctionReferenceImpl;
.source "PackageCrypto.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function0;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lme/ship/PackageCrypto;-><init>()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1018
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Lkotlin/jvm/internal/FunctionReferenceImpl;",
        "Lkotlin/jvm/functions/Function0<",
        "Ljavax/crypto/SecretKey;",
        ">;"
    }
.end annotation

.annotation runtime Lkotlin/Metadata;
    k = 0x3
    mv = {
        0x2,
        0x2,
        0x0
    }
    xi = 0x30
.end annotation


# direct methods
.method constructor <init>(Ljava/lang/Object;)V
    .locals 7

    const-class v3, Lme/ship/PackageCrypto;

    const-string v5, "loadOrCreateKey()Ljavax/crypto/SecretKey;"

    const/4 v6, 0x0

    const/4 v1, 0x0

    const-string v4, "loadOrCreateKey"

    move-object v0, p0

    move-object v2, p1

    invoke-direct/range {v0 .. v6}, Lkotlin/jvm/internal/FunctionReferenceImpl;-><init>(ILjava/lang/Object;Ljava/lang/Class;Ljava/lang/String;Ljava/lang/String;I)V

    return-void
.end method


# virtual methods
.method public bridge synthetic invoke()Ljava/lang/Object;
    .locals 0

    .line 13
    invoke-virtual {p0}, Lme/ship/PackageCrypto$key$2;->invoke()Ljavax/crypto/SecretKey;

    move-result-object p0

    return-object p0
.end method

.method public final invoke()Ljavax/crypto/SecretKey;
    .locals 0

    .line 13
    iget-object p0, p0, Lme/ship/PackageCrypto$key$2;->receiver:Ljava/lang/Object;

    check-cast p0, Lme/ship/PackageCrypto;

    invoke-static {p0}, Lme/ship/PackageCrypto;->access$loadOrCreateKey(Lme/ship/PackageCrypto;)Ljavax/crypto/SecretKey;

    move-result-object p0

    return-object p0
.end method
