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
#import time
#import json

#start_time = time.time()
#results = {}
#n = 10000  # test on first 10,000 spectra

#or i in range(n):
 #   query = spectral_library_new[i]
  #  result = entropy_search.search(
   #     precursor_mz=query["precursor_mz"],
    #    peaks=query["peaks"]
    #)
    #open_scores = result["open_search"]

  #  query_id = query.get('inchikey', query.get('id'))
   # alternatives = []
    #for j, score in enumerate(open_scores):
     #   other_id = spectral_library_new[j].get('inchikey', spectral_library_new[j].get('id'))
      #  if j != i and other_id != query_id and score >= 0.7:
       #     alternatives.append({'name': spectral_library_new[j].get('name'), 'score': float(score)})

    #if alternatives:
     #   results[query.get('name', str(i))] = alternatives

   # if i % 1000 == 0:
    #    elapsed = time.time() - start_time
     #   print(f"Processed {i} / {n}  |  elapsed: {elapsed:.1f}s")

#elapsed_total = time.time() - start_time
#print(f"\nDone. Processed {n} spectra in {elapsed_total:.1f} seconds.")
#print(f"That's {elapsed_total / n * 793757 / 60:.1f} minutes estimated for the FULL library.")

# Save results
#with open("lookalikes_negative_test10000.json", "w") as f:
#    json.dump(results, f, indent=2)

#print(f"\nFound alternatives for {len(results)} out of {n} query spectra.")
#print("Saved to lookalikes_negative_test10000.json")

#---- Please ignore ----
#neg_spectra = parse_msp("lipidblast_negative.msp")
#entropy_search = FlashEntropySearch()
#print(type(neg_spectra))
#print(type(neg_spectra[0]))
#print(neg_spectra[0])
#spectral_library_new = entropy_search.build_index(neg_spectra)
# Step 2: Search the library
#entropy_similarity = entropy_search.search(
 #   precursor_mz=150.0, peaks=[[100.0, 1.0], [101.0, 1.0], [102.0, 1.0]])

# --- MAIN ---
if __name__ == "__main__":
    neg_spectra = parse_msp("lipidblast_negative.msp")
    print(f"Parsed {len(neg_spectra)} spectra.")

    # Step 2: Build the search index (once)
    entropy_search = FlashEntropySearch()
    spectral_library_new = entropy_search.build_index(neg_spectra)
    print(f"Index built. Re-sorted library has {len(spectral_library_new)} entries.")

    # Step 3: TEST — search the first 5 real spectra against the whole library- each compared with th eentire library- should return 1 first as it 
    # would be comapred to itself; in each iteration the " lookalikes"- as in the ones which result in more than 0.7 would be taken into account
    for i in range(len(neg_spectra)):
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
