local socket = require("socket.core")

host = "localhost"
port = 6969

--Memory Addresses
local MemPlayerX = 0x86
local MemPlayerY = 0x3B8
local MemPlayerScreenX = 0x6D
local MemMarioPowerUpState = 0x756
local MemPowerUpShown = 0x14 
local MemPowerUpOnScreen = 0x1B
local MemPowerUpX = 0x8C
local MemPowerUpY = 0x3B9
local MemPowerUpScreenX = 0x73
local MemPowerUpState = 0x23
local MemEnemy = 0xF              -- Start range for enemies (up to 5)
local MemEnemyX = 0x87
local MemEnemyY = 0xCF
local MemEnemyScreenX = 0x6E
local MemEnemyState = 0x1E
local MemViewPortY = 0xB5

local startState = savestate.object(10)
local playerLoaded = false

local function initialize_client()

    local flag = memory.readbyte(0x8F0)    
    if memory.readbyte(0x764) == 0 and joypad.read(1)["start"] ~= true then
        print("Pressing start")
        joypad.write(1, { start = true })
    elseif flag == 0x18 then
        savestate.save(startState)
        playerLoaded = true
        print("Starting savestate initialized")
    end

    emu:frameadvance()
end

function connect(address, port, laddress, lport)
    local sock, err = socket.tcp()
    if not sock then return nil, err end
    if laddress then
        local res, err = sock:bind(laddress, lport, -1)
        if not res then return nil, err end
    end
    local res, err = sock:connect(address, port)
    if not res then return nil, err end
    return sock
end

emu.poweron()

while not playerLoaded do
    initialize_client()
end

local c = connect(host, port)
local try = socket.newtry(function() c:close() end)

local function get_gamestate()
    local state = {}
    state["score"] = memory.readbyterange(0x07DE, 6)
    state["time"] = memory.readbyterange(0x07F8, 3)

    return state
end

local function send_state(gamestate, playerstate, view, viewport_y)

    local function str_tobyte(str)
        return str:gsub(".",function(c) return string.byte(c) end)
    end

    local serialized_view = ''
    for x = 1, 12 do
        for y = 1, 10 do
            serialized_view = serialized_view .. tostring(view[y][x])
        end
    end

    local serialized_state = {
        str_tobyte(gamestate.score),
        str_tobyte(gamestate.time),
        serialized_view,
        string.format("%04d", playerstate.x),
        string.format("%03d", playerstate.y),
        string.format("%02d", playerstate.State),
        string.format("%02d", viewport_y)
    }

    try(c:send(table.concat(serialized_state)))
end

local function receive_input()
    local response = try(c:receive(1))
    if response == nil then return nil end;

    response = string.byte( response ) -- converteer de string terug naar een byte (int)

    local controls = {}
    controls["left"] = AND(response, 1) > 0
    controls["right"] = AND(response, 2) > 0
    controls["up"] = AND(response, 4) > 0
    controls["down"] = AND(response, 8) > 0
    controls["A"] = AND(response, 16) > 0
    controls["B"] = AND(response, 32) > 0

    local commands = {}
    commands["reset"] = AND(response, 64) > 0

    return controls, commands
end

local function get_view_data(player, tileMap)

    local pageSize = 16 --tiles
    local ViewRadiusX = 10
    local ViewRadiusY = 12

    local AIView = {}
    for x = 1, ViewRadiusX do
        AIView[x] = {}
    end

    for viewX = 1, ViewRadiusX do
        for viewY = 1, ViewRadiusY do

            local x = player.MapX+viewX-5
		    local y = viewY-1

            local page = math.floor( x / pageSize)

            local xAddress = x - 16*page+1
            local yAddress = y + 13*(page%2)

            if x == player.MapX-1 and y == player.MapY-1 then
                AIView[viewX][viewY] = 2 --Mark™
                AIView[viewX][viewY-1] = memory.readbyte(MemMarioPowerUpState) > 0 and 2 or AIView[viewX][viewY-1]
            elseif xAddress >= 1 and xAddress < 32 and yAddress >= 1 and yAddress <= 25 then
                AIView[viewX][viewY] = tileMap[xAddress + 16*yAddress]
            else
                AIView[viewX][viewY] = 0
            end
        end
    end

    return AIView
    
end

local function get_playerstate()
    local player = {}
    player.x = memory.readbyte(MemPlayerX) + memory.readbyte(MemPlayerScreenX)*0x100 + 4
	player.y = memory.readbyte(MemPlayerY) + 16
	player.MapX = math.floor((player.x%512)/16)+1
	player.MapY = math.floor((player.y-32)/16)+1
    player.State = memory.readbyte(0xE) 
    return player
end

