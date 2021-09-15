local socket = require("socket")

host = "localhost"
port = 6969

startState = savestate.object(1)
savestate.save(startState)

local c = socket.try(socket.connect(host, port))
local try = socket.newtry(function() c:close() end)

--Memory Addresses
MemPlayerX = 0x86
MemPlayerY = 0x3B8
MemPlayerScreenX = 0x6D

--Variables
ViewRadiusX = 10
ViewRadiusY = 10

playerX = 0
playerY = 0
playerRoomX = 0
playerRoomY = 0
MapPlayerX = 0
MapPlayerY = 0

TileDataTotal = 208

AIView = {}
for x = 0, ViewRadiusX do
    AIView[x] = {}
    for y = 0, ViewRadiusY do
        AIView[x][y] = 0
    end
end

tileMap = {}
for i = 1, 2 * TileDataTotal do
	tileMap[i] = 0
end

running = true

local function get_state()
    local state = {}
    state["score"] = memory.readbyterange(0x07DE, 6)
    state["xposition"] = memory.readbyterange(MemPlayerX, 1)
    state["time"] = memory.readbyterange(0x07F8, 3)
    state["dead"] = memory.readbyte(0x00E)

    return state
end

local function send_state(state)
    try(c:send(state["score"] .. state["time"] .. state["xposition"] .. state["dead"]))
end

local function receive_input()
    local response = try(c:receive(7))
    if response == nil then return nil end;
    local lookup_table = { ['1']=true, ['0']=false }

    local l,r,u,d,a,b,reset = response:match('(%d)(%d)(%d)(%d)(%d)(%d)(%d)')

    if lookup_table[reset] then savestate.load(startState) end;

    local controls = {}
    controls["left"] = lookup_table[l]
    controls["right"] = lookup_table[r]
    controls["up"] = lookup_table[u]
    controls["down"] = lookup_table[d]
    controls["A"] = lookup_table[a]
    controls["B"] = lookup_table[b]

    return controls
end

local function set_view_data()

    local x = 0
    local y = 0

    for viewX = 0, ViewRadiusX do
        for viewY = 0, ViewRadiusY do

            local pageSize = 16 --tiles

            local x = MapPlayerX + x - 1
            local y = MapPlayerY + y - 1

            local page = math.floor(x/pageSize)

            local xAddress = x - 16 * page + 1
            local yAddress = y + 13 * (page % 2)
           
            if xAddress >= 1 and xAddress < 32 and
               yAddress >= 1 and yAddress < 25 then

                AIView[x][y] = tileMap[xAddress + 16 * yAddress]

            else

                AIView[x][y] = 0

            end
        end
    end
end

local function set_player_data()
    playerX = memory.readbyte(MemPlayerX) + memory.readbyte(MemPlayerScreenX)*0x100 + 4
	playerY = memory.readbyte(MemPlayerY) + 16
	playerRoomX = math.floor(playerX/8)+1
	playerRoomY = math.floor(playerY/7.5)-7
	MapPlayerX = math.floor((playerX%512)/16)+1
	MapPlayerY = math.floor((playerY-32)/16)+1
end

function set_map_data()
	for i = 1, 2 * TileDataTotal do
		if memory.readbyte(0x500 + i-1) ~= 0 then
			tileMap[i] = 1
		else
			tileMap[i] = 0
		end
	end
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

ACTIVE = true

while (running) do

    set_player_data()
    set_map_data()
    --set_view_data()

    print(playerX)

    state = get_state()
    send_state(state)

    controls = receive_input()
    joypad.write(1, controls)
    draw_controls(controls)

    emu:frameadvance()
end