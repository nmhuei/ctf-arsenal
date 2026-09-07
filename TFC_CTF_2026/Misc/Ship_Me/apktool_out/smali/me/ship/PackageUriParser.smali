.class public final Lme/ship/PackageUriParser;
.super Ljava/lang/Object;
.source "PackageUriParser.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nPackageUriParser.kt\nKotlin\n*S Kotlin\n*F\n+ 1 PackageUriParser.kt\nme/ship/PackageUriParser\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n+ 3 _Collections.kt\nkotlin/collections/CollectionsKt___CollectionsKt\n*L\n1#1,55:1\n1#2:56\n1740#3,3:57\n1740#3,3:60\n*S KotlinDebug\n*F\n+ 1 PackageUriParser.kt\nme/ship/PackageUriParser\n*L\n27#1:57,3\n28#1:60,3\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u00002\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0008\u0003\n\u0002\u0010\"\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u0008\n\u0002\u0008\u0003\u0008\u00c6\u0002\u0018\u00002\u00020\u0001B\t\u0008\u0002\u00a2\u0006\u0004\u0008\u0002\u0010\u0003J\u000e\u0010\t\u001a\u00020\n2\u0006\u0010\u000b\u001a\u00020\u000cJ \u0010\r\u001a\u00020\u00062\u0006\u0010\u000b\u001a\u00020\u000c2\u0006\u0010\u000e\u001a\u00020\u00062\u0006\u0010\u000f\u001a\u00020\u0010H\u0002J\"\u0010\u0011\u001a\u0004\u0018\u00010\u00062\u0006\u0010\u000b\u001a\u00020\u000c2\u0006\u0010\u000e\u001a\u00020\u00062\u0006\u0010\u000f\u001a\u00020\u0010H\u0002R\u0014\u0010\u0004\u001a\u0008\u0012\u0004\u0012\u00020\u00060\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\u0008X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0012\u001a\u00020\u0010X\u0082T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0013"
    }
    d2 = {
        "Lme/ship/PackageUriParser;",
        "",
        "<init>",
        "()V",
        "allowedParameters",
        "",
        "",
        "controlCharacters",
        "Lkotlin/text/Regex;",
        "parse",
        "Lme/ship/PackageRequest;",
        "uri",
        "Landroid/net/Uri;",
        "required",
        "key",
        "maxLength",
        "",
        "optional",
        "MAX_URI_LENGTH",
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
.field public static final INSTANCE:Lme/ship/PackageUriParser;

.field private static final MAX_URI_LENGTH:I = 0x800

.field private static final allowedParameters:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private static final controlCharacters:Lkotlin/text/Regex;


# direct methods
.method static constructor <clinit>()V
    .locals 3

    new-instance v0, Lme/ship/PackageUriParser;

    invoke-direct {v0}, Lme/ship/PackageUriParser;-><init>()V

    sput-object v0, Lme/ship/PackageUriParser;->INSTANCE:Lme/ship/PackageUriParser;

    const/4 v0, 0x5

    .line 14
    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "name"

    aput-object v2, v0, v1

    const/4 v1, 0x1

    const-string v2, "origin"

    aput-object v2, v0, v1

    const/4 v1, 0x2

    const-string v2, "destination"

    aput-object v2, v0, v1

    const/4 v1, 0x3

    const-string v2, "description"

    aput-object v2, v0, v1

    const/4 v1, 0x4

    const-string v2, "weight"

    aput-object v2, v0, v1

    invoke-static {v0}, Lkotlin/collections/SetsKt;->setOf([Ljava/lang/Object;)Ljava/util/Set;

    move-result-object v0

    sput-object v0, Lme/ship/PackageUriParser;->allowedParameters:Ljava/util/Set;

    .line 15
    new-instance v0, Lkotlin/text/Regex;

    const-string v1, "[\\p{Cc}\\p{Cf}]"

    invoke-direct {v0, v1}, Lkotlin/text/Regex;-><init>(Ljava/lang/String;)V

    sput-object v0, Lme/ship/PackageUriParser;->controlCharacters:Lkotlin/text/Regex;

    return-void
.end method

.method private constructor <init>()V
    .locals 0

    .line 13
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private final optional(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;
    .locals 1

    .line 46
    invoke-virtual {p1, p2}, Landroid/net/Uri;->getQueryParameter(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    if-eqz p0, :cond_4

    check-cast p0, Ljava/lang/CharSequence;

    invoke-static {p0}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    if-nez p0, :cond_0

    goto :goto_0

    .line 47
    :cond_0
    move-object p1, p0

    check-cast p1, Ljava/lang/CharSequence;

    invoke-interface {p1}, Ljava/lang/CharSequence;->length()I

    move-result v0

    if-lez v0, :cond_3

    .line 48
    invoke-virtual {p0}, Ljava/lang/String;->length()I

    move-result v0

    if-gt v0, p3, :cond_2

    .line 49
    sget-object p3, Lme/ship/PackageUriParser;->controlCharacters:Lkotlin/text/Regex;

    invoke-virtual {p3, p1}, Lkotlin/text/Regex;->containsMatchIn(Ljava/lang/CharSequence;)Z

    move-result p1

    if-nez p1, :cond_1

    return-object p0

    :cond_1
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, " contains control characters"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    new-instance p1, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {p1, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 48
    :cond_2
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, " is too long"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    new-instance p1, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {p1, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 47
    :cond_3
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, " cannot be empty"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    new-instance p1, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {p1, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    :cond_4
    :goto_0
    const/4 p0, 0x0

    return-object p0
.end method

.method private final required(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;
    .locals 0

    .line 43
    invoke-direct {p0, p1, p2, p3}, Lme/ship/PackageUriParser;->optional(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;

    move-result-object p0

    if-eqz p0, :cond_0

    return-object p0

    :cond_0
    new-instance p0, Ljava/lang/IllegalArgumentException;

    new-instance p1, Ljava/lang/StringBuilder;

    const-string p3, "Missing "

    invoke-direct {p1, p3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string p2, " parameter"

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method


# virtual methods
.method public final parse(Landroid/net/Uri;)Lme/ship/PackageRequest;
    .locals 11

    const-string v0, "uri"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 18
    invoke-virtual {p1}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v0

    const/16 v1, 0x800

    if-gt v0, v1, :cond_10

    .line 19
    invoke-virtual {p1}, Landroid/net/Uri;->getScheme()Ljava/lang/String;

    move-result-object v0

    const-string v1, "shipme"

    const/4 v2, 0x0

    invoke-static {v0, v1, v2}, Lkotlin/text/StringsKt;->equals(Ljava/lang/String;Ljava/lang/String;Z)Z

    move-result v0

    if-eqz v0, :cond_f

    .line 20
    invoke-virtual {p1}, Landroid/net/Uri;->getHost()Ljava/lang/String;

    move-result-object v0

    const-string v1, "cargo"

    invoke-static {v0, v1, v2}, Lkotlin/text/StringsKt;->equals(Ljava/lang/String;Ljava/lang/String;Z)Z

    move-result v0

    if-eqz v0, :cond_e

    .line 21
    invoke-virtual {p1}, Landroid/net/Uri;->getPort()I

    move-result v0

    const/4 v1, -0x1

    if-ne v0, v1, :cond_d

    invoke-virtual {p1}, Landroid/net/Uri;->getUserInfo()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_d

    invoke-virtual {p1}, Landroid/net/Uri;->getFragment()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_d

    .line 24
    invoke-virtual {p1}, Landroid/net/Uri;->getPath()Ljava/lang/String;

    move-result-object v0

    check-cast v0, Ljava/lang/CharSequence;

    if-eqz v0, :cond_2

    invoke-interface {v0}, Ljava/lang/CharSequence;->length()I

    move-result v0

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    invoke-virtual {p1}, Landroid/net/Uri;->getPath()Ljava/lang/String;

    move-result-object v0

    const-string v1, "/"

    invoke-static {v0, v1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    goto :goto_0

    :cond_1
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Invalid package URI path"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 26
    :cond_2
    :goto_0
    invoke-virtual {p1}, Landroid/net/Uri;->getQueryParameterNames()Ljava/util/Set;

    move-result-object v0

    .line 27
    invoke-static {v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    check-cast v0, Ljava/lang/Iterable;

    sget-object v1, Lme/ship/PackageUriParser;->allowedParameters:Ljava/util/Set;

    .line 57
    instance-of v2, v0, Ljava/util/Collection;

    if-eqz v2, :cond_3

    move-object v3, v0

    check-cast v3, Ljava/util/Collection;

    invoke-interface {v3}, Ljava/util/Collection;->isEmpty()Z

    move-result v3

    if-eqz v3, :cond_3

    goto :goto_2

    .line 58
    :cond_3
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_1
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v4

    if-eqz v4, :cond_5

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/lang/String;

    .line 27
    invoke-interface {v1, v4}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_4

    goto :goto_1

    :cond_4
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Unknown package URI parameter"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_5
    :goto_2
    if-eqz v2, :cond_6

    .line 60
    move-object v1, v0

    check-cast v1, Ljava/util/Collection;

    invoke-interface {v1}, Ljava/util/Collection;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_6

    goto :goto_4

    .line 61
    :cond_6
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_3
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_8

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/String;

    .line 28
    invoke-virtual {p1, v1}, Landroid/net/Uri;->getQueryParameters(Ljava/lang/String;)Ljava/util/List;

    move-result-object v1

    invoke-interface {v1}, Ljava/util/List;->size()I

    move-result v1

    const/4 v2, 0x1

    if-ne v1, v2, :cond_7

    goto :goto_3

    :cond_7
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Duplicate package URI parameter"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 32
    :cond_8
    :goto_4
    const-string v0, "name"

    const/16 v1, 0xa0

    invoke-direct {p0, p1, v0, v1}, Lme/ship/PackageUriParser;->required(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v3

    .line 33
    const-string v0, "origin"

    const/16 v1, 0x78

    invoke-direct {p0, p1, v0, v1}, Lme/ship/PackageUriParser;->required(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v4

    .line 34
    const-string v0, "destination"

    invoke-direct {p0, p1, v0, v1}, Lme/ship/PackageUriParser;->optional(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_9

    const-string v0, "ship.me hub"

    :cond_9
    move-object v5, v0

    .line 35
    const-string v0, "description"

    const/16 v1, 0x1f4

    invoke-direct {p0, p1, v0, v1}, Lme/ship/PackageUriParser;->optional(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_a

    const-string v0, "Package created through ADB"

    :cond_a
    move-object v6, v0

    .line 36
    const-string v0, "weight"

    const/16 v1, 0x18

    invoke-direct {p0, p1, v0, v1}, Lme/ship/PackageUriParser;->optional(Landroid/net/Uri;Ljava/lang/String;I)Ljava/lang/String;

    move-result-object p0

    const-wide/16 v0, 0x0

    if-eqz p0, :cond_b

    invoke-static {p0}, Lkotlin/text/StringsKt;->toDoubleOrNull(Ljava/lang/String;)Ljava/lang/Double;

    move-result-object p0

    if-eqz p0, :cond_b

    invoke-virtual {p0}, Ljava/lang/Double;->doubleValue()D

    move-result-wide p0

    move-wide v7, p0

    goto :goto_5

    :cond_b
    move-wide v7, v0

    .line 37
    :goto_5
    invoke-static {v7, v8}, Ljava/lang/Math;->abs(D)D

    move-result-wide p0

    const-wide v9, 0x7fefffffffffffffL    # Double.MAX_VALUE

    cmpg-double p0, p0, v9

    if-gtz p0, :cond_c

    cmpg-double p0, v0, v7

    if-gtz p0, :cond_c

    const-wide p0, 0x40f86a0000000000L    # 100000.0

    cmpg-double p0, v7, p0

    if-gtz p0, :cond_c

    .line 39
    new-instance v2, Lme/ship/PackageRequest;

    invoke-direct/range {v2 .. v8}, Lme/ship/PackageRequest;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;D)V

    return-object v2

    .line 37
    :cond_c
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Invalid package weight"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 21
    :cond_d
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Package URI contains unsupported authority data"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 20
    :cond_e
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Invalid package URI host"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 19
    :cond_f
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Invalid package URI scheme"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 18
    :cond_10
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Package URI is too long"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method
