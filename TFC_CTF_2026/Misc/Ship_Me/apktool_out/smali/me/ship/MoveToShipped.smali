.class public final Lme/ship/MoveToShipped;
.super Ljava/lang/Throwable;
.source "MoveToShipped.kt"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lme/ship/MoveToShipped$Companion;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nMoveToShipped.kt\nKotlin\n*S Kotlin\n*F\n+ 1 MoveToShipped.kt\nme/ship/MoveToShipped\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,45:1\n1#2:46\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0003\n\u0000\n\u0002\u0010\t\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\u0008\u0005\u0018\u0000 \r2\u00020\u0001:\u0001\rB\u000f\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0004\u0008\u0004\u0010\u0005J\u0008\u0010\u000c\u001a\u00020\u0007H\u0002R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0006\u001a\u0004\u0018\u00010\u0007X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u0008\u001a\u00020\t8VX\u0096\u0004\u00a2\u0006\u0006\u001a\u0004\u0008\n\u0010\u000b\u00a8\u0006\u000e"
    }
    d2 = {
        "Lme/ship/MoveToShipped;",
        "",
        "packageId",
        "",
        "<init>",
        "(J)V",
        "shipment",
        "Lme/ship/Shipment;",
        "message",
        "",
        "getMessage",
        "()Ljava/lang/String;",
        "refreshTrackingStatus",
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
.field public static final Companion:Lme/ship/MoveToShipped$Companion;

.field private static final serialVersionUID:J = 0x1L


# instance fields
.field private final packageId:J

.field private transient shipment:Lme/ship/Shipment;


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lme/ship/MoveToShipped$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lme/ship/MoveToShipped$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lme/ship/MoveToShipped;->Companion:Lme/ship/MoveToShipped$Companion;

    return-void
.end method

.method public constructor <init>(J)V
    .locals 0

    .line 5
    invoke-direct {p0}, Ljava/lang/Throwable;-><init>()V

    .line 4
    iput-wide p1, p0, Lme/ship/MoveToShipped;->packageId:J

    .line 14
    invoke-direct {p0}, Lme/ship/MoveToShipped;->refreshTrackingStatus()Lme/ship/Shipment;

    move-result-object p1

    iput-object p1, p0, Lme/ship/MoveToShipped;->shipment:Lme/ship/Shipment;

    return-void
.end method

.method private final refreshTrackingStatus()Lme/ship/Shipment;
    .locals 5

    .line 26
    sget-object v0, Lme/ship/ShipMeDatabase;->Companion:Lme/ship/ShipMeDatabase$Companion;

    sget-object v1, Lme/ship/ShipMeApplication;->Companion:Lme/ship/ShipMeApplication$Companion;

    invoke-virtual {v1}, Lme/ship/ShipMeApplication$Companion;->getInstance()Lme/ship/ShipMeApplication;

    move-result-object v1

    check-cast v1, Landroid/content/Context;

    invoke-virtual {v0, v1}, Lme/ship/ShipMeDatabase$Companion;->getInstance(Landroid/content/Context;)Lme/ship/ShipMeDatabase;

    move-result-object v0

    .line 27
    iget-wide v1, p0, Lme/ship/MoveToShipped;->packageId:J

    invoke-virtual {v0, v1, v2}, Lme/ship/ShipMeDatabase;->getPackage(J)Lme/ship/Shipment;

    move-result-object v1

    const-string v2, "Package #"

    if-eqz v1, :cond_3

    .line 32
    invoke-virtual {v1}, Lme/ship/Shipment;->getStatus()Lme/ship/PackageStatus;

    move-result-object v1

    sget-object v3, Lme/ship/PackageStatus;->READY_TO_SHIP:Lme/ship/PackageStatus;

    if-ne v1, v3, :cond_1

    .line 33
    iget-wide v3, p0, Lme/ship/MoveToShipped;->packageId:J

    invoke-virtual {v0, v3, v4}, Lme/ship/ShipMeDatabase;->moveToShipped$app(J)Z

    move-result v1

    if-eqz v1, :cond_0

    goto :goto_0

    .line 34
    :cond_0
    iget-wide v0, p0, Lme/ship/MoveToShipped;->packageId:J

    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " could not be moved to shipped"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 33
    new-instance v0, Ljava/lang/IllegalStateException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v0, p0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 38
    :cond_1
    :goto_0
    iget-wide v3, p0, Lme/ship/MoveToShipped;->packageId:J

    invoke-virtual {v0, v3, v4}, Lme/ship/ShipMeDatabase;->getPackage(J)Lme/ship/Shipment;

    move-result-object v0

    if-eqz v0, :cond_2

    return-object v0

    .line 39
    :cond_2
    iget-wide v0, p0, Lme/ship/MoveToShipped;->packageId:J

    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " disappeared after its status update"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 38
    new-instance v0, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v0, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 28
    :cond_3
    iget-wide v0, p0, Lme/ship/MoveToShipped;->packageId:J

    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " does not exist"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 27
    new-instance v0, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v0, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v0
.end method


# virtual methods
.method public getMessage()Ljava/lang/String;
    .locals 3

    .line 19
    iget-object v0, p0, Lme/ship/MoveToShipped;->shipment:Lme/ship/Shipment;

    if-nez v0, :cond_0

    .line 20
    invoke-direct {p0}, Lme/ship/MoveToShipped;->refreshTrackingStatus()Lme/ship/Shipment;

    move-result-object v0

    iput-object v0, p0, Lme/ship/MoveToShipped;->shipment:Lme/ship/Shipment;

    .line 22
    :cond_0
    invoke-virtual {v0}, Lme/ship/Shipment;->getId()J

    move-result-wide v0

    new-instance p0, Ljava/lang/StringBuilder;

    const-string v2, "Package #"

    invoke-direct {p0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " tracking status refreshed"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
