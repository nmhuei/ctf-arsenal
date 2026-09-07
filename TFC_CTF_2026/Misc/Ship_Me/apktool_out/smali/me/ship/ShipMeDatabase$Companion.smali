.class public final Lme/ship/ShipMeDatabase$Companion;
.super Ljava/lang/Object;
.source "ShipMeDatabase.kt"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lme/ship/ShipMeDatabase;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x19
    name = "Companion"
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nShipMeDatabase.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ShipMeDatabase.kt\nme/ship/ShipMeDatabase$Companion\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,235:1\n1#2:236\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u00000\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\u0008\u0003\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u0008\n\u0002\u0008\u000c\n\u0002\u0010\u0011\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\u0008\u0086\u0003\u0018\u00002\u00020\u0001B\t\u0008\u0002\u00a2\u0006\u0004\u0008\u0002\u0010\u0003J\u000e\u0010\u0018\u001a\u00020\u00172\u0006\u0010\u0019\u001a\u00020\u001aR\u000e\u0010\u0004\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0008\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000b\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000c\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\r\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000e\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000f\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0010\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0011\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0012\u001a\u00020\u0005X\u0082T\u00a2\u0006\u0002\n\u0000R\u0016\u0010\u0013\u001a\u0008\u0012\u0004\u0012\u00020\u00050\u0014X\u0082\u0004\u00a2\u0006\u0004\n\u0002\u0010\u0015R\u0010\u0010\u0016\u001a\u0004\u0018\u00010\u0017X\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u001b"
    }
    d2 = {
        "Lme/ship/ShipMeDatabase$Companion;",
        "",
        "<init>",
        "()V",
        "DATABASE_NAME",
        "",
        "DATABASE_VERSION",
        "",
        "TABLE_PACKAGES",
        "COLUMN_ID",
        "COLUMN_NAME",
        "COLUMN_ORIGIN",
        "COLUMN_DESTINATION",
        "COLUMN_DESCRIPTION",
        "COLUMN_WEIGHT_KG",
        "COLUMN_IMAGE_KEY",
        "COLUMN_STATUS",
        "COLUMN_CREATED_AT",
        "COLUMN_SHIPPED_AT",
        "ALL_COLUMNS",
        "",
        "[Ljava/lang/String;",
        "instance",
        "Lme/ship/ShipMeDatabase;",
        "getInstance",
        "context",
        "Landroid/content/Context;",
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


# direct methods
.method private constructor <init>()V
    .locals 0

    .line 205
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public synthetic constructor <init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V
    .locals 0

    invoke-direct {p0}, Lme/ship/ShipMeDatabase$Companion;-><init>()V

    return-void
.end method


# virtual methods
.method public final getInstance(Landroid/content/Context;)Lme/ship/ShipMeDatabase;
    .locals 2

    const-string v0, "context"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 230
    invoke-static {}, Lme/ship/ShipMeDatabase;->access$getInstance$cp()Lme/ship/ShipMeDatabase;

    move-result-object v0

    if-nez v0, :cond_1

    monitor-enter p0

    .line 231
    :try_start_0
    invoke-static {}, Lme/ship/ShipMeDatabase;->access$getInstance$cp()Lme/ship/ShipMeDatabase;

    move-result-object v0

    if-nez v0, :cond_0

    new-instance v0, Lme/ship/ShipMeDatabase;

    const/4 v1, 0x0

    invoke-direct {v0, p1, v1}, Lme/ship/ShipMeDatabase;-><init>(Landroid/content/Context;Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sget-object p1, Lme/ship/ShipMeDatabase;->Companion:Lme/ship/ShipMeDatabase$Companion;

    invoke-static {v0}, Lme/ship/ShipMeDatabase;->access$setInstance$cp(Lme/ship/ShipMeDatabase;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 230
    :cond_0
    monitor-exit p0

    return-object v0

    :catchall_0
    move-exception p1

    monitor-exit p0

    throw p1

    :cond_1
    return-object v0
.end method
