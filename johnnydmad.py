import traceback
import re
from zipfile import ZipFile
from collections import Counter
from operator import itemgetter

# This construction is required for devtool functionality. Do not remove.
try:
    from .musicrandomizer import *
    from .jukebox import add_music_player
    from .mfvitools.insertmfvi import byte_insert, int_insert
    from .mfvitools.mml2mfvi import mml_to_akao
except ImportError:
    from musicrandomizer import *
    from jukebox import add_music_player
    from mfvitools.insertmfvi import byte_insert, int_insert
    from mfvitools.mml2mfvi import mml_to_akao


def print_progress_bar(cur, max):
    pct = (cur / max) * 100
    cursor = " >)|(<-"
    full_boxes = int(pct // 2)
    cursor_idx = int((pct % 2) * (len(cursor)/2))
    boxtext = cursor[-1] * full_boxes + cursor[cursor_idx]
    print(f"\r[{boxtext:<50}] {cur}/{max}", end="", flush=True)


async def johnnydmad(c, filename):
    # This is the original function for your bot. It is untouched.
    try:
        with open("WorldsCollide/seeds/" + filename + ".smc", "rb") as f:
            inrom = f.read()
    except IOError:
        while True:
            fn = input()
            try:
                with open(fn, "rb") as f:
                    inrom = f.read()
            except:
                continue
            break
        
    if c == "chaos":
        f_chaos = True
    else:
        f_chaos = False
    f_dupes = False
    kw = {}
    force_dm = None
    metadata = {}
    if c == "silent":
        kw["playlist_filename"] = "silence.txt"
        f_dupes = True
    outrom = process_music(inrom, meta=metadata, f_chaos=f_chaos, f_dupes=f_dupes, **kw)
    outrom = process_formation_music_by_table(outrom)
    outrom = process_map_music(outrom)

    with open("WorldsCollide/seeds/"+filename+".smc", "wb") as f:
        f.write(outrom)

    sp = get_music_spoiler()
    # --- FIX: Added encoding='utf-8' ---
    with open("WorldsCollide/seeds/"+filename+"_spoiler.txt", "w", encoding="utf-8") as f:
        f.write(sp)


# --- NEW FUNCTION FOR THE WEB APP ---
async def johnnydmad_webapp(c, input_smc_path, output_smc_path, spoiler_log_path):
    """
    A new version of the function that accepts full file paths
    to avoid issues with the current working directory.
    """
    try:
        with open(input_smc_path, "rb") as f:
            inrom = f.read()
    except IOError as e:
        print(f"Could not read input file: {input_smc_path}")
        raise e
        
    if c == "chaos":
        f_chaos = True
    else:
        f_chaos = False
    f_dupes = False
    kw = {}
    force_dm = None
    metadata = {}
    if c == "silent":
        kw["playlist_filename"] = "silence.txt"
        f_dupes = True
    outrom = process_music(inrom, meta=metadata, f_chaos=f_chaos, f_dupes=f_dupes, **kw)
    outrom = process_formation_music_by_table(outrom)
    outrom = process_map_music(outrom)

    with open(output_smc_path, "wb") as f:
        f.write(outrom)

    sp = get_music_spoiler()
    # --- FIX: Added encoding='utf-8' ---
    with open(spoiler_log_path, "w", encoding="utf-8") as f:
        f.write(sp)


# --- The rest of your file is unchanged ---
def tierboss_test(test_song, playlist_filename=None, **kwargs):
    _, original_pool = init_playlist(playlist_filename)
    while True:
        mml = None
        pool = set((a for a in original_pool))
        try:
            mml = generate_tierboss_mml(pool, force_include=test_song)
        except Exception:
            traceback.print_exc()  
        if mml:
            with open("tierboss.mml", "w") as f:
                f.write(mml)
            print("wrote tierboss.mml", end=" ")
        else:
            print(f"failed to generate with \"{test_song}\"", end=" ")
        print("(press enter to reroll; or type a new filename; or type q to quit)")
        i = input()
        if i.lower() == "q":
            break
        elif i:
            test_song = i.strip()
    
def pool_test(inrom, battle_only=False, playlist_filename=None, **kwargs):
    results = {}
    results_by_song = {}
    iterations = 10000
    
    print()
    for i in range(iterations):
        tracklist = process_music(inrom, pool_test=True, playlist_filename=playlist_filename)
        for track, song in tracklist.items():
            if track not in results:
                results[track] = []
            results[track].append(song)
            if not battle_only:
                vsong = song
                if track == "train":
                    if len(song) > 3:
                        if song[-3:] == ":tr":
                            vsong = song[:-3]
                elif track in ["assault", "zozo", "ruin"]:
                    if len(song) > 4:
                        if song[-4:] == ":sfx":
                            vsong = song[:-4]
                elif track in ["tier1", "tier2", "tier3"]:
                    vsong += " (DM)"
                if vsong not in results_by_song:
                    results_by_song[vsong] = {}
                if track not in results_by_song[vsong]:
                    results_by_song[vsong][track] = 0
                results_by_song[vsong][track] += 1
        print_progress_bar(i, iterations)
    print()
    
    if battle_only:
        tracks_to_check = ["battle", "bat2", "bat3", "bat4", "mboss", "boss",
                           "atma", "dmad5", "tier1", "tier2", "tier3"]
    else:
        tracks_to_check = results.keys()
        
    for track in tracks_to_check:
        pool = results[track]
        if len(pool) < iterations:
            pool.extend(["not present"] * (iterations - len(pool)))
            
        print(f"[{track.upper()}]:")
        
        c = Counter(pool)
        rank = sorted(c.items(), key=itemgetter(1), reverse=True)
        songlen = max([len(s) for s in c.keys()])
        for song, reps in rank:
            pct = (reps / iterations) * 100
            print(f"    {pct:04.1f}% {song:<{songlen}} ({reps} / {iterations})")
            
    if not battle_only:
        print("\n * * * * * * * * * *\n")
        song_order = sorted(results_by_song.items(), key=itemgetter(0))
        for song, songtracks in song_order:
            song_count = 0
            for track, track_count in songtracks.items():
                song_count += track_count
            pct = (song_count / iterations) * 100
            print(f"{song.upper()} appears in {pct:.1f}% of seeds:")
            
            rank = sorted(songtracks.items(), key=itemgetter(1), reverse=True)
            for track, track_count in rank:
                pct = (track_count / iterations) * 100
                share = (track_count / song_count) * 100
                print(f"    {pct:4.1f}% ({share:4.1f}%) as {track}")
            
            
def mass_test(sort, playlist_filename=None, **kwargs):
    global used_song_names
    testbed = [
        ("***", "plain", 0x4C, False),
        ("rain", "zozo", 0x29, True),
        ("wind", "ruin", 0x4F, True),
        ("train", "train", 0x20, False)
        ]
    #cursor = " >)|(<"
    playlist_map, _ = init_playlist(playlist_filename)
    results = []
    legacy_files = set()
    jukebox_titles = {}
    song_warnings = {}
    i = 0
    print("")
    for song in sorted(playlist_map):
        binsizes = {}
        memusage = 0
        debugtext = f"{song}: "
        song_warnings[song] = set()
        for type, trackname, idx, use_sfx in testbed:
            tl = Tracklist()
            tl.add_random(trackname, [song], idx=idx, allow_duplicates=True)
            variant = tl[trackname].variant
            if variant is None:
                variant = "_default_"
                
            mml = tl[trackname].mml
            if tl[trackname].is_legacy:
                legacy_files.add(song)
                iset = mml_to_akao(mml, variant=variant, inst_only=True)
                mml = append_legacy_imports(mml, iset, raw_inst=True)
            mml = apply_variant(mml, type, trackname, variant=variant)
            bin = mml_to_akao(mml, song + ' ' + trackname, sfxmode=use_sfx, variant=variant)[0]
            binsizes[type] = len(bin)
            
            if song not in jukebox_titles:
                jukebox_titles[song] = get_jukebox_title(mml, song)
            var_memusage = get_spc_memory_usage(mml, variant=variant, custompath=os.path.dirname(tl[trackname].file))
            debugtext += f"({var_memusage}) "
            memusage = max(memusage, var_memusage)
            
            if memusage > 3746:
                song_warnings[song].add("BRR memory overflow")
            if len(bin) > 0x1002:
                song_warnings[song].add("Sequence memory overflow")
            if "%f0" not in mml:
                if re.search("%[Ff][0-9]", mml) is None:
                    song_warnings[song].add("Echo FIR unset (%f)")
            if "%b" not in mml:
                song_warnings[song].add("Echo feedback unset (%b)")
            if "%v" not in mml:
                song_warnings[song].add("Echo volume unset (%v)")
        order = memusage if sort == "mem" else max(binsizes.values())
        results.append((order, song, binsizes, memusage))
        print_progress_bar(i, len(playlist_map))
        i += 1
        
    results = sorted(results)
    print("")
    for largest, song, binsizes, memusage in results:
        print(f"{song:<20} :: ", end="")
        for k, v in binsizes.items():
            print(f"[{k} ${v:0X}] ", end="")
        if song in legacy_files:
            print(f" :: ~{jukebox_titles[song]:<18}~", end="")
        else:
            print(f" :: <{jukebox_titles[song]:<18}>", end="")
        print(f" ({memusage})", end="")
        #if largest >= 0x1002 or memusage > 3746 or song in song_warnings:
        if song_warnings[song]:
            print(" ~~WARNING~~")
            for w in song_warnings[song]:
                print("    " + w)
        else:
            print("")