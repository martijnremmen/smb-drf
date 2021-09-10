local socket = require("socket")

host = "localhost"
port = 6969

local c = socket.try(socket.connect(host, port))
local try = socket.newtry(function() c:close() end)

-- try(c:send(gui:gdscreenshot(true)))
-- local r = try(c:receive())
-- print(r)

running = true

local function send_state()
    -- local score = {}
    score = memory.readbyterange(0x07DE, 6)
    print(score)

    try(c:send(score))
end

local function receive_input()
    local response = try(c:receive(6))
    if response == nil then return nil end;
    local lookup_table = { ['1']=true, ['0']=false }

    local l,r,u,d,a,b = response:match('(%d)(%d)(%d)(%d)(%d)(%d)')
    -- print(lookup_table[l])

    local controls = {}
    controls["left"] = lookup_table[l]
    controls["right"] = lookup_table[r]
    controls["up"] = lookup_table[u]
    controls["down"] = lookup_table[d]
    controls["A"] = lookup_table[a]
    controls["B"] = lookup_table[b]
    joypad.write(1, controls)
    print(controls)
    -- controls["up"] = r
end

while (running) do
    send_state()
    receive_input()
    emu:frameadvance()
end