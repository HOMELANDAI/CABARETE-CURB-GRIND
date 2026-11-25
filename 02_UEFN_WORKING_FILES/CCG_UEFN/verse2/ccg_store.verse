# ccg_store.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# HAI Skate Store (Ocean Dream Plaza, Highway 5, ~470 m from the Cabarete Sign).
# Currency = run score (ccg_data.store.currency = "points").
#
# GENERATED from ccg_data.json → store.* (flannels, knits, rainSuits, kaftans, kaftanDecks,
# starterDecks, tees, effects, clothing, collections, accessRules, deckRules). Re-run gen_store.py after a data change;
# do not hand-edit the Catalog* tables.
#
# Store tiers (95 catalog rows):
#   free      28  — granted to every player at OnBegin / on join (flannels, 2 knits, 10 starter boards)
#   purchase  29  — bought with run points through Manager.TrySpend[] (23 priced rows + bundled decks)
#   earned    38  — granted by ccg_game_manager events via GrantEarned(Agent, Key)
#
# Unlock keys the game manager fires (GrantEarned):
#   "park:P2" / "park:P3" / "park:P4"  park mastered   -> Desert Dusk kaftan + deck
#   "park:P1"                          Vagamundo mastered -> Desert Dusk kaftan + deck
#   "signgap"                          Sign Gap cleared -> Desert Dusk kaftan + deck
#   "lifetime:1".."lifetime:10"        every 25,000 lifetime points -> Original kaftan + deck ("lifetime:4" = 100k also -> Black Lunar Dragon tee)
#   "signgap"                          also -> Red Lunar Dragon tee
#   "grind:50"                         first grind worth >= 50 points -> fx_sparks (Metal Sparks effect; toggle with ToggleEffect)
#   "grinds:10|25|50", "trick:treFlip", "combo:5000|10000", "grindmeters:100" -> earned knits
#   "with:<kaftan_id>"                 fired internally when a kaftan is granted -> its deck
#
# Purchase rows — wire PurchaseButtons[i] / PurchaseGranters[i] in THIS order:
#   [ 0] rain_spicefront                  Home of the Spicefront  (5,500 pts)
#   [ 1] rain_vicewave_shepherd           Home of the Vicewave (Shepherd)  (5,500 pts)
#   [ 2] rain_vicewave_husky              Home of the Vicewave (Husky)  (5,500 pts)
#   [ 3] rain_stormburn                   Home of the Stormburn  (5,500 pts)
#   [ 4] rain_purpledown                  Home of the Purpledown  (5,500 pts)
#   [ 5] kaftan_ruff_royalty              Home of Ruff Royalty  (7,500 pts)
#   [ 6] kaftan_paw_prestige              Home of Paw Prestige  (7,500 pts)
#   [ 7] kaftan_bark_opulence             Home of Bark Opulence  (7,500 pts)
#   [ 8] kaftan_howl_dynasty              Home of Howl Dynasty  (7,500 pts)
#   [ 9] kaftan_ruff_legacy               Home of Ruff Legacy  (7,500 pts)
#   [10] kaftan_paw_icon                  Home of Paw Icon  (7,500 pts)
#   [11] maroon_crest_wrap                Maroon Crest Wrap  (2,500 pts)
#   [12] auburn_sunrise_cardigan          Auburn Sunrise Cardigan  (2,500 pts)
#   [13] purplescale_crest_cardigan       Purplescale Crest Cardigan  (2,500 pts)
#   [14] carbon_slice_block               Carbon Slice Block  (2,500 pts)
#   [15] cobalt_core_split                Cobalt Core Split  (2,500 pts)
#   [16] logo_flood_luxe                  Logo Flood Luxe  (2,500 pts)
#   [17] suede_stripe_statement           Suede Stripe Statement  (2,500 pts)
#   [18] comic_frame_split                Comic Frame Split  (2,500 pts)
#   [19] neon_circuit_cardigan            Neon Circuit Cardigan  (2,500 pts)
#   [20] ivory                            HomelandAI Ivory Skateboard Collection  (4,000 pts)
#   [21] carved_nine                      The Carved Nine  (6,000 pts)
#   [22] dojo                             HAI Dojo Deck Collection (Karate Gi Series)  (5,000 pts)
#
# NOTE: Fortnite cannot grant real deck/clothing cosmetics. Model decks as prop pickups / wraps in the
# granters and garments as wraps or class changes. See LEVEL_BUILD_GUIDE.md -> "Store".

