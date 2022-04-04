local function clamp(x, min, max)
    return math.min(math.max(x, min), max);
end

local f = nil;


f = CreateFrame("Frame", "TestBorder", UIParent);
f:SetSize(5,5);
f:SetPoint("TOPLEFT");

f.border = f:CreateTexture(nil, "BACKGROUND", nil, -2);
f.border:SetAllPoints(true);

local function update_HUD()
    local player = UnitName("player");
    local health = UnitHealth(player)/UnitHealthMax(player)
    f.border:SetColorTexture(health,0,0);
    print(health);
end

f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
f:SetScript("OnEvent", update_HUD)


