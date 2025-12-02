import pandas as pd
import numpy as np
import datetime

# -------------------------------------------------------------------
# Generic helpers
# -------------------------------------------------------------------

def is_blank(x):
    """
    Identifies blank values in the key fields.
    Returns True for blank / NA, False otherwise.
    """
    if pd.isna(x):
        return True
    if isinstance(x, str) and x.strip() == "":
        return True
    if isinstance(x, (np.datetime64, datetime.date)):
        # let pandas decide if this datetime-like is NA
        return pd.isna(x)
    return False


def nonblank_equal(a, b):
    return (not is_blank(a)) and (not is_blank(b)) and a == b


def nonblank_not_equal(a, b):
    return (not is_blank(a)) and (not is_blank(b)) and a != b


# -------------------------------------------------------------------
# DOB helpers
# -------------------------------------------------------------------

def dob_is_strict_match(dob1, dob2, dob_est1, dob_est2):
    """
    DOBs are considered a 'strict match' if:
    - both are non-blank
    - both are equal
    - neither is estimated (dob_est != 'Y')
    """
    if is_blank(dob1) or is_blank(dob2):
        return False
    if dob_est1 == "Y" or dob_est2 == "Y":
        return False
    if dob1 != dob2:
        return False
    return True


def dob_is_strict_not_match(dob1, dob2):
    """
    DOBs are considered a 'strict not match' if:
    - both are non-blank
    - they are not equal
    - NO consideration for estimation
    """
    if is_blank(dob1) or is_blank(dob2):
        return False
    return dob1 != dob2


# -------------------------------------------------------------------
# Strong match rules (0-6)
# -------------------------------------------------------------------

def match_rule(r1, r2):
    """
    Strong match rules 0–6.
    r1, r2 are tuples: (first_name, last_name, dob, ssn, dob_est_flag)
    """
    fn1, ln1, dob1, ssn1, dob_est1 = r1
    fn2, ln2, dob2, ssn2, dob_est2 = r2

    dob_match    = dob_is_strict_match(dob1, dob2, dob_est1, dob_est2)
    dob_ne_match = dob_is_strict_not_match(dob1, dob2)
    dob1_blank   = is_blank(dob1)
    dob2_blank   = is_blank(dob2)

    # Rule 0: FN= LN= DOB= SSN=
    if nonblank_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_match and nonblank_equal(ssn1, ssn2):
        return 0

    # Rule 1: FN= LN= DOB- SSN=
    if nonblank_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_ne_match and nonblank_equal(ssn1, ssn2):
        return 1

    # Rule 2: FN= LN- DOB= SSN=
    if nonblank_equal(fn1, fn2) and nonblank_not_equal(ln1, ln2) \
       and dob_match and nonblank_equal(ssn1, ssn2):
        return 2

    # Rule 3: FN- LN= DOB= SSN=
    if nonblank_not_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_match and nonblank_equal(ssn1, ssn2):
        return 3

    # Rule 4: FN- LN= DOB blank SSN=
    if nonblank_not_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and (dob1_blank or dob2_blank) and nonblank_equal(ssn1, ssn2):
        return 4

    # Rule 5: FN= LN- DOB blank SSN=
    if nonblank_equal(fn1, fn2) and nonblank_not_equal(ln1, ln2) \
       and (dob1_blank or dob2_blank) and nonblank_equal(ssn1, ssn2):
        return 5

    # Rule 6: FN= LN= DOB blank SSN=
    if nonblank_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and (dob1_blank or dob2_blank) and nonblank_equal(ssn1, ssn2):
        return 6

    return None


# -------------------------------------------------------------------
# Likely match rules (7-12)
# -------------------------------------------------------------------

def likely_match_rule(r1, r2):
    """
    Likely match rules 7–12.
    r1, r2 are tuples: (first_name, last_name, dob, ssn, dob_est_flag)
    """
    fn1, ln1, dob1, ssn1, dob_est1 = r1
    fn2, ln2, dob2, ssn2, dob_est2 = r2

    dob1_blank   = is_blank(dob1)
    dob2_blank   = is_blank(dob2)
    dob_match    = dob_is_strict_match(dob1, dob2, dob_est1, dob_est2)
    dob_ne_match = dob_is_strict_not_match(dob1, dob2)

    # 7: FN= LN= DOB- SSN=
    if nonblank_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_ne_match and nonblank_equal(ssn1, ssn2):
        return 7

    # 8: FN= LN- DOB= SSN=
    if nonblank_equal(fn1, fn2) and nonblank_not_equal(ln1, ln2) \
       and dob_match and nonblank_equal(ssn1, ssn2):
        return 8

    # 9: FN- LN= DOB= SSN blank
    if nonblank_not_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_match and (is_blank(ssn1) or is_blank(ssn2)):
        return 9

    # 10: FN= LN- DOB= SSN blank
    if nonblank_equal(fn1, fn2) and nonblank_not_equal(ln1, ln2) \
       and dob_match and (is_blank(ssn1) or is_blank(ssn2)):
        return 10

    # 11: FN= LN= DOB- SSN blank
    if nonblank_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_ne_match and (is_blank(ssn1) or is_blank(ssn2)):
        return 11

    # 12: FN- LN= DOB- SSN=
    if nonblank_not_equal(fn1, fn2) and nonblank_equal(ln1, ln2) \
       and dob_ne_match and nonblank_equal(ssn1, ssn2):
        return 12

    return None


