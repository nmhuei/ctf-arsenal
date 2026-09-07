.class public final Lme/ship/Shipment;
.super Ljava/lang/Object;
.source "Shipment.kt"


# annotations
.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u00008\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\t\n\u0000\n\u0002\u0010\u000e\n\u0002\u0008\u0004\n\u0002\u0010\u0006\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008!\n\u0002\u0010\u000b\n\u0002\u0008\u0002\n\u0002\u0010\u0008\n\u0002\u0008\u0002\u0008\u0086\u0008\u0018\u00002\u00020\u0001B[\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\u0006\u0010\u0006\u001a\u00020\u0005\u0012\u0006\u0010\u0007\u001a\u00020\u0005\u0012\u0006\u0010\u0008\u001a\u00020\u0005\u0012\u0006\u0010\t\u001a\u00020\n\u0012\u0008\u0010\u000b\u001a\u0004\u0018\u00010\u0005\u0012\u0006\u0010\u000c\u001a\u00020\r\u0012\u0006\u0010\u000e\u001a\u00020\u0003\u0012\u0008\u0010\u000f\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\u0004\u0008\u0010\u0010\u0011J\t\u0010\"\u001a\u00020\u0003H\u00c6\u0003J\t\u0010#\u001a\u00020\u0005H\u00c6\u0003J\t\u0010$\u001a\u00020\u0005H\u00c6\u0003J\t\u0010%\u001a\u00020\u0005H\u00c6\u0003J\t\u0010&\u001a\u00020\u0005H\u00c6\u0003J\t\u0010\'\u001a\u00020\nH\u00c6\u0003J\u000b\u0010(\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003J\t\u0010)\u001a\u00020\rH\u00c6\u0003J\t\u0010*\u001a\u00020\u0003H\u00c6\u0003J\u0010\u0010+\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003\u00a2\u0006\u0002\u0010 Jv\u0010,\u001a\u00020\u00002\u0008\u0008\u0002\u0010\u0002\u001a\u00020\u00032\u0008\u0008\u0002\u0010\u0004\u001a\u00020\u00052\u0008\u0008\u0002\u0010\u0006\u001a\u00020\u00052\u0008\u0008\u0002\u0010\u0007\u001a\u00020\u00052\u0008\u0008\u0002\u0010\u0008\u001a\u00020\u00052\u0008\u0008\u0002\u0010\t\u001a\u00020\n2\n\u0008\u0002\u0010\u000b\u001a\u0004\u0018\u00010\u00052\u0008\u0008\u0002\u0010\u000c\u001a\u00020\r2\u0008\u0008\u0002\u0010\u000e\u001a\u00020\u00032\n\u0008\u0002\u0010\u000f\u001a\u0004\u0018\u00010\u0003H\u00c6\u0001\u00a2\u0006\u0002\u0010-J\u0013\u0010.\u001a\u00020/2\u0008\u00100\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u00101\u001a\u000202H\u00d6\u0001J\t\u00103\u001a\u00020\u0005H\u00d6\u0001R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0012\u0010\u0013R\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0014\u0010\u0015R\u0011\u0010\u0006\u001a\u00020\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0016\u0010\u0015R\u0011\u0010\u0007\u001a\u00020\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0017\u0010\u0015R\u0011\u0010\u0008\u001a\u00020\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0018\u0010\u0015R\u0011\u0010\t\u001a\u00020\n\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0019\u0010\u001aR\u0013\u0010\u000b\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u001b\u0010\u0015R\u0011\u0010\u000c\u001a\u00020\r\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u001c\u0010\u001dR\u0011\u0010\u000e\u001a\u00020\u0003\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u001e\u0010\u0013R\u0015\u0010\u000f\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\n\n\u0002\u0010!\u001a\u0004\u0008\u001f\u0010 \u00a8\u00064"
    }
    d2 = {
        "Lme/ship/Shipment;",
        "",
        "id",
        "",
        "name",
        "",
        "origin",
        "destination",
        "description",
        "weightKg",
        "",
        "imageKey",
        "status",
        "Lme/ship/PackageStatus;",
        "createdAt",
        "shippedAt",
        "<init>",
        "(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V",
        "getId",
        "()J",
        "getName",
        "()Ljava/lang/String;",
        "getOrigin",
        "getDestination",
        "getDescription",
        "getWeightKg",
        "()D",
        "getImageKey",
        "getStatus",
        "()Lme/ship/PackageStatus;",
        "getCreatedAt",
        "getShippedAt",
        "()Ljava/lang/Long;",
        "Ljava/lang/Long;",
        "component1",
        "component2",
        "component3",
        "component4",
        "component5",
        "component6",
        "component7",
        "component8",
        "component9",
        "component10",
        "copy",
        "(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)Lme/ship/Shipment;",
        "equals",
        "",
        "other",
        "hashCode",
        "",
        "toString",
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


# instance fields
.field private final createdAt:J

.field private final description:Ljava/lang/String;

.field private final destination:Ljava/lang/String;

.field private final id:J

.field private final imageKey:Ljava/lang/String;

.field private final name:Ljava/lang/String;

.field private final origin:Ljava/lang/String;

.field private final shippedAt:Ljava/lang/Long;

.field private final status:Lme/ship/PackageStatus;

.field private final weightKg:D


# direct methods
.method public constructor <init>(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V
    .locals 1

    const-string v0, "name"

    invoke-static {p3, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "origin"

    invoke-static {p4, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "destination"

    invoke-static {p5, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "description"

    invoke-static {p6, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "status"

    invoke-static {p10, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 3
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 4
    iput-wide p1, p0, Lme/ship/Shipment;->id:J

    .line 5
    iput-object p3, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    .line 6
    iput-object p4, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    .line 7
    iput-object p5, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    .line 8
    iput-object p6, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    .line 9
    iput-wide p7, p0, Lme/ship/Shipment;->weightKg:D

    .line 10
    iput-object p9, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    .line 11
    iput-object p10, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    .line 12
    iput-wide p11, p0, Lme/ship/Shipment;->createdAt:J

    .line 13
    iput-object p13, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    return-void
.end method

.method public static synthetic copy$default(Lme/ship/Shipment;JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;ILjava/lang/Object;)Lme/ship/Shipment;
    .locals 13

    move/from16 v0, p14

    and-int/lit8 v1, v0, 0x1

    if-eqz v1, :cond_0

    iget-wide v1, p0, Lme/ship/Shipment;->id:J

    goto :goto_0

    :cond_0
    move-wide v1, p1

    :goto_0
    and-int/lit8 v3, v0, 0x2

    if-eqz v3, :cond_1

    iget-object v3, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    goto :goto_1

    :cond_1
    move-object/from16 v3, p3

    :goto_1
    and-int/lit8 v4, v0, 0x4

    if-eqz v4, :cond_2

    iget-object v4, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    goto :goto_2

    :cond_2
    move-object/from16 v4, p4

    :goto_2
    and-int/lit8 v5, v0, 0x8

    if-eqz v5, :cond_3

    iget-object v5, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    goto :goto_3

    :cond_3
    move-object/from16 v5, p5

    :goto_3
    and-int/lit8 v6, v0, 0x10

    if-eqz v6, :cond_4

    iget-object v6, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    goto :goto_4

    :cond_4
    move-object/from16 v6, p6

    :goto_4
    and-int/lit8 v7, v0, 0x20

    if-eqz v7, :cond_5

    iget-wide v7, p0, Lme/ship/Shipment;->weightKg:D

    goto :goto_5

    :cond_5
    move-wide/from16 v7, p7

    :goto_5
    and-int/lit8 v9, v0, 0x40

    if-eqz v9, :cond_6

    iget-object v9, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    goto :goto_6

    :cond_6
    move-object/from16 v9, p9

    :goto_6
    and-int/lit16 v10, v0, 0x80

    if-eqz v10, :cond_7

    iget-object v10, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    goto :goto_7

    :cond_7
    move-object/from16 v10, p10

    :goto_7
    and-int/lit16 v11, v0, 0x100

    if-eqz v11, :cond_8

    iget-wide v11, p0, Lme/ship/Shipment;->createdAt:J

    goto :goto_8

    :cond_8
    move-wide/from16 v11, p11

    :goto_8
    and-int/lit16 v0, v0, 0x200

    if-eqz v0, :cond_9

    iget-object v0, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    move-object/from16 p14, v0

    goto :goto_9

    :cond_9
    move-object/from16 p14, p13

    :goto_9
    move-object p1, p0

    move-wide p2, v1

    move-object/from16 p4, v3

    move-object/from16 p5, v4

    move-object/from16 p6, v5

    move-object/from16 p7, v6

    move-wide/from16 p8, v7

    move-object/from16 p10, v9

    move-object/from16 p11, v10

    move-wide/from16 p12, v11

    invoke-virtual/range {p1 .. p14}, Lme/ship/Shipment;->copy(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)Lme/ship/Shipment;

    move-result-object p0

    return-object p0
.end method


# virtual methods
.method public final component1()J
    .locals 2

    iget-wide v0, p0, Lme/ship/Shipment;->id:J

    return-wide v0
.end method

.method public final component10()Ljava/lang/Long;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    return-object p0
.end method

.method public final component2()Ljava/lang/String;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    return-object p0
.end method

.method public final component3()Ljava/lang/String;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    return-object p0
.end method

.method public final component4()Ljava/lang/String;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    return-object p0
.end method

.method public final component5()Ljava/lang/String;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    return-object p0
.end method

.method public final component6()D
    .locals 2

    iget-wide v0, p0, Lme/ship/Shipment;->weightKg:D

    return-wide v0
.end method

.method public final component7()Ljava/lang/String;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    return-object p0
.end method

.method public final component8()Lme/ship/PackageStatus;
    .locals 0

    iget-object p0, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    return-object p0
.end method

.method public final component9()J
    .locals 2

    iget-wide v0, p0, Lme/ship/Shipment;->createdAt:J

    return-wide v0
.end method

.method public final copy(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)Lme/ship/Shipment;
    .locals 14

    const-string p0, "name"

    move-object/from16 v3, p3

    invoke-static {v3, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string p0, "origin"

    move-object/from16 v4, p4

    invoke-static {v4, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string p0, "destination"

    move-object/from16 v5, p5

    invoke-static {v5, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string p0, "description"

    move-object/from16 v6, p6

    invoke-static {v6, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string p0, "status"

    move-object/from16 v10, p10

    invoke-static {v10, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    new-instance v0, Lme/ship/Shipment;

    move-wide v1, p1

    move-wide/from16 v7, p7

    move-object/from16 v9, p9

    move-wide/from16 v11, p11

    move-object/from16 v13, p13

    invoke-direct/range {v0 .. v13}, Lme/ship/Shipment;-><init>(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V

    return-object v0
.end method

.method public equals(Ljava/lang/Object;)Z
    .locals 7

    const/4 v0, 0x1

    if-ne p0, p1, :cond_0

    return v0

    :cond_0
    instance-of v1, p1, Lme/ship/Shipment;

    const/4 v2, 0x0

    if-nez v1, :cond_1

    return v2

    :cond_1
    check-cast p1, Lme/ship/Shipment;

    iget-wide v3, p0, Lme/ship/Shipment;->id:J

    iget-wide v5, p1, Lme/ship/Shipment;->id:J

    cmp-long v1, v3, v5

    if-eqz v1, :cond_2

    return v2

    :cond_2
    iget-object v1, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    iget-object v3, p1, Lme/ship/Shipment;->name:Ljava/lang/String;

    invoke-static {v1, v3}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_3

    return v2

    :cond_3
    iget-object v1, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    iget-object v3, p1, Lme/ship/Shipment;->origin:Ljava/lang/String;

    invoke-static {v1, v3}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_4

    return v2

    :cond_4
    iget-object v1, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    iget-object v3, p1, Lme/ship/Shipment;->destination:Ljava/lang/String;

    invoke-static {v1, v3}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_5

    return v2

    :cond_5
    iget-object v1, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    iget-object v3, p1, Lme/ship/Shipment;->description:Ljava/lang/String;

    invoke-static {v1, v3}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_6

    return v2

    :cond_6
    iget-wide v3, p0, Lme/ship/Shipment;->weightKg:D

    iget-wide v5, p1, Lme/ship/Shipment;->weightKg:D

    invoke-static {v3, v4, v5, v6}, Ljava/lang/Double;->compare(DD)I

    move-result v1

    if-eqz v1, :cond_7

    return v2

    :cond_7
    iget-object v1, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    iget-object v3, p1, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    invoke-static {v1, v3}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_8

    return v2

    :cond_8
    iget-object v1, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    iget-object v3, p1, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    if-eq v1, v3, :cond_9

    return v2

    :cond_9
    iget-wide v3, p0, Lme/ship/Shipment;->createdAt:J

    iget-wide v5, p1, Lme/ship/Shipment;->createdAt:J

    cmp-long v1, v3, v5

    if-eqz v1, :cond_a

    return v2

    :cond_a
    iget-object p0, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    iget-object p1, p1, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result p0

    if-nez p0, :cond_b

    return v2

    :cond_b
    return v0
.end method

.method public final getCreatedAt()J
    .locals 2

    .line 12
    iget-wide v0, p0, Lme/ship/Shipment;->createdAt:J

    return-wide v0
.end method

.method public final getDescription()Ljava/lang/String;
    .locals 0

    .line 8
    iget-object p0, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    return-object p0
.end method

.method public final getDestination()Ljava/lang/String;
    .locals 0

    .line 7
    iget-object p0, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    return-object p0
.end method

.method public final getId()J
    .locals 2

    .line 4
    iget-wide v0, p0, Lme/ship/Shipment;->id:J

    return-wide v0
.end method

.method public final getImageKey()Ljava/lang/String;
    .locals 0

    .line 10
    iget-object p0, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    return-object p0
.end method

.method public final getName()Ljava/lang/String;
    .locals 0

    .line 5
    iget-object p0, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    return-object p0
.end method

.method public final getOrigin()Ljava/lang/String;
    .locals 0

    .line 6
    iget-object p0, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    return-object p0
.end method

.method public final getShippedAt()Ljava/lang/Long;
    .locals 0

    .line 13
    iget-object p0, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    return-object p0
.end method

.method public final getStatus()Lme/ship/PackageStatus;
    .locals 0

    .line 11
    iget-object p0, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    return-object p0
.end method

.method public final getWeightKg()D
    .locals 2

    .line 9
    iget-wide v0, p0, Lme/ship/Shipment;->weightKg:D

    return-wide v0
.end method

.method public hashCode()I
    .locals 5

    iget-wide v0, p0, Lme/ship/Shipment;->id:J

    invoke-static {v0, v1}, Ljava/lang/Long;->hashCode(J)I

    move-result v0

    mul-int/lit8 v0, v0, 0x1f

    iget-object v1, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->hashCode()I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-object v1, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->hashCode()I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-object v1, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->hashCode()I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-object v1, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    invoke-virtual {v1}, Ljava/lang/String;->hashCode()I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-wide v1, p0, Lme/ship/Shipment;->weightKg:D

    invoke-static {v1, v2}, Ljava/lang/Double;->hashCode(D)I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-object v1, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    const/4 v2, 0x0

    if-nez v1, :cond_0

    move v1, v2

    goto :goto_0

    :cond_0
    invoke-virtual {v1}, Ljava/lang/String;->hashCode()I

    move-result v1

    :goto_0
    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-object v1, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    invoke-virtual {v1}, Lme/ship/PackageStatus;->hashCode()I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-wide v3, p0, Lme/ship/Shipment;->createdAt:J

    invoke-static {v3, v4}, Ljava/lang/Long;->hashCode(J)I

    move-result v1

    add-int/2addr v0, v1

    mul-int/lit8 v0, v0, 0x1f

    iget-object p0, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    if-nez p0, :cond_1

    goto :goto_1

    :cond_1
    invoke-virtual {p0}, Ljava/lang/Object;->hashCode()I

    move-result v2

    :goto_1
    add-int/2addr v0, v2

    return v0
.end method

.method public toString()Ljava/lang/String;
    .locals 14

    iget-wide v0, p0, Lme/ship/Shipment;->id:J

    iget-object v2, p0, Lme/ship/Shipment;->name:Ljava/lang/String;

    iget-object v3, p0, Lme/ship/Shipment;->origin:Ljava/lang/String;

    iget-object v4, p0, Lme/ship/Shipment;->destination:Ljava/lang/String;

    iget-object v5, p0, Lme/ship/Shipment;->description:Ljava/lang/String;

    iget-wide v6, p0, Lme/ship/Shipment;->weightKg:D

    iget-object v8, p0, Lme/ship/Shipment;->imageKey:Ljava/lang/String;

    iget-object v9, p0, Lme/ship/Shipment;->status:Lme/ship/PackageStatus;

    iget-wide v10, p0, Lme/ship/Shipment;->createdAt:J

    iget-object p0, p0, Lme/ship/Shipment;->shippedAt:Ljava/lang/Long;

    new-instance v12, Ljava/lang/StringBuilder;

    const-string v13, "Shipment(id="

    invoke-direct {v12, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v12, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", name="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", origin="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", destination="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", description="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", weightKg="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v6, v7}, Ljava/lang/StringBuilder;->append(D)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", imageKey="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", status="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", createdAt="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v10, v11}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ", shippedAt="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, ")"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
