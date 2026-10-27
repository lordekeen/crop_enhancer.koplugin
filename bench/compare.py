from PIL import Image, ImageDraw
import os, sys, collections

RESULTS = sys.argv[1] if len(sys.argv) > 1 else "results.txt"
PAGES = sys.argv[2] if len(sys.argv) > 2 else "pages"

res = collections.defaultdict(dict)
for line in open(RESULTS):
    p = line.strip().split("|")
    if len(p) < 3: continue
    page, algo = p[0], p[1]
    if p[2] == "nil":
        res[page][algo] = None
    else:
        x0,y0,x1,y1 = map(int,p[2:6]); ms=float(p[6])
        res[page][algo] = (x0,y0,x1,y1,ms)

ALGOS = ["stock","upstream","patched"]
def ink_bbox(im, thr=200):
    # bbox of pixels darker than thr
    mask = im.point(lambda v: 255 if v < thr else 0)
    return mask.getbbox()  # (l,t,r,b) exclusive
def metrics(im, box):
    W,H = im.size
    if box is None: return None
    x0,y0,x1,y1,ms = box
    x0=max(0,x0); y0=max(0,y0); x1=min(W,x1); y1=min(H,y1)
    if x1<=x0 or y1<=y0: return None
    ink = im.point(lambda v: 255 if v < 200 else 0)
    total_ink = sum(1 for v in ink.get_flattened_data() if v)
    crop = im.crop((x0,y0,x1,y1))
    cink = crop.point(lambda v: 255 if v < 200 else 0)
    ink_in = sum(1 for v in cink.get_flattened_data() if v)
    area = (x1-x0)*(y1-y0)
    return dict(box=(x0,y0,x1,y1), ms=ms,
                cut_frac=(total_ink-ink_in)/max(1,total_ink),
                kept_area=area/(W*H),
                ink_density=ink_in/max(1,area),
                iou=None)

def iou(a,b):
    if not a or not b: return 0.0
    ax0,ay0,ax1,ay1=a; bx0,by0,bx1,by1=b
    ix0=max(ax0,bx0); iy0=max(ay0,by0); ix1=min(ax1,bx1); iy1=min(ay1,by1)
    if ix1<=ix0 or iy1<=iy0: return 0.0
    inter=(ix1-ix0)*(iy1-iy0)
    ua=(ax1-ax0)*(ay1-ay0)+(bx1-bx0)*(by1-by0)-inter
    return inter/ua

print(f"{'page':14} {'algo':9} {'bbox':28} {'area%':>6} {'cut ink%':>9} {'ink/area':>9} {'IoU':>6} {'ms':>6}")
for page in res:
    im = Image.open(os.path.join(PAGES, page + ".png")).convert("L")
    truth = ink_bbox(im)
    for algo in ALGOS:
        box = res[page].get(algo)
        m = metrics(im, box)
        if not m:
            print(f"{page:14} {algo:9} {'nil':28}"); continue
        x0,y0,x1,y1 = m["box"]
        print(f"{page:14} {algo:9} {f'({x0},{y0})-({x1},{y1})':28} {m['kept_area']*100:6.1f} {m['cut_frac']*100:9.2f} {m['ink_density']:9.3f} {iou(m['box'],truth):6.3f} {m['ms']:6.1f}")
    print()

# visual sheet
TH=360
rows=[]
for page in res:
    im = Image.open(os.path.join(PAGES, page + ".png")).convert("RGB")
    W,H = im.size
    tiles=[]
    # tile 1: page with boxes
    t = im.copy(); d=ImageDraw.Draw(t)
    colors={"stock":(230,40,40),"upstream":(40,90,230),"patched":(20,160,60)}
    for algo in ALGOS:
        b=res[page].get(algo)
        if b:
            d.rectangle([b[0],b[1],b[2]-1,b[3]-1],outline=colors[algo],width=max(2,W//300))
    tiles.append(t)
    for algo in ALGOS:
        b=res[page].get(algo)
        tiles.append(im.crop((max(0,b[0]),max(0,b[1]),min(W,b[2]),min(H,b[3]))) if b else Image.new("RGB",(W,H),(255,0,255)))
    # scale each tile to height TH
    scaled=[t.resize((max(1,int(t.width*TH/t.height)),TH)) for t in tiles]
    rows.append((page, scaled))
cw=max(sum(t.width for t in row)+10*len(row) for _,row in rows)
sheet=Image.new("RGB",(cw, len(rows)*(TH+24)),(255,255,255))
d=ImageDraw.Draw(sheet)
y=0
for page,row in rows:
    d.text((2,y+4), page+"   [orig+boxes | stock(red) | upstream(blue) | patched(green)]", fill=0)
    y+=20
    x=0
    for t in row:
        sheet.paste(t,(x,y)); x+=t.width+10
    y+=TH+4
sheet.save("compare.png")
print("saved compare.png", sheet.size)
