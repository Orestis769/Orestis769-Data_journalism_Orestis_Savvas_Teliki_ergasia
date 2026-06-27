# -*- coding: utf-8 -*-
"""
============================================================================
ΕΔΔΕ2 - Ανάλυση Μεγάλων Δεδομένων μέσω της Γλώσσας Python
Τελική εργασία: Ανάλυση του πολιτικού λόγου του Κυριάκου Μητσοτάκη στο TikTok
============================================================================

Θέμα: Ελληνική επικαιρότητα/πολιτική επικοινωνία. Τα δεδομένα (161 βίντεο του
επίσημου λογαριασμού @kyriakosmitsotakis_ στο TikTok) εξορύχθηκαν από το
διαδίκτυο: ο ήχος κατέβηκε με scraping (yt-dlp) και απομαγνητοφωνήθηκε τοπικά
με το μοντέλο Whisper. Κάθε βίντεο συνοδεύεται από metadata (views, likes,
comments, shares, saves, διάρκεια, ημερομηνία).

Ο κώδικας καλύπτει τα βήματα 1-11 της εκφώνησης.
Εκτέλεση:  python analysis.py
Παράγει:   dataset_processed.csv  +  φάκελο charts/ με όλα τα γραφήματα.
"""
import os, glob, json, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

import greek_nlp as gnlp

# Γραμματοσειρά με ελληνικά glyphs
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPTS = os.path.join(HERE, "tiktok_output", "transcripts")
AUDIO = os.path.join(HERE, "tiktok_output", "_audio")
CHARTS = os.path.join(HERE, "charts")
os.makedirs(CHARTS, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT):
    FONT = matplotlib.font_manager.findfont("DejaVu Sans")


# ===========================================================================
# ΒΗΜΑ 1 & 2 — Εξόρυξη/φόρτωση δεδομένων σε DataFrame
# ===========================================================================
def parse_transcript(path):
    raw = open(path, encoding="utf-8").read()
    parts = raw.split("ΑΠΟΜΑΓΝΗΤΟΦΩΝΗΣΗ")
    header, body = parts[0], (parts[1].strip() if len(parts) > 1 else "")
    title = re.search(r"Τίτλος:\s*(.*)", header)
    return (title.group(1).strip() if title else ""), body


def load_dataframe():
    rows = []
    for tpath in sorted(glob.glob(os.path.join(TRANSCRIPTS, "*.txt"))):
        base = os.path.basename(tpath).replace(".txt", "")
        title, body = parse_transcript(tpath)
        info_path = os.path.join(AUDIO, base + ".info.json")
        meta = json.load(open(info_path, encoding="utf-8")) if os.path.exists(info_path) else {}
        rows.append({
            "video_id": base.split("_")[-1],
            "date_str": base[:8],
            "title": meta.get("title") or title,
            "transcript": body,
            "views": meta.get("view_count"),
            "likes": meta.get("like_count"),
            "comments": meta.get("comment_count"),
            "shares": meta.get("repost_count"),
            "saves": meta.get("save_count"),
            "duration": meta.get("duration"),
            "timestamp": meta.get("timestamp"),
            "url": meta.get("webpage_url"),
        })
    return pd.DataFrame(rows)


