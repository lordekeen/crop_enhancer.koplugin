local ROOT = os.getenv("KO_ROOT") or error("set KO_ROOT to a koreader checkout")
local PLUGIN = os.getenv("PLUGIN_DIR") or error("set PLUGIN_DIR to this plugin directory")
local HARNESS = os.getenv("HARNESS_DIR") or "."
package.path = ROOT.."/base/?.lua;"..ROOT.."/frontend/?.lua;"..PLUGIN.."/?.lua;./common/?.lua;./?.lua;"..package.path
package.cpath = "./libs/?.so;"..package.cpath
local ffi = require("ffi")
ffi.libc = "gnu"
require("ffi/loadlib")
local C = ffi.C
local KOPTContext = require("ffi/koptcontext")
local k2pdfopt = KOPTContext.k2pdfopt

G_reader_settings = {
  readSetting = function(_, _, default) return default end,
  saveSetting = function() end,
}
G_defaults = G_reader_settings

local now_ms = require("crop_enhancer_logger").now_ms

local fixed = require("crop_enhancer_detect")
local upstream = dofile(HARNESS.."/upstream_detect.lua")
local invertfix = dofile(HARNESS.."/invertfix_detect.lua")

local function readGray(path)
  local f = assert(io.open(path, "rb"))
  local hdr = f:read(8)
  local b1, b2, b3, b4, b5, b6, b7, b8 = hdr:byte(1, 8)
  local w = b1 + b2 * 256 + b3 * 65536 + b4 * 16777216
  local h = b5 + b6 * 256 + b7 * 65536 + b8 * 16777216
  local data = assert(f:read(w * h))
  f:close()
  return data, w, h
end

local function newCtx(data, w, h)
  local kc = KOPTContext.new()
  kc.dev_dpi, kc.dev_width, kc.dev_height = 300, 1072, 1448
  kc.quality, kc.contrast, kc.margin = 1.0, 1.0, 0.10
  kc.trim, kc.straighten, kc.writing_direction = 1, 0, 0
  kc.zoom = 1.0
  kc.page_width, kc.page_height = w, h
  kc.bbox.x0, kc.bbox.y0, kc.bbox.x1, kc.bbox.y1 = 0, 0, w, h
  k2pdfopt.bmp_init(kc.src)
  kc.src.width, kc.src.height, kc.src.bpp = w, h, 8
  local buf = ffi.cast("unsigned char*", C.malloc(w * h))
  ffi.copy(buf, data, w * h)
  kc.src.data = buf
  kc.src.size_allocated = w * h
  for i = 0, 255 do
    kc.src.red[i], kc.src.green[i], kc.src.blue[i] = i, i, i
  end
  return kc
end

local function emit(page, algo, ms, x0, y0, x1, y1)
  if not x0 then
    print(string.format("%s|%s|nil|%.1f", page, algo, ms))
  else
    print(string.format("%s|%s|%d|%d|%d|%d|%.1f", page, algo,
      math.floor(x0 + 0.5), math.floor(y0 + 0.5),
      math.floor(x1 + 0.5), math.floor(y1 + 0.5), ms))
  end
end

for name in arg[1]:gmatch("[^,]+") do
  local data, w, h = readGray(HARNESS.."/raw/"..name..".gray")

  local kc = newCtx(data, w, h)
  local t0 = now_ms()
  k2pdfopt.k2pdfopt_crop_bmp(kc)
  local t1 = now_ms()
  local bb = kc.bbox
  emit(name, "stock", t1 - t0, bb.x0, bb.y0, bb.x1, bb.y1)
  kc:free()

  for _, variant in ipairs({ { "upstream", upstream }, { "invertfix", invertfix }, { "patched", fixed } }) do
    local kc2 = newCtx(data, w, h)
    local t2 = now_ms()
    local x0, y0, x1, y1 = variant[2].enhancedCropBmp(kc2)
    local t3 = now_ms()
    emit(name, variant[1], t3 - t2, x0, y0, x1, y1)
    kc2:free()
  end
end
