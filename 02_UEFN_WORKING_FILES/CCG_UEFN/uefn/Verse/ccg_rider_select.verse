# ccg_rider_select.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Rider select: 7 riders -> 7 class_designer_device slots (ccg_data.riders, same order).
#
#   Slot 0  Kefla             dog   (Kefla)            regular         speed 7 balance 8 air 6 flip 5
#   Slot 1  Koda the Husky    dog   (Siberian Husky)   goofy           speed 9 balance 6 air 7 flip 5
#   Slot 2  Crash the Collie  dog   (Collie)           regular         speed 6 balance 9 air 6 flip 7
#   Slot 3  Yara              human  Model 10          regular         speed 7 balance 7 air 8 flip 8
#   Slot 4  Sunny             human  Model 11          goofy           speed 8 balance 8 air 6 flip 6
#   Slot 5  Rubí              human  Model 6           regular         speed 6 balance 9 air 7 flip 7
#   Slot 6  Kai               human  Model 2           switch-capable  speed 8 balance 6 air 7 flip 9
#
# The dogs are custom meshes (Tripo OBJ -> retopo -> FBX). Fortnite does not allow custom
# player skeletal meshes; the dog "class" is a Fortnite character with the dog mesh attached as a
# prop-style cosmetic stand-in (or a Guard/NPC-style visual) — see LEVEL_BUILD_GUIDE.md -> "Riders".
# Stats are applied through the class designer (movement speed) + per-rider multipliers below.

using { /Fortnite.com/Devices }
using { /Fortnite.com/Game }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

ccg_rider := struct:
    Id:string
    Name:string
    Kind:string          # "dog" | "human"
    Model:string         # women's model number from the data; "" for dogs
    Description:string
    Stance:string
    Speed:int
    Balance:int
    Air:int
    Flip:int

ccg_rider_select<public> := class(creative_device):

    @editable Hud : hud_message_device = hud_message_device{}

    # Exactly 7 class designers, in the order listed above. The class designer defines the
    # rider (movement speed, items, visuals); it is not switched from Verse directly.
    @editable ClassSlots : []class_designer_device = array{}

    # Exactly 7 class_and_team_selector_devices, each set to the class id of the matching slot.
    # These perform the actual switch (class_and_team_selector_device.ChangeClass).
    @editable ClassSelectors : []class_and_team_selector_device = array{}

    # Exactly 7 buttons (one per podium in the select area), same order.
    @editable SelectButtons : []button_device = array{}

    var Chosen<private>:[player]int = map{}

    MsgChosen<localizes>(Name:string, Desc:string):message = "{Name} — {Desc}"

    Riders<public>():[]ccg_rider = array{
        ccg_rider{Id := "kefla", Name := "Kefla", Kind := "dog", Model := "",
            Description := "Kefla. Regular stance. Speed 7 · Balance 8 · Air 6 · Flip 5",
            Stance := "regular", Speed := 7, Balance := 8, Air := 6, Flip := 5},
        ccg_rider{Id := "koda", Name := "Koda the Husky", Kind := "dog", Model := "",
            Description := "Siberian Husky. Goofy stance. Speed 9 · Balance 6 · Air 7 · Flip 5",
            Stance := "goofy", Speed := 9, Balance := 6, Air := 7, Flip := 5},
        ccg_rider{Id := "crash", Name := "Crash the Collie", Kind := "dog", Model := "",
            Description := "Collie. Regular stance. Speed 6 · Balance 9 · Air 6 · Flip 7",
            Stance := "regular", Speed := 6, Balance := 9, Air := 6, Flip := 7},
        ccg_rider{Id := "yara", Name := "Yara", Kind := "human", Model := "Model 10",
            Description := "Model 10 — long auburn locs, gold hoops, burgundy lip, aviator glasses. Regular. Speed 7 · Balance 7 · Air 8 · Flip 8",
            Stance := "regular", Speed := 7, Balance := 7, Air := 8, Flip := 8},
        ccg_rider{Id := "sunny", Name := "Sunny", Kind := "human", Model := "Model 11",
            Description := "Model 11 — long blonde beach waves, blue eyes, drop earrings. Goofy. Speed 8 · Balance 8 · Air 6 · Flip 6",
            Stance := "goofy", Speed := 8, Balance := 8, Air := 6, Flip := 6},
        ccg_rider{Id := "rubi", Name := "Rubí", Kind := "human", Model := "Model 6",
            Description := "Model 6 — big red curls, round gold glasses, gold hoops. Regular. Speed 6 · Balance 9 · Air 7 · Flip 7",
            Stance := "regular", Speed := 6, Balance := 9, Air := 7, Flip := 7},
        ccg_rider{Id := "kai", Name := "Kai", Kind := "human", Model := "Model 2",
            Description := "Model 2 — black bob with bangs, gold aviators, gold hoops. Switch-capable. Speed 8 · Balance 6 · Air 7 · Flip 9",
            Stance := "switch-capable", Speed := 8, Balance := 6, Air := 7, Flip := 9}
    }

    OnBegin<override>()<suspends>:void =
        if (ClassSlots.Length <> 7):
            Print("ccg_rider_select: expected 7 ClassSlots, got {ClassSlots.Length}")
        if (ClassSelectors.Length <> 7):
            Print("ccg_rider_select: expected 7 ClassSelectors, got {ClassSelectors.Length}")
        for (I := 0..SelectButtons.Length - 1):
            if (Button := SelectButtons[I]):
                Binding := ccg_rider_button_binding{Selector := Self, Index := I}
                Button.InteractedWithEvent.Subscribe(Binding.OnPressed)

    # Apply rider slot Index to Agent.
    Select<public>(Index:int, Agent:agent):void =
        if (Player := player[Agent], Rider := Riders()[Index]):
            if (Selector := ClassSelectors[Index]):
                Selector.ChangeClass(Agent)
            else:
                Print("ccg_rider_select: no ClassSelector bound for slot {Index}")
            if (set Chosen[Player] = Index) {}
            Hud.SetText(MsgChosen(Rider.Name, Rider.Description))
            Hud.Show(Agent)

    # Which rider a player picked (0..6), or -1.
    GetChosenIndex<public>(Player:player):int =
        if (I := Chosen[Player]) then return I
        return -1

    GetChosenRider<public>(Player:player):?ccg_rider =
        if (I := Chosen[Player], R := Riders()[I]) then return option{R}
        return false

    # Stat multipliers other devices can read (1.0 = stat 5).
    SpeedMultiplier<public>(Player:player):float =
        if (R := GetChosenRider(Player)?) then return 0.5 + 0.1 * (1.0 * R.Speed)
        return 1.0
    FlipMultiplier<public>(Player:player):float =
        if (R := GetChosenRider(Player)?) then return 0.5 + 0.1 * (1.0 * R.Flip)
        return 1.0
    BalanceMultiplier<public>(Player:player):float =
        if (R := GetChosenRider(Player)?) then return 0.5 + 0.1 * (1.0 * R.Balance)
        return 1.0

ccg_rider_button_binding := class:
    Selector:ccg_rider_select
    Index:int
    OnPressed(Agent:agent):void = Selector.Select(Index, Agent)