# -------------------------------------------------------------------
# Relationship / address helpers for likely matches
# -------------------------------------------------------------------

allowed_relationships = [
    "Father-Adoptive", "Father-Biological", "Father-Unknown",
    "Mother-Adoptive", "Mother-Biological", "Mother-Unknown",
    "Guardian-Unknown", "Guardian-Legal", "Guardian-Non-Legal",
    "Guardian-Ad Litem", "Guardian-Court Ordered",
    "Sibling-Full", "Sibling-Maternal Half", "Sibling-Paternal Half",
]


def relatives_for_referral(df_rel, referral_id, relationship):
    """
    Return a list of (fn, ln, dob, ssn, dob_est) tuples for relatives
    in df_rel for that referral and relationship.
    """
    rel = df_rel[
        (df_rel["referral_id"] == referral_id) &
        (df_rel["relative_relationship"] == relationship)
    ].copy()

    if rel.empty:
        return []

    return list(
        zip(
            rel["relative_first_name"],
            rel["relative_last_name"],
            rel["relative_date_of_birth"],
            rel["relative_social_security_number"],
            rel["relative_date_of_birth_estimated"],
        )
    )


def primary_address_for_referral(df_add, referral_id):
    """
    Return (address_line_1, city, zip) for the 'Primary' address
    in the address table, or None if not found.
    """
    add = df_add[
        (df_add["Referral ID"] == referral_id) &
        (df_add["Address Type"].str.lower() == "primary")
    ]

    if add.empty:
        return None

    row = add.iloc[0]
    return (
        row.get("Address Line 1"),
        row.get("City"),
        row.get("Zip Code"),
    )


def confirm_likely_match(row1, row2, rule, df_rel, df_add):
    """
    Extra confirmation step for likely matches 7-12.

    Returns (confirmed_bool, confirm_type) where confirm_type is:
      - 'relationship' if confirmed via family/relative match
      - 'address'     if confirmed via address match
      - None          if not confirmed
    """
    relationship1 = row1.get("perp_relationship")
    relationship2 = row2.get("perp_relationship")

    # Relationship-based confirmation
    if (
        relationship1 == relationship2
        and relationship1 in allowed_relationships
        and df_rel is not None
    ):
        rels1 = relatives_for_referral(df_rel, row1["referral_id"], relationship1)
        rels2 = relatives_for_referral(df_rel, row2["referral_id"], relationship2)

        for r1 in rels1:
            for r2 in rels2:
                if match_rule(r1, r2) is not None:   # any strong rule 0-6
                    return True, "relationship"

    # Address-based confirmation
    if df_add is not None:
        addr1 = primary_address_for_referral(df_add, row1["referral_id"])
        addr2 = primary_address_for_referral(df_add, row2["referral_id"])
        if addr1 and addr2 and addr1 == addr2:
            return True, "address"

    return False, None


# -------------------------------------------------------------------
# Main function: add perp_reoccurrence_flag(Y/N) + metadata
# -------------------------------------------------------------------

