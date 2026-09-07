.class public final synthetic Lme/ship/MainActivity$$ExternalSyntheticLambda3;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Landroid/view/View$OnClickListener;


# instance fields
.field public final synthetic f$0:Lme/ship/Shipment;

.field public final synthetic f$1:Landroid/widget/Button;

.field public final synthetic f$2:Lme/ship/MainActivity;


# direct methods
.method public synthetic constructor <init>(Lme/ship/Shipment;Landroid/widget/Button;Lme/ship/MainActivity;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda3;->f$0:Lme/ship/Shipment;

    iput-object p2, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda3;->f$1:Landroid/widget/Button;

    iput-object p3, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda3;->f$2:Lme/ship/MainActivity;

    return-void
.end method


# virtual methods
.method public final onClick(Landroid/view/View;)V
    .locals 2

    .line 0
    iget-object v0, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda3;->f$0:Lme/ship/Shipment;

    iget-object v1, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda3;->f$1:Landroid/widget/Button;

    iget-object p0, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda3;->f$2:Lme/ship/MainActivity;

    invoke-static {v0, v1, p0, p1}, Lme/ship/MainActivity;->createPackageCard$lambda$24$lambda$23(Lme/ship/Shipment;Landroid/widget/Button;Lme/ship/MainActivity;Landroid/view/View;)V

    return-void
.end method
