def parse_msp(filepath):#Parsing func to dictionaries
    spectra = []
    current = {}
    peaks = []
    reading_peaks = False

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            if not line:
                if current:
                    if "precursor_mz" in current:
                        current["peaks"] = peaks
                        spectra.append(current)
                current = {}
                peaks = []
                reading_peaks = False
                continue

            if ':' in line and not reading_peaks:
                key, _, value = line.partition(':')
                key = key.strip().lower()
                value = value.strip()

                if key == "precursormz":
                    current["precursor_mz"] = float(value)
                else:
                    current[key] = value

                if key == "num peaks":
                    reading_peaks = True
                    peaks = []
            else:
                parts = line.split()
                if len(parts) >= 2:
                    mz, intensity = float(parts[0]), float(parts[1])
                    peaks.append((mz, intensity))

    if current and "precursor_mz" in current:
        current["peaks"] = peaks
        spectra.append(current)

    return spectra
from ms_entropy import FlashEntropySearch

# --- MAIN ---
if __name__ == "__main__":
    neg_spectra = parse_msp("lipidblast_positive.msp")
    print(f"Parsed {len(neg_spectra)} spectra.")

    # Build the search index (once)
    entropy_search = FlashEntropySearch()
    spectral_library_new = entropy_search.build_index(neg_spectra)
    print(f"Index built. Re-sorted library has {len(spectral_library_new)} entries.")

    # search the first 5 real spectra against the whole library- each compared with th eentire library- should return 1 first as it 
    # would be comapred to itself; in each iteration the " lookalikes"- as in the ones which result in more than 0.7 would be taken into account
    for i in range(10000):
        query = spectral_library_new[i]
        result = entropy_search.search(
            precursor_mz=query["precursor_mz"],
            peaks=query["peaks"]
        )

        open_scores = result["open_search"]

        print(f"\nQuery #{i}: {query.get('name', 'unknown')}")
        #print(f"  Score against itself (should be ~1.0): {open_scores[i]:.4f}")

        # look for other spectra with a suspiciously high score- wconsidering high score is above 0.7 on a scale on 0-1
        for j, score in enumerate(open_scores):
            if (j != i) and (score >= 0.7 and score!=
                             1.0):# lowkey due to duplicates added restriction
                print(f"  Possible lookalike: {spectral_library_new[j].get('name')} "
                      f"(score={score:.4f})")
