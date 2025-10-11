"""
Test why CTOV2103.AZ from inventory doesn't match with KONTAKT
"""
from utils.model_extractor import ModelExtractor

# Test cases
test_cases = [
    # From inventory
    ("Toaster DeLonghi CTOV2103.AZ", "INVENTORY"),
    ("Delonghi toaster  CTOV2103.AZ", "INVENTORY_2"),
    ("Delonghi toaster CTOV2103.GR", "INVENTORY_3"),
    
    # From DIM_KAVA
    ("DeLonghi CTOV2103.AZ", "DIM_KAVA"),
    ("DeLonghi CTOV2103.GR", "DIM_KAVA_2"),
    
    # From ALTA
    ("Delonghi CTOV2103.GR", "ALTA"),
    
    # From KONTAKT (if exists)
    ("Toaster DeLonghi CTOV2103.AZ", "KONTAKT_TEST"),
]

print("="*80)
print("MODEL EXTRACTION TEST")
print("="*80)

results = []
for name, source in test_cases:
    model = ModelExtractor.extract_model(name)
    normalized = ModelExtractor.normalize_for_matching(model) if model else None
    results.append((source, name, model, normalized))
    print(f"\n[{source}]")
    print(f"  Input:      {name}")
    print(f"  Model:      {model}")
    print(f"  Normalized: {normalized}")

print("\n" + "="*80)
print("MATCHING TEST")
print("="*80)

# Test matching between different sources
print("\nComparing inventory models:")
for i, (source1, name1, model1, norm1) in enumerate(results):
    if 'INVENTORY' not in source1:
        continue
    print(f"\n[{source1}] {model1} ({norm1})")
    for j, (source2, name2, model2, norm2) in enumerate(results):
        if i == j or 'INVENTORY' in source2:
            continue
        matches = ModelExtractor.match_models(model1, model2, strict=True)
        fuzzy = ModelExtractor.match_models(model1, model2, strict=False)
        status = "[MATCH]" if matches else ("[FUZZY]" if fuzzy else "[NO MATCH]")
        print(f"  vs [{source2}] {model2} ({norm2}): {status}")

print("\n" + "="*80)
print("PROBLEM ANALYSIS")
print("="*80)

# Analyze the specific problem
inv_model = "CTOV2103.AZ"
kontakt_model = "CTOV2103.AZ"  # Assuming KONTAKT has this

print(f"\nInventory:  {inv_model}")
print(f"KONTAKT:    {kontakt_model}")
print(f"\nNormalized:")
print(f"  Inventory:  {ModelExtractor.normalize_for_matching(inv_model)}")
print(f"  KONTAKT:    {ModelExtractor.normalize_for_matching(kontakt_model)}")
print(f"\nMatch result:")
print(f"  Strict:  {ModelExtractor.match_models(inv_model, kontakt_model, strict=True)}")
print(f"  Fuzzy:   {ModelExtractor.match_models(inv_model, kontakt_model, strict=False)}")

print("\n" + "="*80)

