.class public final synthetic Lme/ship/MainActivity$$ExternalSyntheticLambda2;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Landroid/content/DialogInterface$OnShowListener;


# instance fields
.field public final synthetic f$0:Landroid/app/AlertDialog;

.field public final synthetic f$1:Landroid/widget/EditText;

.field public final synthetic f$2:Landroid/widget/EditText;

.field public final synthetic f$3:Landroid/widget/EditText;

.field public final synthetic f$4:Landroid/widget/EditText;

.field public final synthetic f$5:Lme/ship/MainActivity;

.field public final synthetic f$6:Landroid/widget/EditText;

.field public final synthetic f$7:Landroid/widget/Spinner;


# direct methods
.method public synthetic constructor <init>(Landroid/app/AlertDialog;Landroid/widget/EditText;Landroid/widget/EditText;Landroid/widget/EditText;Landroid/widget/EditText;Lme/ship/MainActivity;Landroid/widget/EditText;Landroid/widget/Spinner;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$0:Landroid/app/AlertDialog;

    iput-object p2, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$1:Landroid/widget/EditText;

    iput-object p3, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$2:Landroid/widget/EditText;

    iput-object p4, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$3:Landroid/widget/EditText;

    iput-object p5, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$4:Landroid/widget/EditText;

    iput-object p6, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$5:Lme/ship/MainActivity;

    iput-object p7, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$6:Landroid/widget/EditText;

    iput-object p8, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$7:Landroid/widget/Spinner;

    return-void
.end method


# virtual methods
.method public final onShow(Landroid/content/DialogInterface;)V
    .locals 9

    .line 0
    iget-object v0, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$0:Landroid/app/AlertDialog;

    iget-object v1, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$1:Landroid/widget/EditText;

    iget-object v2, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$2:Landroid/widget/EditText;

    iget-object v3, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$3:Landroid/widget/EditText;

    iget-object v4, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$4:Landroid/widget/EditText;

    iget-object v5, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$5:Lme/ship/MainActivity;

    iget-object v6, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$6:Landroid/widget/EditText;

    iget-object v7, p0, Lme/ship/MainActivity$$ExternalSyntheticLambda2;->f$7:Landroid/widget/Spinner;

    move-object v8, p1

    invoke-static/range {v0 .. v8}, Lme/ship/MainActivity;->showCreateDialog$lambda$8(Landroid/app/AlertDialog;Landroid/widget/EditText;Landroid/widget/EditText;Landroid/widget/EditText;Landroid/widget/EditText;Lme/ship/MainActivity;Landroid/widget/EditText;Landroid/widget/Spinner;Landroid/content/DialogInterface;)V

    return-void
.end method
