import os

DB_FILE = "db.sql"

def load_db():
    data = []
    in_copy = False
    columns = []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("COPY public.mobile_specs"):
                    in_copy = True
                    columns = line.split("(")[1].split(")")[0].replace(" ", "").split(",")
                    continue
                if line == r"\.":
                    in_copy = False
                    continue
                if in_copy and line:
                    parts = line.split("\t")
                    row = {col: parts[i] if i < len(parts) else "" for i, col in enumerate(columns)}
                    data.append(row)
    except FileNotFoundError:
        print(f"Error: Database file '{DB_FILE}' not found.")
        return []
    except Exception as e:
        print(f"Error loading database: {e}")
        return []
    
    return data

DATA = load_db()

def get_single_specs(model_name):
    model_name = model_name.lower()
    for r in DATA:
        if r.get("name", "").lower() == model_name:
            return dict(r)
    return None

def get_multiple_specs(model_names):
    names = [m.lower() for m in model_names]
    return [dict(r) for r in DATA if r.get("name", "").lower() in names]

def compare_two_models(model1, model2):
    names = [model1.lower(), model2.lower()]
    return [dict(r) for r in DATA if r.get("name", "").lower() in names]

def compare_models_by_criteria(model1, model2, criteria_list):
    names = [model1.lower(), model2.lower()]
    res = []
    for r in DATA:
        if r.get("name", "").lower() in names:
            filtered_row = {"name": r.get("name", "")}
            for criteria in criteria_list:
                filtered_row[criteria] = r.get(criteria, "")
            res.append(filtered_row)
    return res

def filter_by_criteria(criteria_dict):
    res = []
    for r in DATA:
        match = True
        for k, v in criteria_dict.items():
            if k not in r or str(v).lower() not in str(r.get(k, "")).lower():
                match = False
                break
        if match:
            res.append(dict(r))
    return res

def call_logic(user_query):
    return {"query": user_query, "result": DATA}
