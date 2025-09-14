from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import json, pandas as pd
from utils import load_df

app = Flask(__name__)
app.secret_key = "dev-secret"

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "static" / "uploads"

def coords_px():
    p = BASE / "data" / "pref_coords_px.json"
    return json.loads(p.read_text(encoding="utf-8"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/coords_px')
def api_coords_px():
    return coords_px()

@app.route('/api/pref')
def api_pref():
    name = request.args.get("name","").strip()
    df = load_df()
    hit = df[df["prefecture_en"] == name].to_dict(orient="records")
    return jsonify({"items": hit})

@app.route('/add', methods=['GET','POST'])
def add():
    df = load_df()
    if request.method == 'POST':
        f = request.form
        required = ['prefecture_en','prefecture_ja','dish_en','dish_ja']
        if not all(f.get(k,'').strip() for k in required):
            flash('Prefecture (EN/JA) and Dish (EN/JA) are required.', 'danger')
            return redirect(url_for('add'))
        image = request.files.get('image'); image_path = ''
        if image and image.filename:
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            fname = secure_filename(f"{f.get('dish_en')}_{f.get('prefecture_en')}_{image.filename}")
            save_path = UPLOAD_DIR / fname; image.save(save_path)
            image_path = f"static/uploads/{fname}"
        new = {
            "id": str(len(df)+1),
            "prefecture_ja": f.get("prefecture_ja","").strip(),
            "prefecture_en": f.get("prefecture_en","").strip(),
            "dish_ja": f.get("dish_ja","").strip(),
            "dish_en": f.get("dish_en","").strip(),
            "category_en": f.get("category_en","").strip(),
            "description_en": f.get("description_en","").strip(),
            "image_path": image_path,
            "source": f.get("source","").strip(),
            "region": f.get("region","").strip(),
        }
        out = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        out.to_csv(BASE / "data" / "gourmet.csv", index=False)
        flash("Added ✔", "success")
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<id>', methods=['GET','POST'])
def edit(id):
    df = load_df()
    row = df[df["id"] == id]
    if row.empty:
        flash("Not found.", "danger"); return redirect(url_for('index'))
    row = row.iloc[0]
    if request.method == 'POST':
        f = request.form
        for k in ["prefecture_ja","prefecture_en","dish_ja","dish_en","category_en","description_en","source","region"]:
            df.loc[df["id"]==id, k] = f.get(k, row.get(k,"")).strip()
        image = request.files.get('image')
        if image and image.filename:
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            fname = secure_filename(f"{f.get('dish_en',row['dish_en'])}_{f.get('prefecture_en',row['prefecture_en'])}_{image.filename}")
            save_path = UPLOAD_DIR / fname; image.save(save_path)
            df.loc[df["id"]==id, "image_path"] = f"static/uploads/{fname}"
        df.to_csv(BASE / "data" / "gourmet.csv", index=False)
        flash("Updated ✔", "success"); return redirect(url_for('index'))
    return render_template('edit.html', item=row.to_dict())

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    df = load_df()
    df = df[df["id"] != id].reset_index(drop=True)
    df.to_csv(BASE / "data" / "gourmet.csv", index=False)
    flash("Deleted.", "warning"); return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