using { /Fortnite.com/Devices }
using { /Fortnite.com/Game }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# One row of the catalog.
ccg_store_item := struct:
    Id:string
    Name:string
    Kind:string          # flannel | knit | rainsuit | kaftan | kaftan_deck | deck | tee | effect | clothing | collection
    Tier:string          # free | purchase | earned
    Price:int            # points (0 for free / earned / bundled rows)
    Unlock:string        # player-facing unlock text
    UnlockKey:string     # machine key matched by GrantEarned ("" = none)
    Deck:string          # matching deck id / name ("" = none)
    Info:string          # size, dog, pairing, tier or collection style
    NeedsMastery:logic   # collections: buyable only once any park is mastered (deckRules.purchase)

ccg_store<public> := class(creative_device):

    # The game manager injects itself at OnBegin (Store.SetManager(Self)) — an @editable in both directions
    # would be a circular default-construction and the Verse linker rejects it.
    var Manager<private>:?ccg_game_manager = false
    SetManager<public>(M:ccg_game_manager):void = set Manager = option{M}
    @editable Hud : hud_message_device = hud_message_device{}

    # One button + one granter per PRICED purchase row, in the order listed in the header comment.
    @editable PurchaseButtons : []button_device = array{}
    @editable PurchaseGranters : []item_granter_device = array{}

    # Optional: one granter per catalog row (same order as Catalog()) for free/earned cosmetics.
    # Leave empty to track ownership only.
    @editable CosmeticGranters : []item_granter_device = array{}

    LifetimeThreshold<public>:int = 25000

    MsgBought<localizes>(Item:string, Price:int, Left:int):message = "Bought {Item} for {Price} — {Left} points left"
    MsgTooPoor<localizes>(Item:string, Price:int, Have:int):message = "{Item} costs {Price} — you have {Have}"
    MsgOwned<localizes>(Item:string):message = "You already own {Item}"
    MsgNeedsMastery<localizes>(Item:string):message = "{Item} — master one park first"
    MsgUnlocked<localizes>(Item:string, How:string):message = "UNLOCKED {Item} — {How}"
    MsgFreeKit<localizes>(Count:int):message = "HAI Skate Store: {Count} free flannels, knits and boards are yours"

    # Owned item ids per player.
    var Owned<private>:[player][]string = map{}
    # Enabled effect ids per player (effects are off by default even when owned).
    var FxEnabled<private>:[player][]string = map{}
    # Optional button that toggles Metal Sparks (store > Effects).
    @editable EffectToggleButton : button_device = button_device{}
    MsgFxOn<localizes>(Item:string):message = "{Item} ON"
    MsgFxOff<localizes>(Item:string):message = "{Item} OFF"
    MsgFxLocked<localizes>(Item:string, How:string):message = "{Item} is locked — {How}"

    # ------------------------------------------------------------------
    # Catalog (generated)
    # ------------------------------------------------------------------
    Catalog<public>()<transacts>:[]ccg_store_item =
        CatalogFlannels() + CatalogKnits() + CatalogRainSuits() + CatalogKaftans() + CatalogKaftanDecks() + CatalogStarterDecks() + CatalogTees() + CatalogEffects() + CatalogClothing() + CatalogCollections()

    CatalogFlannels()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "flannel_purple_plus", Name := "Purple Plus", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_jacq_supreme", Name := "Jacq Supreme", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_sage_spice", Name := "Sage Spice", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_carbon_slice", Name := "Carbon Slice", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_olympic_club_edition", Name := "Olympic Club Edition", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_moss_gang_color_rush", Name := "Moss Gang Color Rush", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_varsity_letterman_club", Name := "Varsity Letterman Club", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_plaid_out", Name := "Plaid Out", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_vice_edition", Name := "Vice Edition", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_deep_plaids", Name := "Deep Plaids", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_mandarin_ghost_edition", Name := "Mandarin Ghost Edition", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_limited_v2_edition", Name := "Limited V2 Edition", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_sepia_pro_max_edition", Name := "Sepia Pro Max Edition", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_blue_chrome_edition", Name := "Blue Chrome Edition", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_festival_plaid_neon_pop", Name := "Festival Plaid Neon Pop", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false},
        ccg_store_item{Id := "flannel_battle_flannel_tactical_mode", Name := "Battle Flannel Tactical Mode", Kind := "flannel", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "HAI Plaid Flannel Sets", NeedsMastery := false}
    }

    CatalogKnits()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "knit_frenchie_varsity", Name := "Frenchie Varsity", Kind := "knit", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "French Bulldog", NeedsMastery := false},
        ccg_store_item{Id := "knit_bully_blackout", Name := "Bully Blackout", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: 10 clean grinds", UnlockKey := "grinds:10", Deck := "", Info := "American Bully", NeedsMastery := false},
        ccg_store_item{Id := "knit_husky_bluecrown", Name := "Husky Blue Crown", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: land your first tre flip", UnlockKey := "trick:treFlip", Deck := "", Info := "Siberian Husky", NeedsMastery := false},
        ccg_store_item{Id := "knit_spaniel_tartan", Name := "Spaniel Tartan", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: bank a 5,000-point combo", UnlockKey := "combo:5000", Deck := "", Info := "Cocker Spaniel", NeedsMastery := false},
        ccg_store_item{Id := "knit_greyhound_aifuture", Name := "Greyhound AI Future", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: 25 clean grinds", UnlockKey := "grinds:25", Deck := "", Info := "Greyhound", NeedsMastery := false},
        ccg_store_item{Id := "knit_afghan_rosegold", Name := "Afghan Rose Gold", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: bank a 10,000-point combo", UnlockKey := "combo:10000", Deck := "", Info := "Afghan Hound", NeedsMastery := false},
        ccg_store_item{Id := "knit_collie_uplink", Name := "Collie Uplink", Kind := "knit", Tier := "free", Price := 0, Unlock := "Free from the first run", UnlockKey := "", Deck := "", Info := "Border Collie", NeedsMastery := false},
        ccg_store_item{Id := "knit_schnauzer_crest", Name := "Schnauzer Crest", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: 100 m of grinding in one run", UnlockKey := "grindmeters:100", Deck := "", Info := "Schnauzer", NeedsMastery := false},
        ccg_store_item{Id := "knit_bernese_aimode", Name := "Bernese AI Mode", Kind := "knit", Tier := "earned", Price := 0, Unlock := "Trick milestone: 50 clean grinds", UnlockKey := "grinds:50", Deck := "", Info := "Bernese Mountain Dog", NeedsMastery := false}
    }

    CatalogRainSuits()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "rain_spicefront", Name := "Home of the Spicefront", Kind := "rainsuit", Tier := "purchase", Price := 5500, Unlock := "Buy at the HAI Skate Store (includes the Sage Spice Drizzle Drop cruiser; cancels wet-ground slip)", UnlockKey := "", Deck := "Sage Spice Drizzle Drop", Info := "Golden Retriever", NeedsMastery := false},
        ccg_store_item{Id := "rain_vicewave_shepherd", Name := "Home of the Vicewave (Shepherd)", Kind := "rainsuit", Tier := "purchase", Price := 5500, Unlock := "Buy at the HAI Skate Store (includes the Vicewave Swell cruiser; cancels wet-ground slip)", UnlockKey := "", Deck := "Vicewave Swell", Info := "German Shepherd", NeedsMastery := false},
        ccg_store_item{Id := "rain_vicewave_husky", Name := "Home of the Vicewave (Husky)", Kind := "rainsuit", Tier := "purchase", Price := 5500, Unlock := "Buy at the HAI Skate Store (includes the Vice Monsoon Luxe Remix cruiser; cancels wet-ground slip)", UnlockKey := "", Deck := "Vice Monsoon Luxe Remix", Info := "Husky", NeedsMastery := false},
        ccg_store_item{Id := "rain_stormburn", Name := "Home of the Stormburn", Kind := "rainsuit", Tier := "purchase", Price := 5500, Unlock := "Buy at the HAI Skate Store (includes the Stormburn Sunrise cruiser; cancels wet-ground slip)", UnlockKey := "", Deck := "Stormburn Sunrise", Info := "Boxer", NeedsMastery := false},
        ccg_store_item{Id := "rain_purpledown", Name := "Home of the Purpledown", Kind := "rainsuit", Tier := "purchase", Price := 5500, Unlock := "Buy at the HAI Skate Store (includes the Purpledown Drip cruiser; cancels wet-ground slip)", UnlockKey := "", Deck := "Purpledown Drip", Info := "Shiba Inu", NeedsMastery := false}
    }

    CatalogKaftans()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "kaftan_ruff_scripture", Name := "Home of Ruff Scripture", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "25,000 lifetime points (Originals tier 1/10)", UnlockKey := "lifetime:1", Deck := "deck_ruff_scripture", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_paw_sandstorm", Name := "Home of Paw Sandstorm", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "50,000 lifetime points (Originals tier 2/10)", UnlockKey := "lifetime:2", Deck := "deck_paw_sandstorm", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_bark_code", Name := "Home of Bark Code", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "75,000 lifetime points (Originals tier 3/10)", UnlockKey := "lifetime:3", Deck := "deck_bark_code", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_howl_archive", Name := "Home of Howl Archive", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "100,000 lifetime points (Originals tier 4/10)", UnlockKey := "lifetime:4", Deck := "deck_howl_archive", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_ruff_future", Name := "Home of Ruff Future", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "125,000 lifetime points (Originals tier 5/10)", UnlockKey := "lifetime:5", Deck := "deck_ruff_future", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_paw_nomad", Name := "Home of Paw Nomad", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "150,000 lifetime points (Originals tier 6/10)", UnlockKey := "lifetime:6", Deck := "deck_paw_nomad", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_bark_couture", Name := "Home of Bark Couture", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "175,000 lifetime points (Originals tier 7/10)", UnlockKey := "lifetime:7", Deck := "deck_bark_couture", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_howl_sync", Name := "Home of Howl Sync", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "200,000 lifetime points (Originals tier 8/10)", UnlockKey := "lifetime:8", Deck := "deck_howl_sync", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_paw_dynasty", Name := "Home of Paw Dynasty", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "225,000 lifetime points (Originals tier 9/10)", UnlockKey := "lifetime:9", Deck := "deck_paw_dynasty", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_ruff_frequency", Name := "Home of Ruff Frequency", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "250,000 lifetime points (Originals tier 10/10)", UnlockKey := "lifetime:10", Deck := "deck_ruff_frequency", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_ruff_royalty", Name := "Home of Ruff Royalty", Kind := "kaftan", Tier := "purchase", Price := 7500, Unlock := "Buy at the HAI Skate Store (includes the matching deck)", UnlockKey := "", Deck := "deck_ruff_royalty", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_paw_prestige", Name := "Home of Paw Prestige", Kind := "kaftan", Tier := "purchase", Price := 7500, Unlock := "Buy at the HAI Skate Store (includes the matching deck)", UnlockKey := "", Deck := "deck_paw_prestige", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_bark_opulence", Name := "Home of Bark Opulence", Kind := "kaftan", Tier := "purchase", Price := 7500, Unlock := "Buy at the HAI Skate Store (includes the matching deck)", UnlockKey := "", Deck := "deck_bark_opulence", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_howl_dynasty", Name := "Home of Howl Dynasty", Kind := "kaftan", Tier := "purchase", Price := 7500, Unlock := "Buy at the HAI Skate Store (includes the matching deck)", UnlockKey := "", Deck := "deck_howl_dynasty", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_ruff_legacy", Name := "Home of Ruff Legacy", Kind := "kaftan", Tier := "purchase", Price := 7500, Unlock := "Buy at the HAI Skate Store (includes the matching deck)", UnlockKey := "", Deck := "deck_ruff_legacy", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_paw_icon", Name := "Home of Paw Icon", Kind := "kaftan", Tier := "purchase", Price := 7500, Unlock := "Buy at the HAI Skate Store (includes the matching deck)", UnlockKey := "", Deck := "deck_paw_icon", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_ruff_scripture_dusk", Name := "Home of Ruff Scripture — Desert Dusk", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "Master Carve Cabarete Multiplex", UnlockKey := "park:P2", Deck := "deck_ruff_scripture_dusk", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_paw_sandstorm_dusk", Name := "Home of Paw Sandstorm — Desert Dusk", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "Master Mojito Skate Park", UnlockKey := "park:P3", Deck := "deck_paw_sandstorm_dusk", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_bark_code_dusk", Name := "Home of Bark Code — Desert Dusk", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "Master Courtyard Cabarete Skatepark", UnlockKey := "park:P4", Deck := "deck_bark_code_dusk", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_howl_archive_dusk", Name := "Home of Howl Archive — Desert Dusk", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "Clear the Sign Gap", UnlockKey := "signgap", Deck := "deck_howl_archive_dusk", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "kaftan_ruff_future_dusk", Name := "Home of Ruff Future — Desert Dusk", Kind := "kaftan", Tier := "earned", Price := 0, Unlock := "Master Vagamundo Hybrid Park", UnlockKey := "park:P1", Deck := "deck_ruff_future_dusk", Info := "Desert Dusk Variants", NeedsMastery := false}
    }

    CatalogKaftanDecks()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "deck_ruff_scripture", Name := "Home of Ruff Scripture", Kind := "kaftan_deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "longboard 36\"", NeedsMastery := false},
        ccg_store_item{Id := "deck_paw_sandstorm", Name := "Home of Paw Sandstorm", Kind := "kaftan_deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "cruiser 32\"", NeedsMastery := false},
        ccg_store_item{Id := "deck_bark_code", Name := "Home of Bark Code", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Bark Code", UnlockKey := "with:kaftan_bark_code", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_howl_archive", Name := "Home of Howl Archive", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Howl Archive", UnlockKey := "with:kaftan_howl_archive", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_ruff_future", Name := "Home of Ruff Future", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Ruff Future", UnlockKey := "with:kaftan_ruff_future", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_paw_nomad", Name := "Home of Paw Nomad", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Paw Nomad", UnlockKey := "with:kaftan_paw_nomad", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_bark_couture", Name := "Home of Bark Couture", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Bark Couture", UnlockKey := "with:kaftan_bark_couture", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_howl_sync", Name := "Home of Howl Sync", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Howl Sync", UnlockKey := "with:kaftan_howl_sync", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_paw_dynasty", Name := "Home of Paw Dynasty", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Paw Dynasty", UnlockKey := "with:kaftan_paw_dynasty", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_ruff_frequency", Name := "Home of Ruff Frequency", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Ruff Frequency", UnlockKey := "with:kaftan_ruff_frequency", Deck := "", Info := "Original Hooded Kaftans", NeedsMastery := false},
        ccg_store_item{Id := "deck_ruff_royalty", Name := "Home of Ruff Royalty", Kind := "kaftan_deck", Tier := "purchase", Price := 0, Unlock := "Unlocks with Home of Ruff Royalty", UnlockKey := "with:kaftan_ruff_royalty", Deck := "", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "deck_paw_prestige", Name := "Home of Paw Prestige", Kind := "kaftan_deck", Tier := "purchase", Price := 0, Unlock := "Unlocks with Home of Paw Prestige", UnlockKey := "with:kaftan_paw_prestige", Deck := "", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "deck_bark_opulence", Name := "Home of Bark Opulence", Kind := "kaftan_deck", Tier := "purchase", Price := 0, Unlock := "Unlocks with Home of Bark Opulence", UnlockKey := "with:kaftan_bark_opulence", Deck := "", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "deck_howl_dynasty", Name := "Home of Howl Dynasty", Kind := "kaftan_deck", Tier := "purchase", Price := 0, Unlock := "Unlocks with Home of Howl Dynasty", UnlockKey := "with:kaftan_howl_dynasty", Deck := "", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "deck_ruff_legacy", Name := "Home of Ruff Legacy", Kind := "kaftan_deck", Tier := "purchase", Price := 0, Unlock := "Unlocks with Home of Ruff Legacy", UnlockKey := "with:kaftan_ruff_legacy", Deck := "", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "deck_paw_icon", Name := "Home of Paw Icon", Kind := "kaftan_deck", Tier := "purchase", Price := 0, Unlock := "Unlocks with Home of Paw Icon", UnlockKey := "with:kaftan_paw_icon", Deck := "", Info := "Dapper Dan Remixes", NeedsMastery := false},
        ccg_store_item{Id := "deck_ruff_scripture_dusk", Name := "Home of Ruff Scripture — Desert Dusk", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Ruff Scripture — Desert Dusk", UnlockKey := "with:kaftan_ruff_scripture_dusk", Deck := "", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "deck_paw_sandstorm_dusk", Name := "Home of Paw Sandstorm — Desert Dusk", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Paw Sandstorm — Desert Dusk", UnlockKey := "with:kaftan_paw_sandstorm_dusk", Deck := "", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "deck_bark_code_dusk", Name := "Home of Bark Code — Desert Dusk", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Bark Code — Desert Dusk", UnlockKey := "with:kaftan_bark_code_dusk", Deck := "", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "deck_howl_archive_dusk", Name := "Home of Howl Archive — Desert Dusk", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Howl Archive — Desert Dusk", UnlockKey := "with:kaftan_howl_archive_dusk", Deck := "", Info := "Desert Dusk Variants", NeedsMastery := false},
        ccg_store_item{Id := "deck_ruff_future_dusk", Name := "Home of Ruff Future — Desert Dusk", Kind := "kaftan_deck", Tier := "earned", Price := 0, Unlock := "Unlocks with Home of Ruff Future — Desert Dusk", UnlockKey := "with:kaftan_ruff_future_dusk", Deck := "", Info := "Desert Dusk Variants", NeedsMastery := false}
    }

    CatalogStarterDecks()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "deck_ivory_grid_supreme", Name := "Ivory Grid Supreme", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "popsicle 8.0\" · HomelandAI Ivory", NeedsMastery := false},
        ccg_store_item{Id := "deck_carved_ivory_wave", Name := "Carved Ivory Wave", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "popsicle 8.25\" · HomelandAI Ivory", NeedsMastery := false},
        ccg_store_item{Id := "deck_ivory_mandala_flow", Name := "Ivory Mandala Flow", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "popsicle 7.75\" · HomelandAI Ivory", NeedsMastery := false},
        ccg_store_item{Id := "deck_bulldog_crest", Name := "Bulldog Crest", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "popsicle 8.5\" · The Carved Nine", NeedsMastery := false},
        ccg_store_item{Id := "deck_cobalt_trail", Name := "Cobalt Trail", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "cruiser 29\" · The Carved Nine", NeedsMastery := false},
        ccg_store_item{Id := "deck_terrierbyte", Name := "Terrierbyte", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "popsicle 8.0\" · The Carved Nine", NeedsMastery := false},
        ccg_store_item{Id := "deck_silk_spin_kata", Name := "Silk Spin Kata", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "popsicle 8.25\" · HAI Dojo", NeedsMastery := false},
        ccg_store_item{Id := "deck_golden_paw_strike", Name := "Golden Paw Strike", Kind := "deck", Tier := "free", Price := 0, Unlock := "Starter board — free from the first run", UnlockKey := "", Deck := "", Info := "old school 9.5\" · HAI Dojo", NeedsMastery := false}
    }

    CatalogTees()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "tee_red_lunar_dragon", Name := "Red Lunar Dragon Edition", Kind := "tee", Tier := "earned", Price := 0, Unlock := "First Sign Gap", UnlockKey := "signgap", Deck := "", Info := "Lunar Dragon Tees", NeedsMastery := false},
        ccg_store_item{Id := "tee_black_lunar_dragon", Name := "Black Lunar Dragon Edition", Kind := "tee", Tier := "earned", Price := 0, Unlock := "100,000 lifetime points", UnlockKey := "lifetime:4", Deck := "", Info := "Lunar Dragon Tees", NeedsMastery := false}
    }

    CatalogEffects()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "fx_sparks", Name := "Metal Sparks", Kind := "effect", Tier := "earned", Price := 0, Unlock := "First 50-point grind (toggle in the store or pause menu; off by default)", UnlockKey := "grind:50", Deck := "", Info := "Effects", NeedsMastery := false}
    }

    CatalogClothing()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "maroon_crest_wrap", Name := "Maroon Crest Wrap", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Bulldog Crest", Info := "pairs with Bulldog Crest", NeedsMastery := false},
        ccg_store_item{Id := "auburn_sunrise_cardigan", Name := "Auburn Sunrise Cardigan", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Sunrise Scholar", Info := "pairs with Sunrise Scholar", NeedsMastery := false},
        ccg_store_item{Id := "purplescale_crest_cardigan", Name := "Purplescale Crest Cardigan", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Howl Couture", Info := "pairs with Howl Couture", NeedsMastery := false},
        ccg_store_item{Id := "carbon_slice_block", Name := "Carbon Slice Block", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Carbon Bark", Info := "pairs with Carbon Bark", NeedsMastery := false},
        ccg_store_item{Id := "cobalt_core_split", Name := "Cobalt Core Split", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Cobalt Trail", Info := "pairs with Cobalt Trail", NeedsMastery := false},
        ccg_store_item{Id := "logo_flood_luxe", Name := "Logo Flood Luxe", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Ruff Royale", Info := "pairs with Ruff Royale", NeedsMastery := false},
        ccg_store_item{Id := "suede_stripe_statement", Name := "Suede Stripe Statement", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Pawshion Avenue", Info := "pairs with Pawshion Avenue", NeedsMastery := false},
        ccg_store_item{Id := "comic_frame_split", Name := "Comic Frame Split", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Pawsibility", Info := "pairs with Pawsibility", NeedsMastery := false},
        ccg_store_item{Id := "neon_circuit_cardigan", Name := "Neon Circuit Cardigan", Kind := "clothing", Tier := "purchase", Price := 2500, Unlock := "Buy at the HAI Skate Store", UnlockKey := "", Deck := "Terrierbyte", Info := "pairs with Terrierbyte", NeedsMastery := false}
    }

    CatalogCollections()<transacts>:[]ccg_store_item = array{
        ccg_store_item{Id := "ivory", Name := "HomelandAI Ivory Skateboard Collection", Kind := "collection", Tier := "purchase", Price := 4000, Unlock := "Buy as a set once one park is mastered (6 decks)", UnlockKey := "", Deck := "", Info := "ivory carved", NeedsMastery := true},
        ccg_store_item{Id := "carved_nine", Name := "The Carved Nine", Kind := "collection", Tier := "purchase", Price := 6000, Unlock := "Buy as a set once one park is mastered (9 decks)", UnlockKey := "", Deck := "", Info := "dry-carved wood", NeedsMastery := true},
        ccg_store_item{Id := "dojo", Name := "HAI Dojo Deck Collection (Karate Gi Series)", Kind := "collection", Tier := "purchase", Price := 5000, Unlock := "Buy as a set once one park is mastered (11 decks)", UnlockKey := "", Deck := "", Info := "carved gi", NeedsMastery := true}
    }

    # Priced purchase rows, in button/granter order.
    PurchaseRows<public>()<transacts>:[]ccg_store_item =
        var Rows:[]ccg_store_item = array{}
        for (Item : Catalog(), Item.Tier = "purchase", Item.Price > 0):
            set Rows += array{Item}
        return Rows

    FindItem<public>(Id:string)<decides><transacts>:ccg_store_item =
        var Found:?ccg_store_item = false
        for (Item : Catalog(), Item.Id = Id):
            set Found = option{Item}
        Found?

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    OnBegin<override>()<suspends>:void =
        Rows := PurchaseRows()
        for (I := 0..Rows.Length - 1):
            if (Button := PurchaseButtons[I]):
                Binding := ccg_store_button_binding{Store := Self, Index := I}
                Button.InteractedWithEvent.Subscribe(Binding.OnPressed)

        EffectToggleButton.InteractedWithEvent.Subscribe(OnEffectButton)

        # Free tier: everyone present now, and everyone who joins later.
        for (P : GetPlayspace().GetPlayers()) { GrantFree(P) }
        GetPlayspace().PlayerAddedEvent().Subscribe(OnPlayerAdded)

    OnPlayerAdded(Player:player):void = GrantFree(Player)

    # Grant every "free" row to Player (idempotent).
    GrantFree<public>(Player:player):void =
        var Count:int = 0
        for (Item : Catalog(), Item.Tier = "free"):
            if (not OwnsItem(Player, Item.Id)?):
                GrantItem(Player, Item, false)
                set Count += 1
        if (Count > 0):
            ShowHud(Player, MsgFreeKit(Count))

    # Grant every "earned" row whose UnlockKey = Key (idempotent). Called by ccg_game_manager.
    GrantEarned<public>(Agent:agent, Key:string):void =
        if (Player := player[Agent]):
            for (Item : Catalog(), Item.UnlockKey = Key):
                if (not OwnsItem(Player, Item.Id)?):
                    GrantItem(Player, Item, true)

    # Lifetime-points tier N (1..10) -> Original kaftan N (+ its deck).
    GrantLifetimeTier<public>(Agent:agent, Tier:int):void =
        GrantEarned(Agent, "lifetime:{Tier}")

    # ------------------------------------------------------------------
    # Purchases
    # ------------------------------------------------------------------
    TryBuy<public>(Index:int, Agent:agent):void =
        if (Player := player[Agent], Item := PurchaseRows()[Index]):
            if (OwnsItem(Player, Item.Id)?):
                ShowHud(Player, MsgOwned(Item.Name))
                return
            if (M := Manager?):
                if (Item.NeedsMastery?, M.GetState(Player).Mastered.Length < 1):
                    ShowHud(Player, MsgNeedsMastery(Item.Name))
                    return
                if (M.TrySpend[Player, Item.Price]):
                    if (Granter := PurchaseGranters[Index]) then Granter.GrantItem(Agent)
                    GrantItem(Player, Item, false)
                    ShowHud(Player, MsgBought(Item.Name, Item.Price, M.GetScore(Player)))
                else:
                    ShowHud(Player, MsgTooPoor(Item.Name, Item.Price, M.GetScore(Player)))

    # ------------------------------------------------------------------
    # Effects (kind "effect"): owned via GrantEarned, enabled per player with ToggleEffect
    # ------------------------------------------------------------------
    OnEffectButton(Agent:agent):void = ToggleEffect(Agent, "fx_sparks")

    ToggleEffect<public>(Agent:agent, Id:string):void =
        if (Player := player[Agent], Item := FindItem[Id]):
            if (not OwnsItem(Player, Id)?):
                ShowHud(Player, MsgFxLocked(Item.Name, Item.Unlock))
                return
            if (IsEffectActive(Player, Id)?):
                var List:[]string = array{}
                for (Entry : FxEnabledIds(Player), Entry <> Id) { set List += array{Entry} }
                if (set FxEnabled[Player] = List) {}
                ShowHud(Player, MsgFxOff(Item.Name))
            else:
                if (set FxEnabled[Player] = FxEnabledIds(Player) + array{Id}) {}
                ShowHud(Player, MsgFxOn(Item.Name))

    # True when the player owns the effect AND has switched it on (ccg_rail asks this for Metal Sparks).
    IsEffectActive<public>(Player:player, Id:string)<transacts>:logic =
        if (not OwnsItem(Player, Id)?) then return false
        for (Entry : FxEnabledIds(Player), Entry = Id) { return true }
        return false

    FxEnabledIds<private>(Player:player)<transacts>:[]string =
        if (List := FxEnabled[Player]) then return List
        return array{}

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------
    GrantItem<private>(Player:player, Item:ccg_store_item, Announce:logic):void =
        MarkOwned(Player, Item.Id)
        if (Granter := CosmeticGranters[CatalogIndex(Item.Id)]) then Granter.GrantItem(Player)
        if (Announce?) then ShowHud(Player, MsgUnlocked(Item.Name, Item.Unlock))
        # Bundled rows (kaftan decks) unlock with their kaftan.
        for (Bundled : Catalog(), Bundled.UnlockKey = "with:{Item.Id}"):
            if (not OwnsItem(Player, Bundled.Id)?):
                MarkOwned(Player, Bundled.Id)
                if (Granter := CosmeticGranters[CatalogIndex(Bundled.Id)]) then Granter.GrantItem(Player)

    CatalogIndex<private>(Id:string)<transacts>:int =
        Items := Catalog()
        for (I := 0..Items.Length - 1):
            if (Item := Items[I], Item.Id = Id) then return I
        return -1

    OwnsItem<public>(Player:player, Id:string)<transacts>:logic =
        if (List := Owned[Player]):
            for (Entry : List, Entry = Id) { return true }
        return false

    OwnedIds<public>(Player:player):[]string =
        if (List := Owned[Player]) then return List
        return array{}

    MarkOwned<private>(Player:player, Id:string):void =
        var List:[]string = array{}
        if (Existing := Owned[Player]) then set List = Existing
        set List += array{Id}
        if (set Owned[Player] = List) {}

    ShowHud<private>(Agent:agent, Text:message):void =
        Hud.SetText(Text)
        Hud.Show(Agent)

ccg_store_button_binding := class:
    Store:ccg_store
    Index:int
    OnPressed(Agent:agent):void = Store.TryBuy(Index, Agent)
