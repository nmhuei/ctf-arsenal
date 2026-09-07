.class public final Lme/ship/ShipMeDatabase;
.super Landroid/database/sqlite/SQLiteOpenHelper;
.source "ShipMeDatabase.kt"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lme/ship/ShipMeDatabase$Companion;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nShipMeDatabase.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ShipMeDatabase.kt\nme/ship/ShipMeDatabase\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,235:1\n1#2:236\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000h\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u0008\n\u0002\u0008\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0010\u000e\n\u0002\u0008\u0004\n\u0002\u0010\u0006\n\u0002\u0008\u0002\n\u0002\u0010\u000b\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0006\u0018\u0000 -2\u00020\u0001:\u0001-B\u0011\u0008\u0002\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0004\u0008\u0004\u0010\u0005J\u0010\u0010\u0008\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000bH\u0016J\u0010\u0010\u000c\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000bH\u0016J \u0010\r\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000b2\u0006\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\u000fH\u0016J8\u0010\u0011\u001a\u00020\u00122\u0006\u0010\u0013\u001a\u00020\u00142\u0006\u0010\u0015\u001a\u00020\u00142\u0006\u0010\u0016\u001a\u00020\u00142\u0006\u0010\u0017\u001a\u00020\u00142\u0006\u0010\u0018\u001a\u00020\u00192\u0008\u0010\u001a\u001a\u0004\u0018\u00010\u0014J\u0015\u0010\u001b\u001a\u00020\u001c2\u0006\u0010\u001d\u001a\u00020\u0012H\u0000\u00a2\u0006\u0002\u0008\u001eJ\u0010\u0010\u001f\u001a\u0004\u0018\u00010 2\u0006\u0010\u001d\u001a\u00020\u0012J\u000c\u0010!\u001a\u0008\u0012\u0004\u0012\u00020 0\"J\u000c\u0010#\u001a\u00020 *\u00020$H\u0002J\u0010\u0010%\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000bH\u0002Ja\u0010&\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000b2\u0006\u0010\u0013\u001a\u00020\u00142\u0006\u0010\u0015\u001a\u00020\u00142\u0006\u0010\u0016\u001a\u00020\u00142\u0006\u0010\u0017\u001a\u00020\u00142\u0006\u0010\u0018\u001a\u00020\u00192\u0008\u0010\u001a\u001a\u0004\u0018\u00010\u00142\u0006\u0010\'\u001a\u00020(2\u0006\u0010)\u001a\u00020\u00122\u0008\u0010*\u001a\u0004\u0018\u00010\u0012H\u0002\u00a2\u0006\u0002\u0010+J\u0010\u0010,\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u000bH\u0002R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006."
    }
    d2 = {
        "Lme/ship/ShipMeDatabase;",
        "Landroid/database/sqlite/SQLiteOpenHelper;",
        "context",
        "Landroid/content/Context;",
        "<init>",
        "(Landroid/content/Context;)V",
        "crypto",
        "Lme/ship/PackageCrypto;",
        "onConfigure",
        "",
        "db",
        "Landroid/database/sqlite/SQLiteDatabase;",
        "onCreate",
        "onUpgrade",
        "oldVersion",
        "",
        "newVersion",
        "createPackage",
        "",
        "name",
        "",
        "origin",
        "destination",
        "description",
        "weightKg",
        "",
        "imageKey",
        "moveToShipped",
        "",
        "packageId",
        "moveToShipped$app",
        "getPackage",
        "Lme/ship/Shipment;",
        "getAllPackages",
        "",
        "toShipment",
        "Landroid/database/Cursor;",
        "seedDemoPackages",
        "insertSeed",
        "status",
        "Lme/ship/PackageStatus;",
        "createdAt",
        "shippedAt",
        "(Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V",
        "encryptExistingMetadata",
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
.field private static final ALL_COLUMNS:[Ljava/lang/String;

.field private static final COLUMN_CREATED_AT:Ljava/lang/String; = "created_at"

.field private static final COLUMN_DESCRIPTION:Ljava/lang/String; = "description"

.field private static final COLUMN_DESTINATION:Ljava/lang/String; = "destination"

.field private static final COLUMN_ID:Ljava/lang/String; = "id"

.field private static final COLUMN_IMAGE_KEY:Ljava/lang/String; = "image_key"

.field private static final COLUMN_NAME:Ljava/lang/String; = "name"

.field private static final COLUMN_ORIGIN:Ljava/lang/String; = "origin"

.field private static final COLUMN_SHIPPED_AT:Ljava/lang/String; = "shipped_at"

.field private static final COLUMN_STATUS:Ljava/lang/String; = "status"

.field private static final COLUMN_WEIGHT_KG:Ljava/lang/String; = "weight_kg"

.field public static final Companion:Lme/ship/ShipMeDatabase$Companion;

.field private static final DATABASE_NAME:Ljava/lang/String; = "ship_me.db"

.field private static final DATABASE_VERSION:I = 0x3

.field private static final TABLE_PACKAGES:Ljava/lang/String; = "packages"

.field private static volatile instance:Lme/ship/ShipMeDatabase;


# instance fields
.field private final crypto:Lme/ship/PackageCrypto;


# direct methods
.method static constructor <clinit>()V
    .locals 3

    new-instance v0, Lme/ship/ShipMeDatabase$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lme/ship/ShipMeDatabase$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lme/ship/ShipMeDatabase;->Companion:Lme/ship/ShipMeDatabase$Companion;

    const/16 v0, 0xa

    .line 221
    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "id"

    aput-object v2, v0, v1

    const/4 v1, 0x1

    const-string v2, "name"

    aput-object v2, v0, v1

    const/4 v1, 0x2

    const-string v2, "origin"

    aput-object v2, v0, v1

    const/4 v1, 0x3

    const-string v2, "destination"

    aput-object v2, v0, v1

    const/4 v1, 0x4

    .line 222
    const-string v2, "description"

    aput-object v2, v0, v1

    const/4 v1, 0x5

    const-string v2, "weight_kg"

    aput-object v2, v0, v1

    const/4 v1, 0x6

    const-string v2, "image_key"

    aput-object v2, v0, v1

    const/4 v1, 0x7

    const-string v2, "status"

    aput-object v2, v0, v1

    const/16 v1, 0x8

    .line 223
    const-string v2, "created_at"

    aput-object v2, v0, v1

    const/16 v1, 0x9

    const-string v2, "shipped_at"

    aput-object v2, v0, v1

    .line 220
    sput-object v0, Lme/ship/ShipMeDatabase;->ALL_COLUMNS:[Ljava/lang/String;

    return-void
.end method

.method private constructor <init>(Landroid/content/Context;)V
    .locals 3

    .line 10
    invoke-virtual {p1}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object p1

    const/4 v0, 0x0

    const/4 v1, 0x3

    const-string v2, "ship_me.db"

    invoke-direct {p0, p1, v2, v0, v1}, Landroid/database/sqlite/SQLiteOpenHelper;-><init>(Landroid/content/Context;Ljava/lang/String;Landroid/database/sqlite/SQLiteDatabase$CursorFactory;I)V

    .line 11
    new-instance p1, Lme/ship/PackageCrypto;

    invoke-direct {p1}, Lme/ship/PackageCrypto;-><init>()V

    iput-object p1, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    return-void
.end method

.method public synthetic constructor <init>(Landroid/content/Context;Lkotlin/jvm/internal/DefaultConstructorMarker;)V
    .locals 0

    invoke-direct {p0, p1}, Lme/ship/ShipMeDatabase;-><init>(Landroid/content/Context;)V

    return-void
.end method

.method public static final synthetic access$getInstance$cp()Lme/ship/ShipMeDatabase;
    .locals 1

    .line 9
    sget-object v0, Lme/ship/ShipMeDatabase;->instance:Lme/ship/ShipMeDatabase;

    return-object v0
.end method

.method public static final synthetic access$setInstance$cp(Lme/ship/ShipMeDatabase;)V
    .locals 0

    .line 9
    sput-object p0, Lme/ship/ShipMeDatabase;->instance:Lme/ship/ShipMeDatabase;

    return-void
.end method

.method private final encryptExistingMetadata(Landroid/database/sqlite/SQLiteDatabase;)V
    .locals 20

    move-object/from16 v0, p0

    .line 176
    const-string v1, "getString(...)"

    const/4 v2, 0x6

    .line 178
    new-array v5, v2, [Ljava/lang/String;

    const/4 v2, 0x0

    const-string v11, "id"

    aput-object v11, v5, v2

    const/4 v12, 0x1

    const-string v13, "name"

    aput-object v13, v5, v12

    const/4 v3, 0x2

    const-string v14, "origin"

    aput-object v14, v5, v3

    const/4 v3, 0x3

    const-string v15, "destination"

    aput-object v15, v5, v3

    const/4 v3, 0x4

    const-string v4, "description"

    aput-object v4, v5, v3

    const/4 v3, 0x5

    const-string v6, "image_key"

    aput-object v6, v5, v3

    const/4 v9, 0x0

    const/4 v10, 0x0

    move-object v3, v4

    .line 176
    const-string v4, "packages"

    move-object v7, v6

    const/4 v6, 0x0

    move-object v8, v7

    const/4 v7, 0x0

    move-object/from16 v16, v8

    const/4 v8, 0x0

    move/from16 v17, v2

    move-object v2, v3

    move-object/from16 v12, v16

    move-object/from16 v3, p1

    invoke-virtual/range {v3 .. v10}, Landroid/database/sqlite/SQLiteDatabase;->query(Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;

    move-result-object v4

    check-cast v4, Ljava/io/Closeable;

    .line 184
    :try_start_0
    move-object v3, v4

    check-cast v3, Landroid/database/Cursor;

    .line 185
    :goto_0
    invoke-interface {v3}, Landroid/database/Cursor;->moveToNext()Z

    move-result v5

    if-eqz v5, :cond_1

    .line 186
    invoke-interface {v3, v11}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v5

    invoke-interface {v3, v5}, Landroid/database/Cursor;->getLong(I)J

    move-result-wide v5

    .line 187
    invoke-interface {v3, v12}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v7

    .line 189
    const-string v8, "packages"

    .line 190
    new-instance v9, Landroid/content/ContentValues;

    invoke-direct {v9}, Landroid/content/ContentValues;-><init>()V

    .line 191
    iget-object v10, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    move-wide/from16 v18, v5

    invoke-interface {v3, v13}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v5

    invoke-interface {v3, v5}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v5

    invoke-static {v5, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v10, v5}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v9, v13, v5}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 192
    iget-object v5, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-interface {v3, v14}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v6

    invoke-interface {v3, v6}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v6

    invoke-static {v6, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v5, v6}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v9, v14, v5}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 193
    iget-object v5, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-interface {v3, v15}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v6

    invoke-interface {v3, v6}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v6

    invoke-static {v6, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v5, v6}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v9, v15, v5}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 194
    iget-object v5, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-interface {v3, v2}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v6

    invoke-interface {v3, v6}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v6

    invoke-static {v6, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v5, v6}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v9, v2, v5}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 195
    invoke-interface {v3, v7}, Landroid/database/Cursor;->isNull(I)Z

    move-result v5

    if-eqz v5, :cond_0

    invoke-virtual {v9, v12}, Landroid/content/ContentValues;->putNull(Ljava/lang/String;)V

    goto :goto_1

    .line 196
    :cond_0
    iget-object v5, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-interface {v3, v7}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v6

    invoke-static {v6, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v5, v6}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v9, v12, v5}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 197
    :goto_1
    sget-object v5, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 198
    const-string v5, "id = ?"

    const/4 v6, 0x1

    .line 199
    new-array v7, v6, [Ljava/lang/String;

    invoke-static/range {v18 .. v19}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;

    move-result-object v10

    aput-object v10, v7, v17

    move-object/from16 v10, p1

    .line 188
    invoke-virtual {v10, v8, v9, v5, v7}, Landroid/database/sqlite/SQLiteDatabase;->update(Ljava/lang/String;Landroid/content/ContentValues;Ljava/lang/String;[Ljava/lang/String;)I

    goto/16 :goto_0

    .line 202
    :cond_1
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const/4 v0, 0x0

    .line 184
    invoke-static {v4, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    return-void

    :catchall_0
    move-exception v0

    move-object v1, v0

    :try_start_1
    throw v1
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception v0

    invoke-static {v4, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
.end method

.method private final insertSeed(Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V
    .locals 2

    .line 162
    new-instance v0, Landroid/content/ContentValues;

    invoke-direct {v0}, Landroid/content/ContentValues;-><init>()V

    .line 163
    iget-object v1, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-virtual {v1, p2}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    const-string v1, "name"

    invoke-virtual {v0, v1, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 164
    iget-object p2, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-virtual {p2, p3}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    const-string p3, "origin"

    invoke-virtual {v0, p3, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 165
    iget-object p2, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-virtual {p2, p4}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    const-string p3, "destination"

    invoke-virtual {v0, p3, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 166
    iget-object p2, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-virtual {p2, p5}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    const-string p3, "description"

    invoke-virtual {v0, p3, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 167
    const-string p2, "weight_kg"

    invoke-static {p6, p7}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p3

    invoke-virtual {v0, p2, p3}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Double;)V

    .line 168
    const-string p2, "image_key"

    if-nez p8, :cond_0

    invoke-virtual {v0, p2}, Landroid/content/ContentValues;->putNull(Ljava/lang/String;)V

    goto :goto_0

    :cond_0
    iget-object p0, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-virtual {p0, p8}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p2, p0}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 169
    :goto_0
    const-string p0, "status"

    invoke-virtual {p9}, Lme/ship/PackageStatus;->getDatabaseValue()Ljava/lang/String;

    move-result-object p2

    invoke-virtual {v0, p0, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 170
    const-string p0, "created_at"

    invoke-static {p10, p11}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object p2

    invoke-virtual {v0, p0, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Long;)V

    .line 171
    const-string p0, "shipped_at"

    if-nez p12, :cond_1

    invoke-virtual {v0, p0}, Landroid/content/ContentValues;->putNull(Ljava/lang/String;)V

    goto :goto_1

    :cond_1
    invoke-virtual {v0, p0, p12}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Long;)V

    .line 172
    :goto_1
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 162
    const-string p0, "packages"

    const/4 p2, 0x0

    invoke-virtual {p1, p0, p2, v0}, Landroid/database/sqlite/SQLiteDatabase;->insertOrThrow(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;)J

    return-void
.end method

.method private final seedDemoPackages(Landroid/database/sqlite/SQLiteDatabase;)V
    .locals 28

    .line 132
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 136
    sget-object v11, Lme/ship/PackageStatus;->READY_TO_SHIP:Lme/ship/PackageStatus;

    const v2, 0x6ddd00

    int-to-long v2, v2

    sub-long v12, v0, v2

    const/4 v14, 0x0

    .line 133
    const-string v4, "Arctic medical supplies"

    const-string v5, "Reykjav\u00edk"

    const-string v6, "Longyearbyen"

    const-string v7, "Temperature-controlled vaccine case \u00b7 Priority handling"

    const-wide v8, 0x4032666666666666L    # 18.4

    const-string v10, "medical"

    move-object/from16 v2, p0

    move-object/from16 v3, p1

    invoke-direct/range {v2 .. v14}, Lme/ship/ShipMeDatabase;->insertSeed(Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V

    .line 141
    sget-object v24, Lme/ship/PackageStatus;->SHIPPED:Lme/ship/PackageStatus;

    const v2, 0x5265c00

    int-to-long v2, v2

    sub-long v25, v0, v2

    const v2, 0x4ef6d80

    int-to-long v2, v2

    sub-long v2, v0, v2

    invoke-static {v2, v3}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v27

    .line 138
    const-string v17, "Vintage camera collection"

    const-string v18, "Tokyo"

    const-string v19, "Berlin"

    const-string v20, "Three insured 35 mm cameras \u00b7 Fragile"

    const-wide v21, 0x401b333333333333L    # 6.8

    const-string v23, "camera"

    move-object/from16 v15, p0

    move-object/from16 v16, p1

    invoke-direct/range {v15 .. v27}, Lme/ship/ShipMeDatabase;->insertSeed(Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V

    .line 146
    sget-object v24, Lme/ship/PackageStatus;->READY_TO_SHIP:Lme/ship/PackageStatus;

    const v2, 0xa4cb800

    int-to-long v2, v2

    sub-long v25, v0, v2

    const/16 v27, 0x0

    .line 143
    const-string v17, "Racing yacht components"

    const-string v18, "Monaco"

    const-string v19, "Valencia"

    const-string v20, "Carbon-fiber fittings and navigation instruments"

    const-wide v21, 0x40454ccccccccccdL    # 42.6

    const-string v23, "parts"

    invoke-direct/range {v15 .. v27}, Lme/ship/ShipMeDatabase;->insertSeed(Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V

    return-void
.end method

.method private final toShipment(Landroid/database/Cursor;)Lme/ship/Shipment;
    .locals 18

    move-object/from16 v0, p0

    move-object/from16 v1, p1

    .line 115
    const-string v2, "id"

    invoke-interface {v1, v2}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v2

    invoke-interface {v1, v2}, Landroid/database/Cursor;->getLong(I)J

    move-result-wide v4

    .line 116
    iget-object v2, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    const-string v3, "name"

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v3

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v3

    const-string v6, "getString(...)"

    invoke-static {v3, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v2, v3}, Lme/ship/PackageCrypto;->decrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 117
    iget-object v3, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    const-string v7, "origin"

    invoke-interface {v1, v7}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v7

    invoke-interface {v1, v7}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v7

    invoke-static {v7, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v3, v7}, Lme/ship/PackageCrypto;->decrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v7

    .line 118
    iget-object v3, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    const-string v8, "destination"

    invoke-interface {v1, v8}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v8

    invoke-interface {v1, v8}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v8

    invoke-static {v8, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v3, v8}, Lme/ship/PackageCrypto;->decrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v8

    .line 119
    iget-object v3, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    const-string v9, "description"

    invoke-interface {v1, v9}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v9

    invoke-interface {v1, v9}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v9

    invoke-static {v9, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v3, v9}, Lme/ship/PackageCrypto;->decrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v9

    .line 120
    const-string v3, "weight_kg"

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v3

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getDouble(I)D

    move-result-wide v10

    .line 121
    const-string v3, "image_key"

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v3

    .line 122
    invoke-interface {v1, v3}, Landroid/database/Cursor;->isNull(I)Z

    move-result v12

    const/4 v13, 0x0

    if-eqz v12, :cond_0

    move-object v12, v13

    goto :goto_0

    :cond_0
    iget-object v0, v0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v3

    invoke-static {v3, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0, v3}, Lme/ship/PackageCrypto;->decrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    move-object v12, v0

    .line 124
    :goto_0
    sget-object v0, Lme/ship/PackageStatus;->Companion:Lme/ship/PackageStatus$Companion;

    const-string v3, "status"

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v3

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getString(I)Ljava/lang/String;

    move-result-object v3

    invoke-static {v3, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0, v3}, Lme/ship/PackageStatus$Companion;->fromDatabase(Ljava/lang/String;)Lme/ship/PackageStatus;

    move-result-object v0

    .line 125
    const-string v3, "created_at"

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v3

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getLong(I)J

    move-result-wide v14

    .line 126
    const-string v3, "shipped_at"

    invoke-interface {v1, v3}, Landroid/database/Cursor;->getColumnIndexOrThrow(Ljava/lang/String;)I

    move-result v3

    .line 127
    invoke-interface {v1, v3}, Landroid/database/Cursor;->isNull(I)Z

    move-result v6

    if-eqz v6, :cond_1

    goto :goto_1

    :cond_1
    invoke-interface {v1, v3}, Landroid/database/Cursor;->getLong(I)J

    move-result-wide v16

    invoke-static/range {v16 .. v17}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v13

    :goto_1
    move-object/from16 v16, v13

    .line 114
    new-instance v3, Lme/ship/Shipment;

    move-object v13, v0

    move-object v6, v2

    invoke-direct/range {v3 .. v16}, Lme/ship/Shipment;-><init>(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;Lme/ship/PackageStatus;JLjava/lang/Long;)V

    return-object v3
.end method


# virtual methods
.method public final createPackage(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;DLjava/lang/String;)J
    .locals 7

    const-string v0, "name"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v1, "origin"

    invoke-static {p2, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v2, "destination"

    invoke-static {p3, v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v3, "description"

    invoke-static {p4, v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 58
    check-cast p1, Ljava/lang/CharSequence;

    invoke-static {p1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v4

    if-nez v4, :cond_4

    .line 59
    check-cast p2, Ljava/lang/CharSequence;

    invoke-static {p2}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v4

    if-nez v4, :cond_3

    .line 60
    check-cast p3, Ljava/lang/CharSequence;

    invoke-static {p3}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v4

    if-nez v4, :cond_2

    const-wide/16 v4, 0x0

    cmpl-double v4, p5, v4

    if-ltz v4, :cond_1

    .line 63
    invoke-virtual {p0}, Lme/ship/ShipMeDatabase;->getWritableDatabase()Landroid/database/sqlite/SQLiteDatabase;

    move-result-object v4

    new-instance v5, Landroid/content/ContentValues;

    invoke-direct {v5}, Landroid/content/ContentValues;-><init>()V

    .line 64
    iget-object v6, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-static {p1}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v6, p1}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v5, v0, p1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 65
    iget-object p1, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-static {p2}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v5, v1, p1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 66
    iget-object p1, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-static {p3}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v5, v2, p1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 67
    iget-object p1, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    check-cast p4, Ljava/lang/CharSequence;

    invoke-static {p4}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v5, v3, p1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 68
    const-string p1, "weight_kg"

    invoke-static {p5, p6}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p2

    invoke-virtual {v5, p1, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Double;)V

    .line 69
    const-string p1, "image_key"

    if-nez p7, :cond_0

    invoke-virtual {v5, p1}, Landroid/content/ContentValues;->putNull(Ljava/lang/String;)V

    goto :goto_0

    :cond_0
    iget-object p0, p0, Lme/ship/ShipMeDatabase;->crypto:Lme/ship/PackageCrypto;

    invoke-virtual {p0, p7}, Lme/ship/PackageCrypto;->encrypt(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v5, p1, p0}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 70
    :goto_0
    sget-object p0, Lme/ship/PackageStatus;->READY_TO_SHIP:Lme/ship/PackageStatus;

    invoke-virtual {p0}, Lme/ship/PackageStatus;->getDatabaseValue()Ljava/lang/String;

    move-result-object p0

    const-string p1, "status"

    invoke-virtual {v5, p1, p0}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 71
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide p0

    invoke-static {p0, p1}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object p0

    const-string p1, "created_at"

    invoke-virtual {v5, p1, p0}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Long;)V

    .line 72
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 63
    const-string p0, "packages"

    const/4 p1, 0x0

    invoke-virtual {v4, p0, p1, v5}, Landroid/database/sqlite/SQLiteDatabase;->insertOrThrow(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;)J

    move-result-wide p0

    return-wide p0

    .line 61
    :cond_1
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Weight cannot be negative"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 60
    :cond_2
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Destination is required"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 59
    :cond_3
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Origin is required"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 58
    :cond_4
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Package name is required"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public final getAllPackages()Ljava/util/List;
    .locals 8
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()",
            "Ljava/util/List<",
            "Lme/ship/Shipment;",
            ">;"
        }
    .end annotation

    .line 100
    invoke-virtual {p0}, Lme/ship/ShipMeDatabase;->getReadableDatabase()Landroid/database/sqlite/SQLiteDatabase;

    move-result-object v0

    .line 102
    sget-object v2, Lme/ship/ShipMeDatabase;->ALL_COLUMNS:[Ljava/lang/String;

    const/4 v6, 0x0

    .line 107
    const-string v7, "created_at DESC"

    .line 100
    const-string v1, "packages"

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x0

    invoke-virtual/range {v0 .. v7}, Landroid/database/sqlite/SQLiteDatabase;->query(Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;

    move-result-object v0

    move-object v1, v0

    check-cast v1, Ljava/io/Closeable;

    .line 108
    :try_start_0
    move-object v0, v1

    check-cast v0, Landroid/database/Cursor;

    .line 109
    invoke-static {}, Lkotlin/collections/CollectionsKt;->createListBuilder()Ljava/util/List;

    move-result-object v2

    .line 110
    :goto_0
    invoke-interface {v0}, Landroid/database/Cursor;->moveToNext()Z

    move-result v3

    if-eqz v3, :cond_0

    invoke-static {v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-direct {p0, v0}, Lme/ship/ShipMeDatabase;->toShipment(Landroid/database/Cursor;)Lme/ship/Shipment;

    move-result-object v3

    invoke-interface {v2, v3}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_0

    .line 109
    :cond_0
    invoke-static {v2}, Lkotlin/collections/CollectionsKt;->build(Ljava/util/List;)Ljava/util/List;

    move-result-object p0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const/4 v0, 0x0

    .line 108
    invoke-static {v1, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    return-object p0

    :catchall_0
    move-exception v0

    move-object p0, v0

    :try_start_1
    throw p0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception v0

    invoke-static {v1, p0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
.end method

.method public final getPackage(J)Lme/ship/Shipment;
    .locals 9

    .line 87
    invoke-virtual {p0}, Lme/ship/ShipMeDatabase;->getReadableDatabase()Landroid/database/sqlite/SQLiteDatabase;

    move-result-object v0

    .line 89
    sget-object v2, Lme/ship/ShipMeDatabase;->ALL_COLUMNS:[Ljava/lang/String;

    const/4 v1, 0x1

    .line 91
    new-array v4, v1, [Ljava/lang/String;

    const/4 v1, 0x0

    invoke-static {p1, p2}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;

    move-result-object p1

    aput-object p1, v4, v1

    const/4 v7, 0x0

    .line 95
    const-string v8, "1"

    .line 87
    const-string v1, "packages"

    const-string v3, "id = ?"

    const/4 v5, 0x0

    const/4 v6, 0x0

    invoke-virtual/range {v0 .. v8}, Landroid/database/sqlite/SQLiteDatabase;->query(Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;

    move-result-object p1

    check-cast p1, Ljava/io/Closeable;

    .line 96
    :try_start_0
    move-object p2, p1

    check-cast p2, Landroid/database/Cursor;

    .line 97
    invoke-interface {p2}, Landroid/database/Cursor;->moveToFirst()Z

    move-result v0

    const/4 v1, 0x0

    if-eqz v0, :cond_0

    invoke-static {p2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-direct {p0, p2}, Lme/ship/ShipMeDatabase;->toShipment(Landroid/database/Cursor;)Lme/ship/Shipment;

    move-result-object p0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :cond_0
    move-object p0, v1

    .line 96
    :goto_0
    invoke-static {p1, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    return-object p0

    :catchall_0
    move-exception v0

    move-object p0, v0

    :try_start_1
    throw p0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception v0

    move-object p2, v0

    invoke-static {p1, p0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw p2
.end method

.method public final moveToShipped$app(J)Z
    .locals 4

    .line 76
    invoke-virtual {p0}, Lme/ship/ShipMeDatabase;->getWritableDatabase()Landroid/database/sqlite/SQLiteDatabase;

    move-result-object p0

    .line 78
    new-instance v0, Landroid/content/ContentValues;

    invoke-direct {v0}, Landroid/content/ContentValues;-><init>()V

    .line 79
    sget-object v1, Lme/ship/PackageStatus;->SHIPPED:Lme/ship/PackageStatus;

    invoke-virtual {v1}, Lme/ship/PackageStatus;->getDatabaseValue()Ljava/lang/String;

    move-result-object v1

    const-string v2, "status"

    invoke-virtual {v0, v2, v1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 80
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v1

    invoke-static {v1, v2}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v1

    const-string v2, "shipped_at"

    invoke-virtual {v0, v2, v1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Long;)V

    .line 81
    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    const/4 v1, 0x2

    .line 83
    new-array v1, v1, [Ljava/lang/String;

    invoke-static {p1, p2}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;

    move-result-object p1

    const/4 p2, 0x0

    aput-object p1, v1, p2

    sget-object p1, Lme/ship/PackageStatus;->READY_TO_SHIP:Lme/ship/PackageStatus;

    invoke-virtual {p1}, Lme/ship/PackageStatus;->getDatabaseValue()Ljava/lang/String;

    move-result-object p1

    const/4 v2, 0x1

    aput-object p1, v1, v2

    .line 76
    const-string p1, "packages"

    const-string v3, "id = ? AND status = ?"

    invoke-virtual {p0, p1, v0, v3, v1}, Landroid/database/sqlite/SQLiteDatabase;->update(Ljava/lang/String;Landroid/content/ContentValues;Ljava/lang/String;[Ljava/lang/String;)I

    move-result p0

    if-ne p0, v2, :cond_0

    return v2

    :cond_0
    return p2
.end method

.method public onConfigure(Landroid/database/sqlite/SQLiteDatabase;)V
    .locals 1

    const-string v0, "db"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 14
    invoke-super {p0, p1}, Landroid/database/sqlite/SQLiteOpenHelper;->onConfigure(Landroid/database/sqlite/SQLiteDatabase;)V

    const/4 p0, 0x1

    .line 15
    invoke-virtual {p1, p0}, Landroid/database/sqlite/SQLiteDatabase;->setForeignKeyConstraintsEnabled(Z)V

    .line 16
    const-string p0, "PRAGMA secure_delete=ON"

    const/4 v0, 0x0

    invoke-virtual {p1, p0, v0}, Landroid/database/sqlite/SQLiteDatabase;->rawQuery(Ljava/lang/String;[Ljava/lang/String;)Landroid/database/Cursor;

    move-result-object p0

    check-cast p0, Ljava/io/Closeable;

    :try_start_0
    move-object p1, p0

    check-cast p1, Landroid/database/Cursor;

    invoke-interface {p1}, Landroid/database/Cursor;->moveToFirst()Z
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    invoke-static {p0, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    return-void

    :catchall_0
    move-exception p1

    :try_start_1
    throw p1
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception v0

    invoke-static {p0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
.end method

.method public onCreate(Landroid/database/sqlite/SQLiteDatabase;)V
    .locals 1

    const-string v0, "db"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 34
    const-string v0, "CREATE TABLE packages (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name TEXT NOT NULL,\n    origin TEXT NOT NULL,\n    destination TEXT NOT NULL,\n    description TEXT NOT NULL,\n    weight_kg REAL NOT NULL,\n    image_key TEXT,\n    status TEXT NOT NULL CHECK (status IN (\'READY_TO_SHIP\', \'SHIPPED\')),\n    created_at INTEGER NOT NULL,\n    shipped_at INTEGER\n)"

    .line 20
    invoke-virtual {p1, v0}, Landroid/database/sqlite/SQLiteDatabase;->execSQL(Ljava/lang/String;)V

    .line 36
    invoke-direct {p0, p1}, Lme/ship/ShipMeDatabase;->seedDemoPackages(Landroid/database/sqlite/SQLiteDatabase;)V

    return-void
.end method

.method public onUpgrade(Landroid/database/sqlite/SQLiteDatabase;II)V
    .locals 0

    const-string p3, "db"

    invoke-static {p1, p3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const/4 p3, 0x2

    if-ge p2, p3, :cond_0

    .line 41
    const-string p2, "DROP TABLE IF EXISTS packages"

    invoke-virtual {p1, p2}, Landroid/database/sqlite/SQLiteDatabase;->execSQL(Ljava/lang/String;)V

    .line 42
    invoke-virtual {p0, p1}, Lme/ship/ShipMeDatabase;->onCreate(Landroid/database/sqlite/SQLiteDatabase;)V

    return-void

    :cond_0
    const/4 p3, 0x3

    if-ge p2, p3, :cond_1

    .line 46
    invoke-direct {p0, p1}, Lme/ship/ShipMeDatabase;->encryptExistingMetadata(Landroid/database/sqlite/SQLiteDatabase;)V

    :cond_1
    return-void
.end method
