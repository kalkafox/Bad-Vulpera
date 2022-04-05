local Bad_Vulpera = {}
local BV = Bad_Vulpera;

local HF = CreateFrame("Frame", "UwU_Meter", UIParent);
local DF = CreateFrame("Frame", "Fucc_Meter", UIParent);
local PF = CreateFrame("Frame", "Heal_Meter", UIParent);

DF.modifier = 0.5
PF.modifier = 0.5

DF.r = 0
DF.g = 0
DF.b = 0

PF.r = 0
PF.g = 0
PF.b = 0

function BV.update_values(...)
    local timestamp, subevent, _, sourceGUID, sourceName, sourceFlags, sourceRaidFlags, destGUID, destName, destFlags, destRaidFlags = ...
	local spellId, spellName, spellSchool
	local amount, overkill, school, resisted, blocked, absorbed, critical, glancing, crushing, isOffHand

    local player, realm = UnitName("player")

    if player == destName then
        if subevent == "SPELL_HEAL" then
            PF.g = 1
            PF.b = 1
        end
        if subevent == "SWING_DAMAGE" then
            amount, overkill, school, resisted, blocked, absorbed, critical, glancing, crushing, isOffHand = select(12, ...)
            DF.g = 1
            DF.b = 0
            DF.r = 0
        elseif subevent == "SPELL_DAMAGE" then
            spellId, spellName, spellSchool, amount, overkill, school, resisted, blocked, absorbed, critical, glancing, crushing, isOffHand = select(12, ...)

            DF.b = 1
            DF.g = 0
            DF.r = 0
        elseif subevent == "ENVIRONMENTAL_DAMAGE" then
            DF.r = 1
            DF.g = 0
            DF.b = 0
        end
    end
end

function BV.tick_dmg(tbl, elapsed)
    DF.r = DF.r > 0 and DF.r - DF.modifier * elapsed or 0
        -- Start ticking to bring the color down after we registered whatever spell hit us
        -- Update the box with the color of the new value
        -- We use 'elapsed' here to determine the time between frames (deltatime) to make sure the animation
        -- doesn't lag behind when the FPS is low
    DF.g = DF.g > 0 and DF.g - DF.modifier * elapsed or 0-- Run the actual math that fades the color away
    DF.b = DF.b > 0 and DF.b - DF.modifier * elapsed or 0

    PF.r = PF.r > 0 and PF.r - PF.modifier * elapsed or 0
    PF.g = PF.g > 0 and PF.g - PF.modifier * elapsed or 0
    PF.b = PF.b > 0 and PF.b - PF.modifier * elapsed or 0
    local player = UnitName("player")
    local num = 1
    -- Get a value between 1 and 0 based on the player's missing health and negate it to reverse the color value
    -- Black is less intensity, red is more intensity
    -- abs is used here to remove negative values (we just want to know how far away we are from x)
    local health = math.abs(UnitHealth(player)/UnitHealthMax(player) - num)
    -- Update the pixel with the player's health color determined by the value.
    -- A value of 1 means the toy will max out at 20 (see the python script)
    -- In this case, it will just be set to red. Format is RED,GREEN,BLUE.
    HF.border:SetColorTexture(health,0,0)

    -- TODO: Filter this value to be set to 1 only and only if we are hit by spells
    -- TODO: Change color value based on the type of spell that was hit (projectile, magic, etc.)
    -- Color value can determine different types of ways to command the toy. (Green is a spell, red is melee, etc.)
    DF.border:SetColorTexture(DF.r,DF.g,DF.b)
    PF.border:SetColorTexture(PF.r,PF.g,PF.b)
end

function BV.main()
    -- Configure our frames.
    -- HF: Health Frame
    HF:SetSize(10, 10)
    HF:SetPoint("TOPLEFT")


    -- The boxes will be small pixels on the top left, and the python script will use that as a way
    -- to map those numbers to intensity values.
    HF.border = HF:CreateTexture(nil, "BACKGROUND", nil, 5);
    HF.border:SetDrawLayer("OVERLAY", 5);
    HF.border:SetAllPoints(true);
    -- Register the frame to 
    HF:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED");
    HF:SetScript("OnEvent", function() 
        BV.update_values(CombatLogGetCurrentEventInfo())
    end);

    -- DF: Damage Frame (or Spell Frame)
    DF:SetSize(10, 10);
    DF:SetPoint("TOPLEFT", 10, 0);

    DF.border = DF:CreateTexture(nil, "BACKGROUND", nil, 5);
    DF.border:SetAllPoints(true);
    DF:SetScript("OnUpdate", BV.tick_dmg);

    -- PF: Heal Frame (I know, it's the wrong abbreviation, but I'm too lazy to rewrite)
    PF:SetSize(10, 10);
    PF:SetPoint("TOPLEFT", 20, 0);

    PF.border = PF:CreateTexture(nil, "BACKGROUND", nil, 5);
    PF.border:SetAllPoints(true);

end

BV.main()


