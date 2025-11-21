"""
Reconcile inventory products with Dim Kava scraped products.
Generates an Excel report with:
- matches: confidently matched items (by model)
- unmatched_inventory: inventory items without a Dim Kava match
- unmatched_dimkava: Dim Kava items without an inventory match
- suggestions: fuzzy suggestions for unmatched items
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import sys
import re

# Ensure project root is on sys.path to import utils
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.model_extractor import ModelExtractor


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INBOX_DIR = DATA_DIR / "inbox"
OUTPUT_DIR = DATA_DIR / "output"


def load_inventory() -> pd.DataFrame:
    """Replicate inventory parsing from build_price_comparison for consistency."""
    file_path = INBOX_DIR / "остатки.xls"
    if not file_path.exists():
        print(f"[ERROR] Inventory file not found: {file_path}")
        return pd.DataFrame()

    df = pd.read_excel(file_path, header=None)
    products: List[Dict] = []
    for i in range(len(df)):
        row = df.iloc[i]
        row_values = [v for v in row.values if pd.notna(v)]
        if len(row_values) < 4:
            continue

        row_str = ' '.join([str(v) for v in row_values])
        text_lc = row_str.lower()
        if ('delonghi' not in text_lc and 'melitta' not in text_lc and 'nivona' not in text_lc):
            continue

        try:
            name = None
            qty = None
            price = None
            if len(row_values) == 5:
                name, qty, price = str(row_values[1]), row_values[2], row_values[3]
            elif len(row_values) == 6:
                name, qty, price = str(row_values[1]), row_values[3], row_values[4]
            elif len(row_values) == 7:
                name, qty, price = str(row_values[1]), row_values[4], row_values[5]

            if name and (('delonghi' in name.lower()) or ('melitta' in name.lower()) or ('nivona' in name.lower())):
                if isinstance(qty, (int, float)) and isinstance(price, (int, float)):
                    if qty > 0 and price > 0:
                        model = ModelExtractor.extract_model(name)
                        model_norm = ModelExtractor.normalize_for_matching(model) if model else ""
                        products.append({
                            'name': name,
                            'quantity': int(qty),
                            'price': float(price),
                            'model': model,
                            'model_norm': model_norm,
                        })
        except Exception:
            pass

    return pd.DataFrame(products)


def find_latest_dimkava_file() -> Optional[Path]:
    candidates = sorted(OUTPUT_DIR.glob("dimkava_*prices_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def load_dimkava(latest_file: Path) -> pd.DataFrame:
    df = pd.read_excel(latest_file)
    # Expect columns: name, regular_price, discount_price, final_price, has_discount, ...
    # Normalize columns to lower-case for safety
    df.columns = [str(c).strip().lower() for c in df.columns]
    rows: List[Dict] = []
    for _, r in df.iterrows():
        name = str(r.get("name", "")).strip()
        if not name:
            continue
        price = r.get("final_price") or r.get("discount_price") or r.get("regular_price")
        try:
            price = float(price) if pd.notna(price) else None
        except Exception:
            price = None

        model = ModelExtractor.extract_model(name)
        model_norm = ModelExtractor.normalize_for_matching(model) if model else ""
        rows.append({
            "name": name,
            "price": price,
            "model": model,
            "model_norm": model_norm,
        })
    return pd.DataFrame(rows)


def match_by_model(inv_df: pd.DataFrame, dk_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Exact normalized model match first
    dk_by_model: Dict[str, List[Dict]] = {}
    for _, r in dk_df.iterrows():
        key = r["model_norm"]
        if not key:
            continue
        dk_by_model.setdefault(key, []).append(r)

    matches: List[Dict] = []
    unmatched_inv_idx: List[int] = []

    for idx, r in inv_df.iterrows():
        key = r["model_norm"]
        if key and key in dk_by_model:
            # pick first dk item for now
            dk = dk_by_model[key][0]
            matches.append({
                "inventory_name": r["name"],
                "inventory_model": r["model"],
                "inventory_price": r["price"],
                "inventory_qty": r["quantity"],
                "dimkava_name": dk["name"],
                "dimkava_model": dk["model"],
                "dimkava_price": dk["price"],
            })
        else:
            unmatched_inv_idx.append(idx)

    matched_df = pd.DataFrame(matches)
    unmatched_inv = inv_df.loc[unmatched_inv_idx].copy() if unmatched_inv_idx else inv_df.iloc[0:0].copy()

    # Unmatched DimKava: those not used in matches by key
    used_keys = set(m["dimkava_model"] for m in matches if m.get("dimkava_model"))
    unmatched_dk = dk_df[~dk_df["model"].isin(list(used_keys))].copy()
    return matched_df, unmatched_inv, unmatched_dk


def make_suggestions(unmatched_inv: pd.DataFrame, unmatched_dk: pd.DataFrame) -> pd.DataFrame:
    # Heuristic base-model matching (ignore last letters like color)
    suggestions: List[Dict] = []
    if unmatched_inv.empty or unmatched_dk.empty:
        return pd.DataFrame(columns=["inventory_name", "inventory_model", "candidate_model", "candidate_name", "reason"]) 

    # Precompute base model for dk
    dk_base_map: Dict[str, List[Tuple[str, str]]] = {}
    for _, r in unmatched_dk.iterrows():
        m = r.get("model") or ""
        base = pd.Series([m]).str.replace(r"[A-Z]{1,2}$", "", regex=True).iloc[0]
        if base:
            dk_base_map.setdefault(base, []).append((str(r.get("model")), str(r.get("name"))))

    for _, r in unmatched_inv.iterrows():
        inv_m = r.get("model") or ""
        base = pd.Series([inv_m]).str.replace(r"[A-Z]{1,2}$", "", regex=True).iloc[0]
        if base and base in dk_base_map:
            for cand_m, cand_name in dk_base_map[base]:
                suggestions.append({
                    "inventory_name": r.get("name"),
                    "inventory_model": inv_m,
                    "candidate_model": cand_m,
                    "candidate_name": cand_name,
                    "reason": "Base model match (color variant)"
                })

    # Additionally, try containment of normalized forms (one inside another)
    dk_norm_set = [(str(r.get("model_norm")), str(r.get("model")), str(r.get("name"))) for _, r in unmatched_dk.iterrows() if r.get("model_norm")]
    for _, r in unmatched_inv.iterrows():
        inv_norm = str(r.get("model_norm"))
        if not inv_norm:
            continue
        for dk_norm, dk_model, dk_name in dk_norm_set:
            if (inv_norm and dk_norm) and (inv_norm in dk_norm or dk_norm in inv_norm) and inv_norm != dk_norm:
                suggestions.append({
                    "inventory_name": r.get("name"),
                    "inventory_model": r.get("model"),
                    "candidate_model": dk_model,
                    "candidate_name": dk_name,
                    "reason": "Contained normalized model"
                })

    # Melitta keyword-based suggestion (order-insensitive): Barista T Smart SST ~= Barista Smart TS SST
    def tokenize(title: str) -> List[str]:
        if not title:
            return []
        title_up = str(title).upper()
        # keep alnum and spaces
        title_up = re.sub(r"[^A-Z0-9\s]", " ", title_up)
        tokens = [t for t in title_up.split() if t not in {"MELITTA", "DELONGHI", "NIVONA", "COFFEE", "MACHINE"}]
        return tokens

    for _, r in unmatched_inv.iterrows():
        inv_name = r.get("name")
        inv_tokens = set(tokenize(inv_name))
        if not inv_tokens:
            continue
        # Trigger only for Melitta to reduce noise
        if "MELITTA" not in str(inv_name).upper():
            continue
        for _, dk in unmatched_dk.iterrows():
            dk_name = dk.get("name")
            if "MELITTA" not in str(dk_name).upper():
                continue
            dk_tokens = set(tokenize(dk_name))
            if not dk_tokens:
                continue
            overlap = len(inv_tokens & dk_tokens)
            if overlap >= 3:  # strong overlap in descriptors
                suggestions.append({
                    "inventory_name": inv_name,
                    "inventory_model": r.get("model"),
                    "candidate_model": dk.get("model"),
                    "candidate_name": dk_name,
                    "reason": "High keyword overlap (Melitta series)"
                })

    return pd.DataFrame(suggestions)


def save_report(matched: pd.DataFrame, unmatched_inv: pd.DataFrame, unmatched_dk: pd.DataFrame, suggestions: pd.DataFrame) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"reconciliation_dimkava_{ts}.xlsx"
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        matched.to_excel(writer, sheet_name="matches", index=False)
        unmatched_inv.to_excel(writer, sheet_name="unmatched_inventory", index=False)
        unmatched_dk.to_excel(writer, sheet_name="unmatched_dimkava", index=False)
        suggestions.to_excel(writer, sheet_name="suggestions", index=False)
    return out_path


def main():
    inv = load_inventory()
    if inv.empty:
        print("[ERROR] Inventory is empty. Abort.")
        return

    latest = find_latest_dimkava_file()
    if not latest:
        print("[ERROR] No Dim Kava export found in data/output. Run the scraper first.")
        return
    print(f"[INFO] Using Dim Kava file: {latest}")

    dk = load_dimkava(latest)
    matched, unmatched_inv, unmatched_dk = match_by_model(inv, dk)
    suggestions = make_suggestions(unmatched_inv, unmatched_dk)

    report = save_report(matched, unmatched_inv, unmatched_dk, suggestions)
    print("[DONE] Report saved to:", report)
    print(f"[STATS] matches={len(matched)}, unmatched_inventory={len(unmatched_inv)}, unmatched_dimkava={len(unmatched_dk)}, suggestions={len(suggestions)}")


if __name__ == "__main__":
    main()


