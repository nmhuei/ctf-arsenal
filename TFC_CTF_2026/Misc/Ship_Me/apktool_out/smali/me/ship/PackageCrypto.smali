.class public final Lme/ship/PackageCrypto;
.super Ljava/lang/Object;
.source "PackageCrypto.kt"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lme/ship/PackageCrypto$Companion;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nPackageCrypto.kt\nKotlin\n*S Kotlin\n*F\n+ 1 PackageCrypto.kt\nme/ship/PackageCrypto\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,58:1\n1#2:59\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u001c\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0005\n\u0002\u0010\u000e\n\u0002\u0008\u0006\u0018\u0000 \u00102\u00020\u0001:\u0001\u0010B\u0007\u00a2\u0006\u0004\u0008\u0002\u0010\u0003J\u000e\u0010\n\u001a\u00020\u000b2\u0006\u0010\u000c\u001a\u00020\u000bJ\u000e\u0010\r\u001a\u00020\u000b2\u0006\u0010\u000e\u001a\u00020\u000bJ\u0008\u0010\u000f\u001a\u00020\u0005H\u0002R\u001b\u0010\u0004\u001a\u00020\u00058BX\u0082\u0084\u0002\u00a2\u0006\u000c\n\u0004\u0008\u0008\u0010\t\u001a\u0004\u0008\u0006\u0010\u0007\u00a8\u0006\u0011"
    }
    d2 = {
        "Lme/ship/PackageCrypto;",
        "",
        "<init>",
        "()V",
        "key",
        "Ljavax/crypto/SecretKey;",
        "getKey",
        "()Ljavax/crypto/SecretKey;",
        "key$delegate",
        "Lkotlin/Lazy;",
        "encrypt",
        "",
        "plaintext",
        "decrypt",
        "storedValue",
        "loadOrCreateKey",
        "Companion",
        "app"
    }
    k = 0x1
    mv = {
        0x2,
        0x2,
        0x0
    }
    xi = 0x30
.end annotation


# static fields
.field public static final Companion:Lme/ship/PackageCrypto$Companion;

.field private static final IV_LENGTH:I = 0xc

.field private static final KEYSTORE_PROVIDER:Ljava/lang/String; = "AndroidKeyStore"

.field private static final KEY_ALIAS:Ljava/lang/String; = "ship.me.package.metadata.v1"

.field private static final PREFIX:Ljava/lang/String; = "encrypted:v1:"

.field private static final TRANSFORMATION:Ljava/lang/String; = "AES/GCM/NoPadding"


# instance fields
.field private final key$delegate:Lkotlin/Lazy;


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lme/ship/PackageCrypto$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lme/ship/PackageCrypto$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lme/ship/PackageCrypto;->Companion:Lme/ship/PackageCrypto$Companion;

    return-void
.end method

.method public constructor <init>()V
    .locals 1

    .line 12
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 13
    new-instance v0, Lme/ship/PackageCrypto$key$2;

    invoke-direct {v0, p0}, Lme/ship/PackageCrypto$key$2;-><init>(Ljava/lang/Object;)V

    check-cast v0, Lkotlin/jvm/functions/Function0;

    invoke-static {v0}, Lkotlin/LazyKt;->lazy(Lkotlin/jvm/functions/Function0;)Lkotlin/Lazy;

    move-result-object v0

    iput-object v0, p0, Lme/ship/PackageCrypto;->key$delegate:Lkotlin/Lazy;

    return-void
.end method

.method public static final synthetic access$loadOrCreateKey(Lme/ship/PackageCrypto;)Ljavax/crypto/SecretKey;
    .locals 0

    .line 12
    invoke-direct {p0}, Lme/ship/PackageCrypto;->loadOrCreateKey()Ljavax/crypto/SecretKey;

    move-result-object p0

    return-object p0
.end method

.method private final getKey()Ljavax/crypto/SecretKey;
    .locals 0

    .line 13
    iget-object p0, p0, Lme/ship/PackageCrypto;->key$delegate:Lkotlin/Lazy;

    invoke-interface {p0}, Lkotlin/Lazy;->getValue()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljavax/crypto/SecretKey;

    return-object p0
.end method

