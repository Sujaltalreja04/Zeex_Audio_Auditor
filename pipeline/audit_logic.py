import re
from thefuzz import fuzz

def normalize_education(edu):
    if not edu: return ""
    edu = str(edu).lower()
    if any(x in edu for x in ["10", "tenth"]): return "10th"
    if any(x in edu for x in ["12", "twelfth"]): return "12th"
    if any(x in edu for x in ["grad", "bachelor", "degree", "b.tech"]): return "graduate"
    if any(x in edu for x in ["master", "pg", "post"]): return "masters"
    if "diploma" in edu: return "diploma"
    return edu

def professions_match(written, spoken):
    if not written or not spoken: return False
    w, s = str(written).lower(), str(spoken).lower()
    if "business" in w and "business" in s: return True
    return fuzz.partial_ratio(w, s) > 80

def match_word(word, target):
    if not target or not word: return False
    w, t = str(word).lower(), str(target).lower()
    return fuzz.ratio(w, t) > 85 or (len(t) > 3 and fuzz.partial_ratio(w, t) > 90)

def extract_and_verify(form_data, words_data, transcript):
    results = {
        "Name": {"status": "Missing", "timestamp": None, "spoken": None},
        "Age": {"status": "Missing", "timestamp": None, "spoken": None},
        "Profession": {"status": "Missing", "timestamp": None, "spoken": None},
        "Education": {"status": "Missing", "timestamp": None, "spoken": None},
        "District": {"status": "Missing", "timestamp": None, "spoken": None},
    }

    transcript_lower = transcript.lower()
    
    written_name = str(form_data.get("Name", "")).lower()
    written_age = str(form_data.get("Age", "")).lower()
    written_prof = str(form_data.get("Profession", "")).lower()
    written_edu = str(form_data.get("Education", "")).lower()
    written_dist = str(form_data.get("District", "")).lower()

    norm_written_edu = normalize_education(written_edu)

    for w_data in words_data:
        word = w_data["word"].lower().strip(".,!?\"'")
        t = w_data["start"]

        # 1. Name
        if results["Name"]["status"] == "Missing" and written_name:
            if any(match_word(word, p) for p in written_name.split() if len(p) > 2):
                results["Name"] = {"status": "Match", "timestamp": t, "spoken": word}
        
        # 2. Age
        if results["Age"]["status"] == "Missing" and written_age:
            if word == written_age:
                results["Age"] = {"status": "Match", "timestamp": t, "spoken": word}
            elif word.isdigit() and len(word) <= 3: # just naive
                pass
        
        # 3. Profession
        if results["Profession"]["status"] == "Missing" and written_prof:
            if professions_match(written_prof, word):
                results["Profession"] = {"status": "Match", "timestamp": t, "spoken": word}
            elif word in ["student", "business", "farming", "engineer", "job", "unemployed"]:
                results["Profession"] = {"status": "Mismatch", "timestamp": t, "spoken": word}

        # 4. Education
        if results["Education"]["status"] == "Missing" and written_edu:
            norm_w = normalize_education(word)
            if (norm_written_edu and norm_written_edu in norm_w) or match_word(word, written_edu):
                results["Education"] = {"status": "Match", "timestamp": t, "spoken": word}
            elif any(x in word for x in ["10th", "12th", "graduate", "masters", "diploma"]):
                results["Education"] = {"status": "Mismatch", "timestamp": t, "spoken": word}

        # 5. District
        if results["District"]["status"] == "Missing" and written_dist:
            if match_word(word, written_dist):
                results["District"] = {"status": "Match", "timestamp": t, "spoken": word}

    # Final pass with Regex for Age
    if results["Age"]["status"] == "Missing" and written_age:
        age_patterns = [
            r"i am (\d+) years? old",
            r"my age is (\d+)",
            r"(\d+) years of age",
            r"(?:i'm|i am) (\d+)"
        ]
        for pattern in age_patterns:
            match = re.search(pattern, transcript_lower)
            if match:
                spoken_age = match.group(1)
                status = "Match" if spoken_age == written_age else "Mismatch"
                approx_t = None
                for w in words_data:
                    if spoken_age in w["word"]: approx_t = w["start"]; break
                results["Age"] = {"status": status, "timestamp": approx_t, "spoken": spoken_age}
                break

    all_match = True
    any_mismatch = False
    
    for k, v in results.items():
        if not form_data.get(k): continue
        if v["status"] == "Mismatch": any_mismatch = True
        if v["status"] != "Match": all_match = False
        
    if any_mismatch: final_verdict = "Mismatch"
    elif all_match: final_verdict = "Match"
    else: final_verdict = "Missing Data"

    return {
        "verdict": final_verdict,
        "details": results
    }
