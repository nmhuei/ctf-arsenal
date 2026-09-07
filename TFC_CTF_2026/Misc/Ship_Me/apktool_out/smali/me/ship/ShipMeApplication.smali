.class public final Lme/ship/ShipMeApplication;
.super Landroid/app/Application;
.source "ShipMeApplication.kt"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lme/ship/ShipMeApplication$Companion;
    }
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u0002\n\u0002\u0008\u0002\u0018\u0000 \u00062\u00020\u0001:\u0001\u0006B\u0007\u00a2\u0006\u0004\u0008\u0002\u0010\u0003J\u0008\u0010\u0004\u001a\u00020\u0005H\u0016\u00a8\u0006\u0007"
    }
    d2 = {
        "Lme/ship/ShipMeApplication;",
        "Landroid/app/Application;",
        "<init>",
        "()V",
        "onCreate",
        "",
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
.field public static final Companion:Lme/ship/ShipMeApplication$Companion;

.field private static instance:Lme/ship/ShipMeApplication;


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lme/ship/ShipMeApplication$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lme/ship/ShipMeApplication$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lme/ship/ShipMeApplication;->Companion:Lme/ship/ShipMeApplication$Companion;

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 5
    invoke-direct {p0}, Landroid/app/Application;-><init>()V

    return-void
.end method

.method public static final synthetic access$getInstance$cp()Lme/ship/ShipMeApplication;
    .locals 1

    .line 5
    sget-object v0, Lme/ship/ShipMeApplication;->instance:Lme/ship/ShipMeApplication;

    return-object v0
.end method


# virtual methods
.method public onCreate()V
    .locals 0

    .line 7
    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    .line 8
    sput-object p0, Lme/ship/ShipMeApplication;->instance:Lme/ship/ShipMeApplication;

    return-void
.end method