.method private final loadOrCreateKey()Ljavax/crypto/SecretKey;
    .locals 5

    .line 32
    const-string p0, "AndroidKeyStore"

    invoke-static {p0}, Ljava/security/KeyStore;->getInstance(Ljava/lang/String;)Ljava/security/KeyStore;

    move-result-object v0

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Ljava/security/KeyStore;->load(Ljava/security/KeyStore$LoadStoreParameter;)V

    .line 33
    const-string v2, "ship.me.package.metadata.v1"

    invoke-virtual {v0, v2, v1}, Ljava/security/KeyStore;->getKey(Ljava/lang/String;[C)Ljava/security/Key;

    move-result-object v0

    instance-of v3, v0, Ljavax/crypto/SecretKey;

    if-eqz v3, :cond_0

    move-object v1, v0

    check-cast v1, Ljavax/crypto/SecretKey;

    :cond_0
    if-eqz v1, :cond_1

    return-object v1

    .line 34
    :cond_1
    const-string v0, "AES"

    invoke-static {v0, p0}, Ljavax/crypto/KeyGenerator;->getInstance(Ljava/lang/String;Ljava/lang/String;)Ljavax/crypto/KeyGenerator;

    move-result-object p0

    .line 36
    new-instance v0, Landroid/security/keystore/KeyGenParameterSpec$Builder;

    const/4 v1, 0x3

    invoke-direct {v0, v2, v1}, Landroid/security/keystore/KeyGenParameterSpec$Builder;-><init>(Ljava/lang/String;I)V

    const/4 v1, 0x1

    .line 40
    new-array v2, v1, [Ljava/lang/String;

    const-string v3, "GCM"

    const/4 v4, 0x0

    aput-object v3, v2, v4

    invoke-virtual {v0, v2}, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setBlockModes([Ljava/lang/String;)Landroid/security/keystore/KeyGenParameterSpec$Builder;

    move-result-object v0

    .line 41
    new-array v2, v1, [Ljava/lang/String;

    const-string v3, "NoPadding"

    aput-object v3, v2, v4

    invoke-virtual {v0, v2}, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setEncryptionPaddings([Ljava/lang/String;)Landroid/security/keystore/KeyGenParameterSpec$Builder;

    move-result-object v0

    const/16 v2, 0x100

    .line 42
    invoke-virtual {v0, v2}, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setKeySize(I)Landroid/security/keystore/KeyGenParameterSpec$Builder;

    move-result-object v0

    .line 43
    invoke-virtual {v0, v1}, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setRandomizedEncryptionRequired(Z)Landroid/security/keystore/KeyGenParameterSpec$Builder;

    move-result-object v0

    .line 44
    invoke-virtual {v0}, Landroid/security/keystore/KeyGenParameterSpec$Builder;->build()Landroid/security/keystore/KeyGenParameterSpec;

    move-result-object v0

    check-cast v0, Ljava/security/spec/AlgorithmParameterSpec;

    .line 35
    invoke-virtual {p0, v0}, Ljavax/crypto/KeyGenerator;->init(Ljava/security/spec/AlgorithmParameterSpec;)V

    .line 46
    invoke-virtual {p0}, Ljavax/crypto/KeyGenerator;->generateKey()Ljavax/crypto/SecretKey;

    move-result-object p0

    .line 34
    const-string v0, "run(...)"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0
.end method


# virtual methods
.method public final decrypt(Ljava/lang/String;)Ljava/lang/String;
    .locals 6

    const-string v0, "storedValue"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const/4 v0, 0x0

    .line 23
    const-string v1, "encrypted:v1:"

    const/4 v2, 0x0

    const/4 v3, 0x2

    invoke-static {p1, v1, v2, v3, v0}, Lkotlin/text/StringsKt;->startsWith$default(Ljava/lang/String;Ljava/lang/String;ZILjava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    return-object p1

    .line 24
    :cond_0
    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {p1, v1}, Lkotlin/text/StringsKt;->removePrefix(Ljava/lang/String;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object p1

    invoke-static {p1, v3}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object p1

    .line 25
    array-length v0, p1

    const/16 v1, 0xc

    if-le v0, v1, :cond_1

    .line 26
    const-string v0, "AES/GCM/NoPadding"

    invoke-static {v0}, Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;

    move-result-object v0

    .line 27
    invoke-direct {p0}, Lme/ship/PackageCrypto;->getKey()Ljavax/crypto/SecretKey;

    move-result-object p0

    check-cast p0, Ljava/security/Key;

    new-instance v4, Ljavax/crypto/spec/GCMParameterSpec;

    invoke-static {p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {p1, v2, v1}, Lkotlin/collections/ArraysKt;->copyOfRange([BII)[B

    move-result-object v2

    const/16 v5, 0x80

    invoke-direct {v4, v5, v2}, Ljavax/crypto/spec/GCMParameterSpec;-><init>(I[B)V

    check-cast v4, Ljava/security/spec/AlgorithmParameterSpec;

    invoke-virtual {v0, v3, p0, v4}, Ljavax/crypto/Cipher;->init(ILjava/security/Key;Ljava/security/spec/AlgorithmParameterSpec;)V

    .line 28
    array-length p0, p1

    invoke-static {p1, v1, p0}, Lkotlin/collections/ArraysKt;->copyOfRange([BII)[B

    move-result-object p0

    invoke-virtual {v0, p0}, Ljavax/crypto/Cipher;->doFinal([B)[B

    move-result-object p0

    const-string p1, "doFinal(...)"

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    sget-object p1, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    new-instance v0, Ljava/lang/String;

    invoke-direct {v0, p0, p1}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V

    return-object v0

    .line 25
    :cond_1
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Invalid encrypted package value"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public final encrypt(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    const-string v0, "plaintext"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 16
    const-string v0, "AES/GCM/NoPadding"

    invoke-static {v0}, Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;

    move-result-object v0

    .line 17
    invoke-direct {p0}, Lme/ship/PackageCrypto;->getKey()Ljavax/crypto/SecretKey;

    move-result-object p0

    check-cast p0, Ljava/security/Key;

    const/4 v1, 0x1

    invoke-virtual {v0, v1, p0}, Ljavax/crypto/Cipher;->init(ILjava/security/Key;)V

    .line 18
    invoke-virtual {v0}, Ljavax/crypto/Cipher;->getIV()[B

    move-result-object p0

    const-string v1, "getIV(...)"

    invoke-static {p0, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    sget-object v1, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {p1, v1}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object p1

    const-string v1, "getBytes(...)"

    invoke-static {p1, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0, p1}, Ljavax/crypto/Cipher;->doFinal([B)[B

    move-result-object p1

    const-string v0, "doFinal(...)"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-static {p0, p1}, Lkotlin/collections/ArraysKt;->plus([B[B)[B

    move-result-object p0

    const/4 p1, 0x2

    .line 19
    invoke-static {p0, p1}, Landroid/util/Base64;->encodeToString([BI)Ljava/lang/String;

    move-result-object p0

    new-instance p1, Ljava/lang/StringBuilder;

    const-string v0, "encrypted:v1:"

    invoke-direct {p1, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