local function get_map_data()

    local function set_data(mapData, x, y, value)
        local page = math.floor(x/16)
        local xAddress = x - 16*page+1
        local yAddress = y - 1 + 13*(page%2)
        if xAddress >= 1 and xAddress < 32 and yAddress >= 1 and yAddress <= 25 then 
            mapData[xAddress + 16*yAddress] = value
        end
    end

    local function get_positions(memoryX, memoryY, memoryScreenX, xOffset, yOffset)
        local positions = {}
        x = memory.readbyte(memoryX) + memory.readbyte(memoryScreenX)*0x100 - xOffset
        y = memory.readbyte(memoryY) + yOffset
        positions.X = math.floor((x%512)/16)+1
        positions.Y = math.floor((y-32)/16)
        return positions
    end

    local function get_enemies()

        local enemyMaxCount = 5 --Maximum amount of enemies on screen
        local enemies = {}
    
        for i=1, enemyMaxCount do        
            enemies[i] = {}
            if memory.readbyte(MemEnemy+(i-1)) ~= 0 then
                enemies[i] = get_positions(MemEnemyX+(i-1), MemEnemyY+(i-1), MemEnemyScreenX+(i-1), 0, 24)
            else
                enemies[i] = -1
            end
        end
    
        return enemies
    end

    object_id = {
        [0xC2] = 4,     --Coins
        -- [81] = 6,       --Breakable Blocks (With some hidden specials)
        -- [82] = 6,
        -- [87] = 6,
        -- [88] = 6,
        -- [0x23] = 6,
        -- [0xC1] = 7,     --Special Blocks
        -- [0xC0] = 7,
        -- [0x60] = 8      --Invisible Block
    }

    local tileDataTotal = 208
    local mapData = {}

	for i = 1, 2 * tileDataTotal do
        local tileId = memory.readbyte(0x500 + i-1)
        local objectId = object_id[tileId]
		if tileId ~= 0 then
			mapData[i] = (objectId ~= nil and objectId or 1)    --Defaults to block id if not defined in object_id table
		else
			mapData[i] = 0
		end
	end

    local enemies = get_enemies()
    for i=1, #enemies do
		if memory.readbyte(MemEnemy+(i-1)) ~= 0 and memory.readbyte(MemEnemyState+(i-1)) ~= 0x22 then
            set_data(mapData, enemies[i].X, enemies[i].Y, 3)
		end
	end

    if memory.readbyte(MemPowerUpShown) == 1 and 
       memory.readbyte(MemPowerUpOnScreen) == 0x2E and 
       memory.readbyte(MemPowerUpState) >= 0x07 then
        local powerup = get_positions(MemPowerUpX, MemPowerUpY, MemPowerUpScreenX, 4, 36)
        set_data(mapData, powerup.X, powerup.Y, 5)
    end

    return mapData
end

local function draw_controls(controls)

    local function get_color(control)
        if control then return "white" else return "black" end;
    end

    gui.box(180, 40, 185, 50, get_color(controls['up']))
    gui.box(180, 57, 185, 67, get_color(controls['down']))
    gui.box(169, 51, 179, 56, get_color(controls['left']))
    gui.box(186, 51, 196, 56, get_color(controls['right']))

    gui.box(210, 55, 218, 63, get_color(controls['B']))
    gui.box(225, 55, 233, 63, get_color(controls['A']))
end

local function draw_ai_view(AIView)

    local object_color = {
        [0] = {204,204,255,255},--Background
        [1] = "black",          --Block
        [2] = "blue",           --Mario
        [3] = "red",            --Enemy
        [4] = "yellow",         --Coin
        -- [5] = "green",          --Powerup
        -- [6] = {153,102,0,255},  --Breakable Block
        -- [7] = "orange",         --Special Block
        -- [8] = "magenta"         --Invisible Block
    }

    local startX = 30
    local startY = 35
    local tileSize = 2
    local padding = 1
    local paddingColor = {104,104,104,255}

    --Background
    gui.box(
        startX, 
        startY, 
        startX + (tileSize * #AIView) + (padding * #AIView) + padding,
        startY + (tileSize * #AIView[1]) + (padding * #AIView[1]) + padding,
        paddingColor
    )

    for x = 1, #AIView do
        for y = 1, #AIView[x] do
            local currentX = startX + ((x-1) * tileSize) + padding * (x-1) + padding
            local currentY = startY + ((y-1) * tileSize) + padding * (y-1) + padding
            gui.box(
                currentX, 
                currentY, 
                currentX + tileSize, 
                currentY + tileSize, 
                object_color[AIView[x][y]]
            )
        end
    end
end

while true do

    local playerstate = get_playerstate()
    local mapdata = get_map_data()
    local view = get_view_data(playerstate, mapdata)
    local viewport_y =  memory.readbyte(MemViewPortY)

    local gamestate = get_gamestate()
    send_state(gamestate, playerstate, view, viewport_y) 

    local controls, commands = receive_input()
    joypad.write(1, controls)
    -- local controls = joypad.read(1) 

    if commands["reset"] then
        savestate.load(startState)
    end

    draw_controls(controls)
    draw_ai_view(view)

    --print("X: " .. playerstate.x .. " | Y: " .. playerstate.y)
    --print("Xp: " .. playerstate.MapX .. " | Yp: " .. playerstate.MapY)

    emu:frameadvance()
end