def add_perp_reoccurrence_flag(df, df_rel=None, df_add=None):
    """
    For each (long_person_id, person_id):

    perp_reoccurrence_flag = 'Y' ONLY when:
    - The perpetrator appears on the *index* referral
      with subcategory_of_abuse = 'Child Sexually Acting Out'
      (is_index == 'Y' and subcategory_of_abuse == 'Child Sexually Acting Out')
    - AND the same perpetrator appears again on a *Subsequent* referral
      (referral_sequence_type == 'Subsequent')
      after the index, within the same longitudinal person id.

    We flag ONLY the Subsequent rows as 'Y'.

    Also adds:
      - perp_reoccurrence_match_type  ('strong' / 'likely')
      - perp_reoccurrence_rule        (0–12)
      - perp_reoccurrence_confirm_type ('relationship' / 'address' / NaN)
    """
    df = df.copy()
    df["perp_reoccurrence_flag"] = "N"
    df["perp_reoccurrence_match_type"] = np.nan
    df["perp_reoccurrence_rule"] = np.nan
    df["perp_reoccurrence_confirm_type"] = np.nan

    group_cols = ["long_person_id", "person_id"]
    needed_cols = group_cols + [
        "is_index",
        "referral_sequence_type",
        "subcategory_of_abuse",
        "referral_id",
        "perp_first_name",
        "perp_last_name",
        "perp_date_of_birth",
        "perp_date_of_birth_estimated",
        "perp_social_security_number",
        "perp_relationship",
    ]
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        raise ValueError(f"df must contain columns: {missing}")

    # We will only mark the "Subsequent" rows where a CSA perp reoccurs
    reocc_idx = set()

    # per-row classification for summary
    match_type_map = {}        # idx -> 'strong' or 'likely'
    match_rule_map = {}        # idx -> rule number
    confirm_type_map = {}      # idx -> 'relationship' / 'address' / None

    # Work within each longitudinal person + victim person
    for _, grp in df.groupby(group_cols):
        idxs = list(grp.index)
        if len(idxs) < 2:
            continue

        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                idx_i = idxs[i]
                idx_j = idxs[j]

                row_i = df.loc[idx_i]
                row_j = df.loc[idx_j]

                # Must be different referrals (referral-level, not row-level)
                if row_i["referral_id"] == row_j["referral_id"]:
                    continue

                # Identify index-CSA vs Subsequent
                is_index_csa_i = (
                    row_i["is_index"] == "Y"
                    and row_i["subcategory_of_abuse"] == "Child Sexually Acting Out"
                )
                is_index_csa_j = (
                    row_j["is_index"] == "Y"
                    and row_j["subcategory_of_abuse"] == "Child Sexually Acting Out"
                )

                is_subseq_i = row_i["referral_sequence_type"] == "Subsequent"
                is_subseq_j = row_j["referral_sequence_type"] == "Subsequent"

                # Only keep pairs where one side is index-CSA and the other is Subsequent
                if not (
                    (is_index_csa_i and is_subseq_j)
                    or (is_index_csa_j and is_subseq_i)
                ):
                    continue

                # Build perpetrator tuples
                r1 = (
                    row_i["perp_first_name"],
                    row_i["perp_last_name"],
                    row_i["perp_date_of_birth"],
                    row_i["perp_social_security_number"],
                    row_i["perp_date_of_birth_estimated"],
                )
                r2 = (
                    row_j["perp_first_name"],
                    row_j["perp_last_name"],
                    row_j["perp_date_of_birth"],
                    row_j["perp_social_security_number"],
                    row_j["perp_date_of_birth_estimated"],
                )

                # Decide which index is the "later" (Subsequent) row
                if is_index_csa_i and is_subseq_j:
                    later_idx = idx_j
                    row_later = row_j
                    row_index = row_i
                    r_later, r_index = r2, r1
                elif is_index_csa_j and is_subseq_i:
                    later_idx = idx_i
                    row_later = row_i
                    row_index = row_j
                    r_later, r_index = r1, r2
                else:
                    continue

                # Step 1: strong match?
                rule = match_rule(r_index, r_later)
                matched = False
                mtype = None
                confirm_type = None
                used_rule = None

                if rule is not None:
                    matched = True
                    mtype = "strong"
                    used_rule = rule
                else:
                    # Step 2: likely match + extra checks
                    lk_rule = likely_match_rule(r_index, r_later)
                    if lk_rule is not None:
                        confirmed, confirm_type = confirm_likely_match(
                            row_index, row_later, lk_rule, df_rel, df_add
                        )
                        if confirmed:
                            matched = True
                            mtype = "likely"
                            used_rule = lk_rule

                if matched:
                    reocc_idx.add(later_idx)

                    # update classification for this later row
                    prev_type = match_type_map.get(later_idx)
                    prev_rule = match_rule_map.get(later_idx)
                    prev_confirm = confirm_type_map.get(later_idx)

                    if prev_type is None:
                        match_type_map[later_idx] = mtype
                        match_rule_map[later_idx] = used_rule
                        confirm_type_map[later_idx] = confirm_type
                    else:
                        # upgrade from likely -> strong if needed
                        if prev_type == "likely" and mtype == "strong":
                            match_type_map[later_idx] = mtype
                            match_rule_map[later_idx] = used_rule
                            confirm_type_map[later_idx] = confirm_type
                        elif prev_type == mtype:
                            # same type: keep existing rule but prefer relationship confirmation
                            if prev_confirm != "relationship" and confirm_type == "relationship":
                                confirm_type_map[later_idx] = "relationship"
                            elif prev_confirm is None and confirm_type == "address":
                                confirm_type_map[later_idx] = "address"
                        # if prev_type is strong and new is likely, ignore new one

    if reocc_idx:
        df.loc[list(reocc_idx), "perp_reoccurrence_flag"] = "Y"

        # write classification columns back to df
        for idx, v in match_type_map.items():
            df.at[idx, "perp_reoccurrence_match_type"] = v
        for idx, v in match_rule_map.items():
            df.at[idx, "perp_reoccurrence_rule"] = v
        for idx, v in confirm_type_map.items():
            if v is not None:
                df.at[idx, "perp_reoccurrence_confirm_type"] = v

    return df


