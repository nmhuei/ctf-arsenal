.class public final Lme/ship/GetShippingLabel;
.super Ljava/lang/Throwable;
.source "GetShippingLabel.kt"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lme/ship/GetShippingLabel$Companion;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nGetShippingLabel.kt\nKotlin\n*S Kotlin\n*F\n+ 1 GetShippingLabel.kt\nme/ship/GetShippingLabel\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,170:1\n1#2:171\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000J\n\u0002\u0018\u0002\n\u0002\u0010\u0003\n\u0000\n\u0002\u0010\t\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\u0008\u0005\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0010\u0007\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0006\u0018\u0000 !2\u00020\u0001:\u0001!B\u000f\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0004\u0008\u0004\u0010\u0005J\u0008\u0010\u000c\u001a\u00020\u0007H\u0002J\u0010\u0010\r\u001a\u00020\u00072\u0006\u0010\u000e\u001a\u00020\u000fH\u0002J\u0010\u0010\u0010\u001a\u00020\u00112\u0006\u0010\u000e\u001a\u00020\u000fH\u0002J8\u0010\u0012\u001a\u00020\u00132\u0006\u0010\u0014\u001a\u00020\u00152\u0006\u0010\u0016\u001a\u00020\t2\u0006\u0010\u0017\u001a\u00020\u00182\u0006\u0010\u0019\u001a\u00020\u00182\u0006\u0010\u001a\u001a\u00020\u00182\u0006\u0010\u001b\u001a\u00020\u001cH\u0002J\u0010\u0010\u001d\u001a\u00020\t2\u0006\u0010\u001e\u001a\u00020\tH\u0002J\u0010\u0010\u001f\u001a\u00020\t2\u0006\u0010 \u001a\u00020\u0003H\u0002R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0006\u001a\u0004\u0018\u00010\u0007X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u0008\u001a\u00020\t8VX\u0096\u0004\u00a2\u0006\u0006\u001a\u0004\u0008\n\u0010\u000b\u00a8\u0006\""
    }
    d2 = {
        "Lme/ship/GetShippingLabel;",
        "",
        "packageId",
        "",
        "<init>",
        "(J)V",
        "outputUri",
        "Landroid/net/Uri;",
        "message",
        "",
        "getMessage",
        "()Ljava/lang/String;",
        "prepareShippingLabel",
        "writeToImages",
        "shipment",
        "Lme/ship/Shipment;",
        "createLabelBitmap",
        "Landroid/graphics/Bitmap;",
        "drawWrapped",
        "",
        "canvas",
        "Landroid/graphics/Canvas;",
        "text",
        "x",
        "",
        "y",
        "maxWidth",
        "paint",
        "Landroid/graphics/Paint;",
        "clean",
        "value",
        "formatDate",
        "timestamp",
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
.field public static final Companion:Lme/ship/GetShippingLabel$Companion;

.field private static final serialVersionUID:J = 0x1L


# instance fields
.field private transient outputUri:Landroid/net/Uri;

.field private final packageId:J


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lme/ship/GetShippingLabel$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lme/ship/GetShippingLabel$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lme/ship/GetShippingLabel;->Companion:Lme/ship/GetShippingLabel$Companion;

    return-void
.end method

.method public constructor <init>(J)V
    .locals 0

    .line 18
    invoke-direct {p0}, Ljava/lang/Throwable;-><init>()V

    .line 17
    iput-wide p1, p0, Lme/ship/GetShippingLabel;->packageId:J

    .line 27
    invoke-direct {p0}, Lme/ship/GetShippingLabel;->prepareShippingLabel()Landroid/net/Uri;

    move-result-object p1

    iput-object p1, p0, Lme/ship/GetShippingLabel;->outputUri:Landroid/net/Uri;

    return-void
.end method

.method private final clean(Ljava/lang/String;)Ljava/lang/String;
    .locals 1

    .line 165
    check-cast p1, Ljava/lang/CharSequence;

    new-instance p0, Lkotlin/text/Regex;

    const-string v0, "[\\r\\n\\t]"

    invoke-direct {p0, v0}, Lkotlin/text/Regex;-><init>(Ljava/lang/String;)V

    const-string v0, " "

    invoke-virtual {p0, p1, v0}, Lkotlin/text/Regex;->replace(Ljava/lang/CharSequence;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    const/16 p1, 0x1f4

    invoke-static {p0, p1}, Lkotlin/text/StringsKt;->take(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method private final createLabelBitmap(Lme/ship/Shipment;)Landroid/graphics/Bitmap;
    .locals 14

    const/16 v0, 0x694

    .line 91
    sget-object v1, Landroid/graphics/Bitmap$Config;->ARGB_8888:Landroid/graphics/Bitmap$Config;

    const/16 v2, 0x4a6

    invoke-static {v2, v0, v1}, Landroid/graphics/Bitmap;->createBitmap(IILandroid/graphics/Bitmap$Config;)Landroid/graphics/Bitmap;

    move-result-object v0

    const-string v1, "createBitmap(...)"

    invoke-static {v0, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 92
    new-instance v3, Landroid/graphics/Canvas;

    invoke-direct {v3, v0}, Landroid/graphics/Canvas;-><init>(Landroid/graphics/Bitmap;)V

    const/4 v1, -0x1

    .line 93
    invoke-virtual {v3, v1}, Landroid/graphics/Canvas;->drawColor(I)V

    const/high16 v1, 0x40000000    # 2.0f

    .line 94
    invoke-virtual {v3, v1, v1}, Landroid/graphics/Canvas;->scale(FF)V

    .line 97
    new-instance v7, Landroid/graphics/Paint;

    invoke-direct {v7}, Landroid/graphics/Paint;-><init>()V

    const v1, -0xf8ece1

    invoke-virtual {v7, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 98
    new-instance v9, Landroid/graphics/Paint;

    invoke-direct {v9}, Landroid/graphics/Paint;-><init>()V

    const/4 v10, 0x1

    .line 99
    invoke-virtual {v9, v10}, Landroid/graphics/Paint;->setAntiAlias(Z)V

    const v2, -0xdf5679

    .line 100
    invoke-virtual {v9, v2}, Landroid/graphics/Paint;->setColor(I)V

    const/high16 v2, 0x41900000    # 18.0f

    .line 101
    invoke-virtual {v9, v2}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 102
    sget-object v2, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-static {v2, v10}, Landroid/graphics/Typeface;->create(Landroid/graphics/Typeface;I)Landroid/graphics/Typeface;

    move-result-object v2

    invoke-virtual {v9, v2}, Landroid/graphics/Paint;->setTypeface(Landroid/graphics/Typeface;)Landroid/graphics/Typeface;

    .line 104
    new-instance v8, Landroid/graphics/Paint;

    invoke-direct {v8}, Landroid/graphics/Paint;-><init>()V

    .line 105
    invoke-virtual {v8, v10}, Landroid/graphics/Paint;->setAntiAlias(Z)V

    .line 106
    invoke-virtual {v8, v1}, Landroid/graphics/Paint;->setColor(I)V

    const/high16 v1, 0x41f00000    # 30.0f

    .line 107
    invoke-virtual {v8, v1}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 108
    sget-object v1, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-static {v1, v10}, Landroid/graphics/Typeface;->create(Landroid/graphics/Typeface;I)Landroid/graphics/Typeface;

    move-result-object v1

    invoke-virtual {v8, v1}, Landroid/graphics/Paint;->setTypeface(Landroid/graphics/Typeface;)Landroid/graphics/Typeface;

    .line 110
    new-instance v1, Landroid/graphics/Paint;

    invoke-direct {v1}, Landroid/graphics/Paint;-><init>()V

    .line 111
    invoke-virtual {v1, v10}, Landroid/graphics/Paint;->setAntiAlias(Z)V

    const v2, -0xaa8f80

    .line 112
    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setColor(I)V

    const/high16 v2, 0x41300000    # 11.0f

    .line 113
    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 114
    sget-object v2, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    invoke-static {v2, v10}, Landroid/graphics/Typeface;->create(Landroid/graphics/Typeface;I)Landroid/graphics/Typeface;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTypeface(Landroid/graphics/Typeface;)Landroid/graphics/Typeface;

    move-object v11, v8

    .line 116
    new-instance v8, Landroid/graphics/Paint;

    invoke-direct {v8}, Landroid/graphics/Paint;-><init>()V

    .line 117
    invoke-virtual {v8, v10}, Landroid/graphics/Paint;->setAntiAlias(Z)V

    const v2, -0xefdccd

    .line 118
    invoke-virtual {v8, v2}, Landroid/graphics/Paint;->setColor(I)V

    const/high16 v2, 0x41800000    # 16.0f

    .line 119
    invoke-virtual {v8, v2}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 121
    new-instance v12, Landroid/graphics/Paint;

    invoke-direct {v12, v8}, Landroid/graphics/Paint;-><init>(Landroid/graphics/Paint;)V

    sget-object v2, Landroid/graphics/Typeface;->MONOSPACE:Landroid/graphics/Typeface;

    invoke-virtual {v12, v2}, Landroid/graphics/Paint;->setTypeface(Landroid/graphics/Typeface;)Landroid/graphics/Typeface;

    const v5, 0x4414c000    # 595.0f

    const/high16 v6, 0x41900000    # 18.0f

    move-object v2, v3

    const/4 v3, 0x0

    const/4 v4, 0x0

    .line 123
    invoke-virtual/range {v2 .. v7}, Landroid/graphics/Canvas;->drawRect(FFFFLandroid/graphics/Paint;)V

    const/high16 v3, 0x42800000    # 64.0f

    .line 124
    const-string v4, "SHIP.ME"

    const/high16 v13, 0x42400000    # 48.0f

    invoke-virtual {v2, v4, v13, v3, v9}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 125
    const-string v3, "Shipping Label"

    const/high16 v4, 0x42e00000    # 112.0f

    invoke-virtual {v2, v3, v13, v4, v11}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 126
    invoke-virtual {p1}, Lme/ship/Shipment;->getId()J

    move-result-wide v3

    new-instance v5, Ljava/lang/StringBuilder;

    const-string v6, "PACKAGE #"

    invoke-direct {v5, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5, v3, v4}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    const/high16 v11, 0x43240000    # 164.0f

    invoke-virtual {v2, v3, v13, v11, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 127
    invoke-virtual {p1}, Lme/ship/Shipment;->getName()Ljava/lang/String;

    move-result-object v3

    invoke-direct {p0, v3}, Lme/ship/GetShippingLabel;->clean(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    const/high16 v6, 0x433e0000    # 190.0f

    const/high16 v7, 0x43870000    # 270.0f

    const/high16 v5, 0x42400000    # 48.0f

    move-object v3, v2

    move-object v2, p0

    invoke-direct/range {v2 .. v8}, Lme/ship/GetShippingLabel;->drawWrapped(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 128
    const-string p0, "STATUS"

    const/high16 v4, 0x43b40000    # 360.0f

    invoke-virtual {v3, p0, v4, v11, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    const/high16 p0, 0x433c0000    # 188.0f

    .line 129
    const-string v11, "SHIPPED"

    invoke-virtual {v3, v11, v4, p0, v9}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 130
    const-string p0, "ROUTE"

    const/high16 v4, 0x437a0000    # 250.0f

    invoke-virtual {v3, p0, v13, v4, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 131
    invoke-virtual {p1}, Lme/ship/Shipment;->getOrigin()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v2, p0}, Lme/ship/GetShippingLabel;->clean(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    const/high16 v4, 0x438b0000    # 278.0f

    invoke-virtual {v3, p0, v13, v4, v8}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 132
    const-string p0, "to"

    const/high16 v4, 0x43980000    # 304.0f

    invoke-virtual {v3, p0, v13, v4, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 133
    invoke-virtual {p1}, Lme/ship/Shipment;->getDestination()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v2, p0}, Lme/ship/GetShippingLabel;->clean(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    const/high16 v4, 0x43a60000    # 332.0f

    invoke-virtual {v3, p0, v13, v4, v8}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 134
    const-string p0, "CONTENTS"

    const/high16 v4, 0x43bf0000    # 382.0f

    invoke-virtual {v3, p0, v13, v4, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 135
    invoke-virtual {p1}, Lme/ship/Shipment;->getDescription()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v2, p0}, Lme/ship/GetShippingLabel;->clean(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    const/high16 v6, 0x43cd0000    # 410.0f

    const/high16 v7, 0x43fa0000    # 500.0f

    invoke-direct/range {v2 .. v8}, Lme/ship/GetShippingLabel;->drawWrapped(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 136
    const-string p0, "WEIGHT"

    const/high16 v4, 0x43ef0000    # 478.0f

    invoke-virtual {v3, p0, v13, v4, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 137
    sget-object p0, Lkotlin/jvm/internal/StringCompanionObject;->INSTANCE:Lkotlin/jvm/internal/StringCompanionObject;

    sget-object p0, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-virtual {p1}, Lme/ship/Shipment;->getWeightKg()D

    move-result-wide v4

    invoke-static {v4, v5}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v4

    filled-new-array {v4}, [Ljava/lang/Object;

    move-result-object v4

    invoke-static {v4, v10}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object v4

    const-string v5, "%.1f kg"

    invoke-static {p0, v5, v4}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    const-string v4, "format(...)"

    invoke-static {p0, v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const/high16 v4, 0x43fc0000    # 504.0f

    invoke-virtual {v3, p0, v13, v4, v12}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 138
    const-string p0, "CREATED"

    const v4, 0x440a8000    # 554.0f

    invoke-virtual {v3, p0, v13, v4, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 139
    invoke-virtual {p1}, Lme/ship/Shipment;->getCreatedAt()J

    move-result-wide v5

    invoke-direct {v2, v5, v6}, Lme/ship/GetShippingLabel;->formatDate(J)Ljava/lang/String;

    move-result-object p0

    const/high16 v5, 0x44110000    # 580.0f

    invoke-virtual {v3, p0, v13, v5, v8}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    const/high16 p0, 0x43960000    # 300.0f

    .line 140
    invoke-virtual {v3, v11, p0, v4, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 141
    invoke-virtual {p1}, Lme/ship/Shipment;->getShippedAt()Ljava/lang/Long;

    move-result-object p1

    if-eqz p1, :cond_0

    check-cast p1, Ljava/lang/Number;

    invoke-virtual {p1}, Ljava/lang/Number;->longValue()J

    move-result-wide v6

    invoke-direct {v2, v6, v7}, Lme/ship/GetShippingLabel;->formatDate(J)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v3, p1, p0, v5, v8}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 142
    const-string p0, "Generated by ship.me"

    const p1, 0x44458000    # 790.0f

    invoke-virtual {v3, p0, v13, p1, v1}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    return-object v0

    .line 141
    :cond_0
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Required value was null."

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method private final drawWrapped(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V
    .locals 1

    .line 156
    :goto_0
    move-object p0, p2

    check-cast p0, Ljava/lang/CharSequence;

    invoke-interface {p0}, Ljava/lang/CharSequence;->length()I

    move-result p0

    if-lez p0, :cond_0

    const/4 p0, 0x0

    const/4 v0, 0x1

    .line 157
    invoke-virtual {p6, p2, v0, p5, p0}, Landroid/graphics/Paint;->breakText(Ljava/lang/String;ZF[F)I

    move-result p0

    invoke-static {p0, v0}, Lkotlin/ranges/RangesKt;->coerceAtLeast(II)I

    move-result p0

    .line 158
    invoke-static {p2, p0}, Lkotlin/text/StringsKt;->take(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p1, v0, p3, p4, p6}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 159
    invoke-static {p2, p0}, Lkotlin/text/StringsKt;->drop(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object p2

    .line 160
    invoke-virtual {p6}, Landroid/graphics/Paint;->getTextSize()F

    move-result p0

    const v0, 0x3faccccd    # 1.35f

    mul-float/2addr p0, v0

    add-float/2addr p4, p0

    goto :goto_0

    :cond_0
    return-void
.end method

.method private final formatDate(J)Ljava/lang/String;
    .locals 2

    .line 168
    new-instance p0, Ljava/text/SimpleDateFormat;

    const-string v0, "yyyy-MM-dd HH:mm"

    sget-object v1, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-direct {p0, v0, v1}, Ljava/text/SimpleDateFormat;-><init>(Ljava/lang/String;Ljava/util/Locale;)V

    new-instance v0, Ljava/util/Date;

    invoke-direct {v0, p1, p2}, Ljava/util/Date;-><init>(J)V

    invoke-virtual {p0, v0}, Ljava/text/SimpleDateFormat;->format(Ljava/util/Date;)Ljava/lang/String;

    move-result-object p0

    const-string p1, "format(...)"

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0
.end method

.method private final prepareShippingLabel()Landroid/net/Uri;
    .locals 4

    .line 40
    sget-object v0, Lme/ship/ShipMeDatabase;->Companion:Lme/ship/ShipMeDatabase$Companion;

    .line 41
    sget-object v1, Lme/ship/ShipMeApplication;->Companion:Lme/ship/ShipMeApplication$Companion;

    invoke-virtual {v1}, Lme/ship/ShipMeApplication$Companion;->getInstance()Lme/ship/ShipMeApplication;

    move-result-object v1

    check-cast v1, Landroid/content/Context;

    invoke-virtual {v0, v1}, Lme/ship/ShipMeDatabase$Companion;->getInstance(Landroid/content/Context;)Lme/ship/ShipMeDatabase;

    move-result-object v0

    .line 42
    iget-wide v1, p0, Lme/ship/GetShippingLabel;->packageId:J

    invoke-virtual {v0, v1, v2}, Lme/ship/ShipMeDatabase;->getPackage(J)Lme/ship/Shipment;

    move-result-object v0

    .line 39
    const-string v1, "Package #"

    if-eqz v0, :cond_1

    .line 45
    invoke-virtual {v0}, Lme/ship/Shipment;->getStatus()Lme/ship/PackageStatus;

    move-result-object v2

    sget-object v3, Lme/ship/PackageStatus;->SHIPPED:Lme/ship/PackageStatus;

    if-ne v2, v3, :cond_0

    .line 48
    invoke-direct {p0, v0}, Lme/ship/GetShippingLabel;->writeToImages(Lme/ship/Shipment;)Landroid/net/Uri;

    move-result-object p0

    return-object p0

    .line 46
    :cond_0
    iget-wide v2, p0, Lme/ship/GetShippingLabel;->packageId:J

    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v2, v3}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " must be shipped before creating a label"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 45
    new-instance v0, Ljava/lang/IllegalStateException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v0, p0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 43
    :cond_1
    iget-wide v2, p0, Lme/ship/GetShippingLabel;->packageId:J

    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v2, v3}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " does not exist"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 39
    new-instance v0, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {v0, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v0
.end method

.method private final writeToImages(Lme/ship/Shipment;)Landroid/net/Uri;
    .locals 9

    .line 52
    sget-object v0, Lme/ship/ShipMeApplication;->Companion:Lme/ship/ShipMeApplication$Companion;

    invoke-virtual {v0}, Lme/ship/ShipMeApplication$Companion;->getInstance()Lme/ship/ShipMeApplication;

    move-result-object v0

    invoke-virtual {v0}, Lme/ship/ShipMeApplication;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0

    .line 53
    invoke-virtual {p1}, Lme/ship/Shipment;->getId()J

    move-result-wide v1

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v4, "ship-me-label-"

    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v1, v2}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ".png"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 54
    new-instance v2, Landroid/content/ContentValues;

    invoke-direct {v2}, Landroid/content/ContentValues;-><init>()V

    .line 55
    const-string v3, "_display_name"

    invoke-virtual {v2, v3, v1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 56
    const-string v3, "mime_type"

    const-string v4, "image/png"

    invoke-virtual {v2, v3, v4}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 59
    sget-object v3, Landroid/os/Environment;->DIRECTORY_PICTURES:Ljava/lang/String;

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, "/ship.me"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 57
    const-string v4, "relative_path"

    invoke-virtual {v2, v4, v3}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    const/4 v3, 0x1

    .line 61
    invoke-static {v3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v4

    const-string v5, "is_pending"

    invoke-virtual {v2, v5, v4}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Integer;)V

    .line 63
    sget-object v4, Landroid/provider/MediaStore$Images$Media;->EXTERNAL_CONTENT_URI:Landroid/net/Uri;

    invoke-virtual {v0, v4, v2}, Landroid/content/ContentResolver;->insert(Landroid/net/Uri;Landroid/content/ContentValues;)Landroid/net/Uri;

    move-result-object v4

    if-eqz v4, :cond_3

    const/4 v1, 0x0

    .line 67
    :try_start_0
    invoke-direct {p0, p1}, Lme/ship/GetShippingLabel;->createLabelBitmap(Lme/ship/Shipment;)Landroid/graphics/Bitmap;

    move-result-object p0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_3

    .line 69
    :try_start_1
    const-string p1, "w"

    invoke-virtual {v0, v4, p1}, Landroid/content/ContentResolver;->openOutputStream(Landroid/net/Uri;Ljava/lang/String;)Ljava/io/OutputStream;

    move-result-object p1

    if-eqz p1, :cond_2

    check-cast p1, Ljava/io/Closeable;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_2

    :try_start_2
    move-object v6, p1

    check-cast v6, Ljava/io/OutputStream;

    .line 70
    sget-object v7, Landroid/graphics/Bitmap$CompressFormat;->PNG:Landroid/graphics/Bitmap$CompressFormat;

    const/16 v8, 0x64

    invoke-virtual {p0, v7, v8, v6}, Landroid/graphics/Bitmap;->compress(Landroid/graphics/Bitmap$CompressFormat;ILjava/io/OutputStream;)Z

    move-result v6

    if-eqz v6, :cond_1

    .line 73
    sget-object v6, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 69
    :try_start_3
    invoke-static {p1, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_2

    .line 75
    :try_start_4
    invoke-virtual {p0}, Landroid/graphics/Bitmap;->recycle()V

    .line 78
    invoke-virtual {v2}, Landroid/content/ContentValues;->clear()V

    const/4 p0, 0x0

    .line 79
    invoke-static {p0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object p0

    invoke-virtual {v2, v5, p0}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Integer;)V

    .line 80
    invoke-virtual {v0, v4, v2, v1, v1}, Landroid/content/ContentResolver;->update(Landroid/net/Uri;Landroid/content/ContentValues;Ljava/lang/String;[Ljava/lang/String;)I

    move-result p0

    if-ne p0, v3, :cond_0

    return-object v4

    .line 81
    :cond_0
    const-string p0, "Could not publish the shipping label"

    .line 80
    new-instance p1, Ljava/lang/IllegalStateException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {p1, p0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p1
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_3

    .line 71
    :cond_1
    :try_start_5
    const-string v2, "Could not encode the shipping label as PNG"

    .line 70
    new-instance v3, Ljava/lang/IllegalStateException;

    invoke-virtual {v2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v3, v2}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v3
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_0

    :catchall_0
    move-exception v2

    .line 69
    :try_start_6
    throw v2
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_1

    :catchall_1
    move-exception v3

    :try_start_7
    invoke-static {p1, v2}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v3

    :cond_2
    new-instance p1, Ljava/lang/IllegalStateException;

    .line 73
    const-string v2, "Could not open the shipping-label output stream"

    invoke-virtual {v2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {p1, v2}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p1
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_2

    :catchall_2
    move-exception p1

    .line 75
    :try_start_8
    invoke-virtual {p0}, Landroid/graphics/Bitmap;->recycle()V

    throw p1
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_3

    :catchall_3
    move-exception p0

    .line 85
    invoke-virtual {v0, v4, v1, v1}, Landroid/content/ContentResolver;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I

    .line 86
    throw p0

    .line 63
    :cond_3
    new-instance p0, Ljava/lang/IllegalStateException;

    .line 64
    new-instance p1, Ljava/lang/StringBuilder;

    const-string v0, "Could not create "

    invoke-direct {p1, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string v0, " in MediaStore.Images"

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method


# virtual methods
.method public getMessage()Ljava/lang/String;
    .locals 2

    .line 32
    iget-object v0, p0, Lme/ship/GetShippingLabel;->outputUri:Landroid/net/Uri;

    if-nez v0, :cond_0

    .line 33
    invoke-direct {p0}, Lme/ship/GetShippingLabel;->prepareShippingLabel()Landroid/net/Uri;

    move-result-object v0

    iput-object v0, p0, Lme/ship/GetShippingLabel;->outputUri:Landroid/net/Uri;

    .line 35
    :cond_0
    new-instance p0, Ljava/lang/StringBuilder;

    const-string v1, "Shipping label available at "

    invoke-direct {p0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
