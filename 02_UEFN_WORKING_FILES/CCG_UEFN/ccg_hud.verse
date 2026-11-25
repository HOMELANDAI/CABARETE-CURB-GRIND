# ccg_hud.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Persistent per-player HUD (Verse UI): score, open combo, current park, grind metres, lifetime tier.
# The hud_message_device still carries the one-shot messages (trick names, grind payouts, unlocks);
# this canvas is what the rider sees all the time. Polls the game manager's player state at HudHz.

using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Game }
using { /Fortnite.com/Playspaces }
using { /Fortnite.com/UI }
using { /UnrealEngine.com/Temporary/UI }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/Colors }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

ccg_hud<public> := class(creative_device):

    @editable Manager : ccg_game_manager = ccg_game_manager{}
    @editable HudHz : float = 5.0
    # Screen placement (fraction of the viewport, top-left anchored).
    @editable AnchorX : float = 0.02
    @editable AnchorY : float = 0.08

    MsgScore<localizes>(Score:int):message = "SCORE  {Score}"
    MsgCombo<localizes>(Count:int, Pending:int, Mult:int):message = "COMBO  x{Count}   +{Pending}   ({Mult}%)"
    MsgNoCombo<localizes>:message = "COMBO  —"
    MsgPark<localizes>(Park:string):message = "{Park}"
    MsgRoad<localizes>:message = "HIGHWAY 5 · CABARETE"
    MsgGrind<localizes>(Meters:int, Best:int):message = "GRIND {Meters} m   BEST LINE {Best}"
    MsgLifetime<localizes>(Points:int, Tier:int, Parks:int, MuralCount:int):message = "LIFETIME {Points}  ·  KAFTAN {Tier}/10  ·  PARKS {Parks}/4  ·  MURALS {MuralCount}/6"

    var Panels<private>:[player]ccg_hud_panel = map{}

    OnBegin<override>()<suspends>:void =
        for (P : GetPlayspace().GetPlayers()) { Attach(P) }
        GetPlayspace().PlayerAddedEvent().Subscribe(Attach)
        GetPlayspace().PlayerRemovedEvent().Subscribe(Detach)
        loop:
            Sleep(1.0 / HudHz)
            for (P -> Panel : Panels) { Refresh(P, Panel) }

    Attach(P:player):void =
        if (Panels[P]) then return
        if (UI := GetPlayerUI[P]):
            Gold := color{R := 0.95, G := 0.78, B := 0.25}
            White := color{R := 1.0, G := 1.0, B := 1.0}
            Teal := color{R := 0.45, G := 0.92, B := 0.88}
            Panel := ccg_hud_panel{
                Score := text_block{DefaultText := MsgScore(0), DefaultTextColor := Gold, DefaultShadowOpacity := 0.8},
                Combo := text_block{DefaultText := MsgNoCombo, DefaultTextColor := White, DefaultShadowOpacity := 0.8},
                Park := text_block{DefaultText := MsgRoad, DefaultTextColor := Teal, DefaultShadowOpacity := 0.8},
                Grind := text_block{DefaultText := MsgGrind(0, 0), DefaultTextColor := White, DefaultShadowOpacity := 0.8},
                Lifetime := text_block{DefaultText := MsgLifetime(0, 0, 0, 0), DefaultTextColor := White, DefaultShadowOpacity := 0.8}}
            Rows := array{Panel.Score, Panel.Combo, Panel.Park, Panel.Grind, Panel.Lifetime}
            var Slots:[]canvas_slot = array{}
            for (I -> W : Rows):
                Top := 30.0 * (1.0 * I)
                set Slots += array{canvas_slot{
                    Anchors := anchors{Minimum := vector2{X := AnchorX, Y := AnchorY}, Maximum := vector2{X := AnchorX, Y := AnchorY}},
                    Offsets := margin{Top := Top, Left := 0.0, Right := 0.0, Bottom := 0.0},
                    Alignment := vector2{X := 0.0, Y := 0.0},
                    SizeToContent := true,
                    Widget := W}}
            Root := canvas{Slots := Slots}
            set Panel.Root = option{Root}
            UI.AddWidget(Root)
            if (set Panels[P] = Panel) {}

    Detach(P:player):void =
        if (Panel := Panels[P], Root := Panel.Root?, UI := GetPlayerUI[P]):
            UI.RemoveWidget(Root)
        var Keep:[player]ccg_hud_panel = map{}
        for (Q -> Panel : Panels, Q <> P) { if (set Keep[Q] = Panel) {} }
        set Panels = Keep

    Refresh(P:player, Panel:ccg_hud_panel):void =
        S := Manager.GetState(P)
        Panel.Score.SetText(MsgScore(S.Score))
        Count := S.Combo.GetTrickCount()
        if (Count > 0):
            var Mult:int = 100
            if (M := Round[S.Combo.GetMultiplier() * 100.0]) then set Mult = M
            Panel.Combo.SetText(MsgCombo(Count, S.Combo.GetPendingPoints(), Mult))
        else:
            Panel.Combo.SetText(MsgNoCombo)
        if (S.CurrentPark <> ""):
            Panel.Park.SetText(MsgPark(Manager.ParkName(S.CurrentPark)))
        else:
            Panel.Park.SetText(MsgRoad)
        var Meters:int = 0
        if (M := Round[S.GrindMeters]) then set Meters = M
        Panel.Grind.SetText(MsgGrind(Meters, S.BestLine))
        Panel.Lifetime.SetText(MsgLifetime(S.LifetimePoints, S.LifetimeTiers, S.Mastered.Length, S.MuralsSeen.Length))

# The five text rows of one rider's HUD.
ccg_hud_panel := class:
    Score:text_block
    Combo:text_block
    Park:text_block
    Grind:text_block
    Lifetime:text_block
    var Root:?canvas = false