# -------------------------------------------------------------------
# Summary helper
# -------------------------------------------------------------------

def summarize_perp_reoccurrence(df):
    """
    Given a dataframe returned by add_perp_reoccurrence_flag,
    produce breakdowns:

    - How many definite (strong) vs likely matches
    - For likely:
        * how many perps in child's family (Y/N)
        * how many had exact match on a family member (Y/N)
        * how many were NOT in child's family but had same address (Y/N)

    Returns a dict of summary DataFrames.
    """
    df = df.copy()
    family_set = set(allowed_relationships)

    flagged = df[df["perp_reoccurrence_flag"] == "Y"].copy()
    if flagged.empty:
        return {
            "by_match_type": pd.DataFrame(columns=["match_type", "count"]),
            "by_rule": pd.DataFrame(columns=["match_type", "rule", "count"]),
            "likely_by_family": pd.DataFrame(columns=["perp_in_child_family", "count"]),
            "likely_exact_family_match": pd.DataFrame(columns=["exact_family_member_match", "count"]),
            "likely_nonfamily_same_address": pd.DataFrame(columns=["non_family_same_address", "count"]),
        }

    flagged["perp_in_child_family"] = flagged["perp_relationship"].isin(family_set)
    flagged["perp_reoccurrence_confirm_type"] = (
        flagged["perp_reoccurrence_confirm_type"].fillna("none")
    )

    # 1) definite vs likely
    s_match_type = (
        flagged["perp_reoccurrence_match_type"]
        .value_counts(dropna=False)
        .reset_index()
    )
    s_match_type.columns = ["match_type", "count"]

    # 2) by rule (for more detailed breakdown)
    s_rule = (
        flagged.groupby(["perp_reoccurrence_match_type", "perp_reoccurrence_rule"])
        .size()
        .reset_index(name="count")
    )
    s_rule.columns = ["match_type", "rule", "count"]

    # 3) only likely matches
    likely = flagged[flagged["perp_reoccurrence_match_type"] == "likely"].copy()
    if likely.empty:
        s_likely_family = pd.DataFrame(columns=["perp_in_child_family", "count"])
        s_likely_exact_family = pd.DataFrame(columns=["exact_family_member_match", "count"])
        s_likely_nonfam_address = pd.DataFrame(columns=["non_family_same_address", "count"])
    else:
        # 3a) perps in child's family Y/N
        s_likely_family = (
            likely.groupby("perp_in_child_family")
            .size()
            .reset_index(name="count")
        )

        # 3b) exact match on a family member:
        #     confirmed via relationship AND perp is in child's family
        likely["exact_family_member_match"] = (
            likely["perp_in_child_family"]
            & (likely["perp_reoccurrence_confirm_type"] == "relationship")
        )
        s_likely_exact_family = (
            likely.groupby("exact_family_member_match")
            .size()
            .reset_index(name="count")
        )

        # 3c) not in child's family but same address
        likely["non_family_same_address"] = (
            ~likely["perp_in_child_family"]
            & (likely["perp_reoccurrence_confirm_type"] == "address")
        )
        s_likely_nonfam_address = (
            likely.groupby("non_family_same_address")
            .size()
            .reset_index(name="count")
        )

    return {
        "by_match_type": s_match_type,
        "by_rule": s_rule,
        "likely_by_family": s_likely_family,
        "likely_exact_family_match": s_likely_exact_family,
        "likely_nonfamily_same_address": s_likely_nonfam_address,
    }

df_with_flags = add_perp_reoccurrence_flag(df, df_rel, df_add)
summaries = summarize_perp_reoccurrence(df_with_flags)

summaries["by_match_type"]
summaries["likely_by_family"]