# ===========================================================================
# ΒΗΜΑ 3 — Καθαρισμός δεδομένων
# ===========================================================================
def clean_dataframe(df):
    df = df.copy()
    # Ημερομηνία
    df["date"] = pd.to_datetime(df["date_str"], format="%Y%m%d", errors="coerce")
    # Αριθμητικές στήλες -> numeric, NaN -> 0 (όπου λογικό)
    for c in ["views", "likes", "comments", "shares", "saves", "duration"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Αφαίρεση εγγραφών χωρίς κείμενο ή ημερομηνία
    df = df[df["transcript"].str.len() > 0]
    df = df.dropna(subset=["date"])
    # Πολύ μικρά transcripts (θόρυβος) -> εκτός
    df = df[df["transcript"].str.split().str.len() >= 5]
    # Αφαίρεση διπλότυπων video
    df = df.drop_duplicates(subset=["video_id"])
    # Συμπλήρωση τυχόν NaN engagement με 0
    df[["views", "likes", "comments", "shares", "saves"]] = (
        df[["views", "likes", "comments", "shares", "saves"]].fillna(0)
    )
    df = df.drop(columns=["date_str"]).reset_index(drop=True)
    return df


# ===========================================================================
# ΒΗΜΑ 4 — Προεπεξεργασία κειμένου (stopwords + stemming)
# ===========================================================================
def add_nlp_columns(df):
    df = df.copy()
    df["tokens"] = df["transcript"].apply(lambda t: gnlp.preprocess(t, do_stem=True))
    df["tokens_nostem"] = df["transcript"].apply(lambda t: gnlp.preprocess(t, do_stem=False))
    df["clean_text"] = df["tokens"].apply(lambda toks: " ".join(toks))
    df["word_count"] = df["transcript"].str.split().str.len()
    return df


# ===========================================================================
# ΒΗΜΑ 5 — Δημιουργία νέων παραμέτρων (στηλών)
# ===========================================================================
def add_feature_columns(df):
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%Y-%m")
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    # Ποσοστά / δείκτες αλληλεπίδρασης
    df["engagement"] = df["likes"] + df["comments"] + df["shares"] + df["saves"]
    df["engagement_rate_%"] = np.where(
        df["views"] > 0, (df["engagement"] / df["views"]) * 100, 0
    ).round(3)
    df["like_rate_%"] = np.where(df["views"] > 0, df["likes"] / df["views"] * 100, 0).round(3)
    df["comment_rate_%"] = np.where(df["views"] > 0, df["comments"] / df["views"] * 100, 0).round(3)
    df["views_per_sec"] = np.where(df["duration"] > 0, df["views"] / df["duration"], 0).round(1)
    return df


# ===========================================================================
# ΒΗΜΑ 9 — Πολικότητα & συναίσθημα (sentiment)
# ===========================================================================
def add_sentiment_columns(df):
    df = df.copy()
    sent = df["transcript"].apply(gnlp.sentiment_scores).apply(pd.Series)
    return pd.concat([df, sent], axis=1)


# ===========================================================================
# Custom WordCloud (χωρίς τη βιβλιοθήκη wordcloud)
# ===========================================================================
def make_wordcloud(freqs, path, width=1100, height=650, max_words=110, title=""):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    pad = 3
    occ = np.zeros((height, width), dtype=bool)
    items = sorted(freqs.items(), key=lambda x: -x[1])[:max_words]
    if not items:
        return
    maxf, minf = items[0][1], items[-1][1]
    palette = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),
               (148, 103, 189), (140, 86, 75), (23, 190, 207), (227, 119, 194)]
    cx, cy = width / 2, height / 2
    max_r = (width ** 2 + height ** 2) ** 0.5 / 2
    for idx, (word, f) in enumerate(items):
        # Λογαριθμική κλιμάκωση μεγέθους για ομαλότερη κατανομή
        scale = (np.log1p(f) - np.log1p(minf)) / (np.log1p(maxf) - np.log1p(minf) + 1e-9)
        size = int(16 + scale * 70)
        font = ImageFont.truetype(FONT, size)
        bbox = draw.textbbox((0, 0), word, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        placed = False
        ang = 0.0
        while True:
            r = 1.0 * ang  # Αρχιμήδειος σπείρα
            if r > max_r:
                break
            x = int(cx + r * np.cos(ang) - w / 2)
            y = int(cy + r * np.sin(ang) - h / 2)
            ang += 0.25 if r < 120 else 0.12
            if x < pad or y < pad or x + w >= width - pad or y + h >= height - pad:
                continue
            if not occ[y - pad:y + h + pad, x - pad:x + w + pad].any():
                draw.text((x - bbox[0], y - bbox[1]), word, font=font,
                          fill=palette[idx % len(palette)])
                occ[y - pad:y + h + pad, x - pad:x + w + pad] = True
                placed = True
                break
        if not placed:
            continue
    img.save(path)


# ===========================================================================
# ΒΗΜΑ 11 — CountVectorizer + cosine_similarity (χειροκίνητη υλοποίηση)
# ===========================================================================
def count_vectorize(docs, min_df=2, max_features=None):
    """Επιστρέφει (matrix [n_docs x n_terms], vocabulary list)."""
    from collections import Counter
    df_counts = Counter()
    doc_tokens = [d.split() for d in docs]
    for toks in doc_tokens:
        for term in set(toks):
            df_counts[term] += 1
    vocab = [t for t, c in df_counts.items() if c >= min_df]
    vocab.sort(key=lambda t: -df_counts[t])
    if max_features:
        vocab = vocab[:max_features]
    index = {t: i for i, t in enumerate(vocab)}
    mat = np.zeros((len(docs), len(vocab)), dtype=np.float32)
    for r, toks in enumerate(doc_tokens):
        for term in toks:
            j = index.get(term)
            if j is not None:
                mat[r, j] += 1
    return mat, vocab


def cosine_similarity_matrix(mat):
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normed = mat / norms
    return normed @ normed.T


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print(">> Βήμα 1-2: Φόρτωση δεδομένων...")
    df = load_dataframe()
    print(f"   Φορτώθηκαν {len(df)} εγγραφές.")

    print(">> Βήμα 3: Καθαρισμός...")
    df = clean_dataframe(df)
    print(f"   Μετά τον καθαρισμό: {len(df)} εγγραφές.")

    print(">> Βήμα 4: Προεπεξεργασία κειμένου (stopwords + stemming)...")
    df = add_nlp_columns(df)

    print(">> Βήμα 5: Νέες στήλες/παράμετροι...")
    df = add_feature_columns(df)

    print(">> Βήμα 9: Πολικότητα & συναίσθημα...")
    df = add_sentiment_columns(df)

    # ---------------- ΒΗΜΑ 8: Ημερομηνία ως index ----------------
    ts = df.set_index("date").sort_index()

    # ===================================================================
    # ΒΗΜΑ 6 — Αριθμητικές αναλύσεις & γραφήματα
    # ===================================================================
    print(">> Βήμα 6: Αριθμητικές αναλύσεις & γραφήματα...")
    num_cols = ["views", "likes", "comments", "shares", "saves",
                "duration", "word_count", "engagement_rate_%", "polarity"]
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(num_cols))); ax.set_xticklabels(num_cols, rotation=45, ha="right")
    ax.set_yticks(range(len(num_cols))); ax.set_yticklabels(num_cols)
    for i in range(len(num_cols)):
        for j in range(len(num_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                    color="black", fontsize=8)
    ax.set_title("Συσχέτιση αριθμητικών μεταβλητών (Pearson)")
    fig.colorbar(im, fraction=0.046, pad=0.04)
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06a_correlation.png", dpi=130); plt.close(fig)

    # Μηνιαία εξέλιξη προβολών & engagement (resample - ΒΗΜΑ 8)
    monthly = ts[["views", "likes", "engagement"]].resample("ME").mean()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly.index, monthly["views"], marker="o", label="Μ.Ο. προβολών")
    ax.plot(monthly.index, monthly["likes"], marker="s", label="Μ.Ο. likes")
    ax.set_title("Μηνιαία εξέλιξη προβολών & likes (resample 'ME')")
    ax.set_ylabel("Μέσος όρος"); ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06b_monthly_views.png", dpi=130); plt.close(fig)

    # Κατανομή προβολών (log)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["views"].clip(lower=1), bins=30)
    ax.set_xscale("log")
    ax.set_title("Κατανομή προβολών ανά βίντεο (log)")
    ax.set_xlabel("Προβολές"); ax.set_ylabel("Πλήθος βίντεο")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06c_views_hist.png", dpi=130); plt.close(fig)

    # Top-10 βίντεο κατά προβολές
    top10 = df.nlargest(10, "views")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    def _clean(t):
        t = "".join(c for c in t if ord(c) < 0x500 or 0x1F00 <= ord(c) <= 0x1FFF)
        t = t.strip()
        return (t[:42] + "...") if len(t) > 42 else t
    labels = [_clean(t) for t in top10["title"]]
    ax.barh(range(len(top10)), top10["views"], color="#1f77b4")
    ax.set_yticks(range(len(top10))); ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis(); ax.set_xlabel("Προβολές")
    ax.set_title("Top-10 βίντεο με τις περισσότερες προβολές")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06d_top10_views.png", dpi=130); plt.close(fig)

    # Διάρκεια vs engagement rate
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    sc = ax.scatter(df["duration"], df["engagement_rate_%"], c=df["polarity"],
                    cmap="RdYlGn", s=40, edgecolor="k", linewidth=0.3)
    ax.set_xlabel("Διάρκεια βίντεο (sec)"); ax.set_ylabel("Engagement rate (%)")
    ax.set_title("Διάρκεια vs Engagement (χρώμα = πολικότητα)")
    fig.colorbar(sc, label="Πολικότητα")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06e_duration_vs_engagement.png", dpi=130); plt.close(fig)

    # Πλήθος αναρτήσεων ανά έτος
    fig, ax = plt.subplots(figsize=(8, 5))
    df["year"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#ff7f0e")
    ax.set_title("Πλήθος βίντεο ανά έτος"); ax.set_xlabel("Έτος"); ax.set_ylabel("Πλήθος")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/06f_videos_per_year.png", dpi=130); plt.close(fig)

    # ===================================================================
    # ΒΗΜΑ 7 — Γραφήματα κειμένου (wordcloud, top-15, bigrams)
    # ===================================================================
    print(">> Βήμα 7: Γραφήματα κειμένου...")
    from collections import Counter
    all_tokens = [t for toks in df["tokens_nostem"] for t in toks]
    freq = Counter(all_tokens)

    make_wordcloud(dict(freq), f"{CHARTS}/07a_wordcloud.png")

    top15 = freq.most_common(15)
    fig, ax = plt.subplots(figsize=(10, 6))
    words, counts = zip(*top15)
    ax.barh(range(len(words)), counts, color="#2ca02c")
    ax.set_yticks(range(len(words))); ax.set_yticklabels(words)
    ax.invert_yaxis(); ax.set_xlabel("Συχνότητα")
    ax.set_title("15 πιο συχνές λέξεις")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/07b_top15_words.png", dpi=130); plt.close(fig)

    # Bigrams
    bigram_counter = Counter()
    for toks in df["tokens_nostem"]:
        for a, b in zip(toks, toks[1:]):
            bigram_counter[f"{a} {b}"] += 1
    top_bi = bigram_counter.most_common(15)
    fig, ax = plt.subplots(figsize=(10, 6))
    bwords, bcounts = zip(*top_bi)
    ax.barh(range(len(bwords)), bcounts, color="#9467bd")
    ax.set_yticks(range(len(bwords))); ax.set_yticklabels(bwords)
    ax.invert_yaxis(); ax.set_xlabel("Συχνότητα")
    ax.set_title("15 πιο συχνά διγράμματα (bigrams)")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/07c_bigrams.png", dpi=130); plt.close(fig)

    # ===================================================================
    # ΒΗΜΑ 10 — Πολικότητα ανά περίοδο (resample)
    # ===================================================================
    print(">> Βήμα 10: Χρονοσειρές πολικότητας...")
    pol_m = ts["polarity"].resample("ME").mean()
    fig, ax = plt.subplots(figsize=(11, 5))
    colors = ["#2ca02c" if v >= 0 else "#d62728" for v in pol_m]
    ax.bar(pol_m.index, pol_m.values, width=20, color=colors)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("Μέση πολικότητα ανά μήνα (resample 'ME')")
    ax.set_ylabel("Πολικότητα")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/10a_polarity_monthly.png", dpi=130); plt.close(fig)

    pol_q = ts["polarity"].resample("QE").mean()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(pol_q.index, pol_q.values, marker="o", color="#1f77b4")
    ax.axhline(0, color="k", lw=0.8)
    ax.fill_between(pol_q.index, pol_q.values, 0,
                    where=pol_q.values >= 0, color="#2ca02c", alpha=0.3)
    ax.fill_between(pol_q.index, pol_q.values, 0,
                    where=pol_q.values < 0, color="#d62728", alpha=0.3)
    ax.set_title("Μέση πολικότητα ανά τρίμηνο (resample 'QE')")
    ax.set_ylabel("Πολικότητα")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/10b_polarity_quarterly.png", dpi=130); plt.close(fig)

    # Κατανομή sentiment
    fig, ax = plt.subplots(figsize=(7, 5))
    order = ["positive", "neutral", "negative"]
    counts_s = df["sentiment"].value_counts().reindex(order).fillna(0)
    ax.bar(order, counts_s.values, color=["#2ca02c", "#7f7f7f", "#d62728"])
    ax.set_title("Κατανομή πολικότητας άρθρων")
    ax.set_ylabel("Πλήθος βίντεο")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/10c_sentiment_dist.png", dpi=130); plt.close(fig)

    # Κατανομή συναισθημάτων
    fig, ax = plt.subplots(figsize=(7.5, 5))
    emo = df["emotion"].value_counts()
    ax.bar(emo.index, emo.values, color="#17becf")
    ax.set_title("Κυρίαρχο συναίσθημα ανά βίντεο")
    ax.set_ylabel("Πλήθος")
    fig.tight_layout(); fig.savefig(f"{CHARTS}/10d_emotion_dist.png", dpi=130); plt.close(fig)

    # ===================================================================
    # ΒΗΜΑ 11 — Ομοιότητα κειμένων (CountVectorizer + cosine + heatmap)
    # ===================================================================
    print(">> Βήμα 11: Ομοιότητα κειμένων (cosine similarity)...")
    mat, vocab = count_vectorize(df["clean_text"].tolist(), min_df=2)
    sim = cosine_similarity_matrix(mat)

    # Heatmap σε δείγμα 40 βίντεο (για αναγνωσιμότητα)
    n = min(40, len(df))
    sample_idx = np.linspace(0, len(df) - 1, n).astype(int)
    sub = sim[np.ix_(sample_idx, sample_idx)]
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(sub, cmap="viridis", vmin=0, vmax=1)
    ax.set_title(f"Ομοιότητα κειμένων (cosine similarity) — δείγμα {n} βίντεο")
    ax.set_xlabel("Βίντεο"); ax.set_ylabel("Βίντεο")
    fig.colorbar(im, label="Ομοιότητα", fraction=0.046, pad=0.04)
    fig.tight_layout(); fig.savefig(f"{CHARTS}/11a_cosine_heatmap.png", dpi=130); plt.close(fig)

    # Πιο όμοια ζεύγη
    pairs = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            pairs.append((sim[i, j], i, j))
    pairs.sort(reverse=True)
    print("\n   Top-5 πιο όμοια ζεύγη βίντεο:")
    top_pairs_txt = []
    for s, i, j in pairs[:5]:
        line = f"   {s:.3f} | {df.iloc[i]['title'][:40]} <-> {df.iloc[j]['title'][:40]}"
        print(line); top_pairs_txt.append(line)

    # ===================================================================
    # Αποθήκευση επεξεργασμένου dataframe
    # ===================================================================
    out_cols = ["video_id", "date", "title", "transcript", "clean_text",
                "views", "likes", "comments", "shares", "saves", "duration",
                "word_count", "year", "month", "quarter", "engagement",
                "engagement_rate_%", "like_rate_%", "views_per_sec",
                "pos_words", "neg_words", "polarity", "sentiment", "emotion"]
    df[out_cols].to_csv(os.path.join(HERE, "dataset_processed.csv"),
                        index=False, encoding="utf-8-sig")
    # Δείγμα 20 εγγραφών για το GitHub
    df[out_cols].head(20).to_csv(os.path.join(HERE, "dataset_sample.csv"),
                                 index=False, encoding="utf-8-sig")

    # Σύνοψη
    print("\n========== ΣΥΝΟΨΗ ==========")
    print(f"Σύνολο βίντεο: {len(df)}")
    print(f"Περίοδος: {df['date'].min().date()} έως {df['date'].max().date()}")
    print(f"Σύνολο προβολών: {int(df['views'].sum()):,}")
    print(f"Μέσες προβολές/βίντεο: {df['views'].mean():,.0f}")
    print(f"Μέση πολικότητα: {df['polarity'].mean():.3f}")
    print("Κατανομή sentiment:", df['sentiment'].value_counts().to_dict())
    print("Λεξιλόγιο (όροι >= 2 docs):", len(vocab))
    print(f"\nΌλα τα γραφήματα -> {CHARTS}")


if __name__ == "__main__":
    main()
