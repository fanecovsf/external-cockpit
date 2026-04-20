from pathlib import Path
import struct
import zlib
import nbtlib
import io

def read_chunk_from_region(file_path, cx, cz):
    with open(file_path, "rb") as f:
        # header (8KB)
        f.seek(0)
        header = f.read(4096)

        index = cx + cz * 32
        offset_bytes = header[index * 4:index * 4 + 4]

        if offset_bytes == b"\x00\x00\x00\x00":
            return None

        offset = struct.unpack(">I", offset_bytes)[0]
        offset >>= 8  # chunk offset em setores de 4KB

        f.seek(offset * 4096)
        length = struct.unpack(">I", f.read(4))[0]

        compression_type = f.read(1)
        data = f.read(length - 1)

        # 2 = zlib (Minecraft padrão moderno)
        if compression_type == b"\x02":
            decompressed = zlib.decompress(data)
        else:
            return None

        return nbtlib.File.parse(io.BytesIO(decompressed))
    
def get_top_block_from_nbt(nbt):
    try:
        level = nbt

        sections = level.get("sections") or level.get("Sections")
        if not sections:
            return "minecraft:air"

        # de cima pra baixo
        for section in reversed(sections):
            block_states = section.get("block_states")
            if not block_states:
                continue

            palette = block_states.get("palette")
            if not palette:
                continue

            for block in palette:
                name = block.get("Name")
                if name and name != "minecraft:air":
                    return str(name)

        return "minecraft:air"

    except Exception as e:
        print("NBT parse error:", e)
        return "minecraft:air"

def get_chunks_from_mca(file_path):
    chunks = []

    with open(file_path, "rb") as f:
        # region file header = 8KB
        header = f.read(4096)

        for i in range(1024):
            offset = header[i * 4:(i * 4) + 4]

            # chunk existe se offset != 0
            if offset == b"\x00\x00\x00\x00":
                continue

            cx = i % 32
            cz = i // 32

            chunks.append((cx, cz))

    return chunks


def classify_block(block_id: str):
    if not block_id:
        return "unknown"

    if "water" in block_id:
        return "water"

    if "lava" in block_id:
        return "lava"

    if "sand" in block_id:
        return "sand"

    if "stone" in block_id or "deepslate" in block_id:
        return "rock"

    if "grass" in block_id or "dirt" in block_id:
        return "land"

    if "snow" in block_id:
        return "snow"

    return "other"


def get_top_block(chunk):
    # scan simples do topo (rápido e suficiente pra mapa)
    for y in range(319, -64, -1):
        try:
            block = chunk.get_block(0, y, 0)
            if block and block.id != "minecraft:air":
                return block.id
        except:
            continue
    return "minecraft:air"

def parse_world(world_path: str):
    world_path = Path(world_path)
    regions_path = world_path / "region"

    chunks = []

    for region_file in regions_path.glob("*.mca"):
        name = region_file.stem
        _, rx, rz = name.split(".")
        rx, rz = int(rx), int(rz)

        for cx, cz in get_chunks_from_mca(region_file):

            nbt = read_chunk_from_region(region_file, cx, cz)
            if not nbt:
                continue

            top_block = get_top_block_from_nbt(nbt)
            chunk_type = classify_block(top_block)

            chunks.append({
                "chunkX": rx * 32 + cx,
                "chunkZ": rz * 32 + cz,
                "topBlock": top_block,
                "type": chunk_type
            })

    return chunks