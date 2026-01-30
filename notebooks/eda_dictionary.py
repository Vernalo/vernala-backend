import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import json
    from pathlib import Path
    import polars as pl
    from collections import Counter, defaultdict
    return Path, json, mo, pl


@app.cell
def _(mo):
    mo.md("""
    # Vernala Dictionary Exploratory Data Analysis

    This notebook analyzes scraped dictionary data for African languages,
    comparing French and English translations.
    """)
    return


@app.cell
def _(Path, json, pl):
    def load_language_data(language="ngiemboon", source_lang="en"):
        """Load all JSON files for a language and source language."""
        base_path = Path("scraped_data") / language / source_lang

        if not base_path.exists():
            return pl.DataFrame()

        all_entries = []

        for letter_file in sorted(base_path.glob("*.json")):
            try:
                with open(letter_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for entry in data:
                    source_word = entry.get(source_lang, entry.get("english", entry.get("french", "")))
                    letter = letter_file.stem

                    for translation in entry.get(language, []):
                        all_entries.append({
                            "letter": letter,
                            "source_language": source_lang,
                            "source_word": source_word,
                            "target_word": translation.get("word", ""),
                            "link": translation.get("link", "")
                        })
            except Exception as e:
                print(f"Error loading {letter_file}: {e}")

        return pl.DataFrame(all_entries)


    # Load both English and French data
    df_english = load_language_data("ngiemboon", "en")
    df_french = load_language_data("ngiemboon", "fr")

    # Combine both datasets
    df_all = pl.concat([df_english, df_french])
    return df_all, df_english, df_french


@app.cell
def _(df_all, df_english, df_french, mo):
    mo.md(f"""
    ## Dataset Overview

    - **Total entries (all languages)**: {len(df_all):,}
    - **English entries**: {len(df_english):,}
    - **French entries**: {len(df_french):,}
    - **Unique English words**: {df_english.select("source_word").n_unique():,}
    - **Unique French words**: {df_french.select("source_word").n_unique():,}
    """)
    return


@app.cell
def _(df_all, mo, pl):
    # Distribution by letter
    letter_distribution = (
        df_all
        .group_by(["letter", "source_language"])
        .agg(pl.count("source_word").alias("count"))
        .sort("letter")
    )

    mo.ui.table(letter_distribution, selection=None)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Common Words Between French and English
    """)
    return


@app.cell
def _(df_english, df_french):
    # Find common source words between French and English
    english_words = set(df_english.select("source_word").to_series().to_list())
    french_words = set(df_french.select("source_word").to_series().to_list())

    common_words = english_words & french_words

    print(f"Total common words: {len(common_words):,}")
    print(f"\nExamples of common words:")
    for word in sorted(list(common_words))[:20]:
        print(f"  - {word}")
    return (common_words,)


@app.cell
def _(df_english, df_french, mo, pl):
    # Common words by letter
    def get_common_words_by_letter():
        results = []

        for letter in "abcdefghijklmnopqrstuvwxyz":
            en_words = set(
                df_english
                .filter(pl.col("letter") == letter)
                .select("source_word")
                .to_series()
                .to_list()
            )

            fr_words = set(
                df_french
                .filter(pl.col("letter") == letter)
                .select("source_word")
                .to_series()
                .to_list()
            )

            common = en_words & fr_words

            results.append({
                "letter": letter,
                "english_words": len(en_words),
                "french_words": len(fr_words),
                "common_words": len(common),
                "overlap_pct": round(len(common) / max(len(en_words), len(fr_words)) * 100, 2) if max(len(en_words), len(fr_words)) > 0 else 0,
                "examples": ", ".join(sorted(list(common))[:5]) if common else ""
            })

        return pl.DataFrame(results)


    common_by_letter = get_common_words_by_letter()
    mo.ui.table(common_by_letter, selection=None)
    return (common_by_letter,)


@app.cell
def _(common_by_letter, mo):
    # Visualize overlap percentage
    import altair as alt

    chart = (
        alt.Chart(common_by_letter.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("letter:N", title="Letter"),
            y=alt.Y("overlap_pct:Q", title="Overlap Percentage (%)"),
            color=alt.Color("overlap_pct:Q", scale=alt.Scale(scheme="viridis")),
            tooltip=["letter", "english_words", "french_words", "common_words", "overlap_pct"]
        )
        .properties(
            title="French-English Word Overlap by Letter",
            width=700,
            height=400
        )
    )

    mo.ui.altair_chart(chart)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Translation Patterns
    """)
    return


@app.cell
def _(df_all, mo, pl):
    # Words with most translations
    translation_counts = (
        df_all
        .group_by(["source_language", "source_word"])
        .agg(pl.count("target_word").alias("num_translations"))
        .sort("num_translations", descending=True)
        .head(20)
    )

    mo.ui.table(translation_counts, selection=None)
    return


@app.cell
def _(df_english, df_french, pl):
    # Compare translations for common words
    def get_translation_comparison(word):
        """Compare French and English translations for a given word."""
        en_translations = (
            df_english
            .filter(pl.col("source_word") == word)
            .select("target_word")
            .to_series()
            .to_list()
        )

        fr_translations = (
            df_french
            .filter(pl.col("source_word") == word)
            .select("target_word")
            .to_series()
            .to_list()
        )

        common_translations = set(en_translations) & set(fr_translations)

        return {
            "word": word,
            "en_translations": en_translations,
            "fr_translations": fr_translations,
            "common_translations": list(common_translations),
            "translation_agreement": len(common_translations) > 0
        }
    return (get_translation_comparison,)


@app.cell
def _(common_words, get_translation_comparison):
    # Sample some common words and check translation agreement
    sample_common = sorted(list(common_words))[:10]

    print("Translation Agreement Analysis:")
    print("=" * 60)
    for _word in sample_common:
        comp = get_translation_comparison(_word)
        print(f"\nWord: '{comp['word']}'")
        print(f"  English translations: {comp['en_translations']}")
        print(f"  French translations: {comp['fr_translations']}")
        print(f"  Common translations: {comp['common_translations']}")
        print(f"  Agreement: {'✓' if comp['translation_agreement'] else '✗'}")
    return


@app.cell
def _(df_all, mo, pl):
    # Statistics on word lengths
    word_stats = (
        df_all
        .with_columns([
            pl.col("source_word").str.len_chars().alias("source_length"),
            pl.col("target_word").str.len_chars().alias("target_length")
        ])
        .select([
            pl.col("source_language"),
            pl.col("source_length").mean().alias("avg_source_length"),
            pl.col("target_length").mean().alias("avg_target_length"),
            pl.col("source_length").max().alias("max_source_length"),
            pl.col("target_length").max().alias("max_target_length")
        ])
        .group_by("source_language")
        .first()
    )

    mo.md(f"""
    ## Word Length Statistics

    {mo.as_html(mo.ui.table(word_stats, selection=None))}
    """)
    return


@app.cell
def _(df_all, mo, pl):
    # Unique target words
    unique_targets = (
        df_all
        .group_by("source_language")
        .agg([
            pl.col("target_word").n_unique().alias("unique_target_words"),
            pl.col("source_word").n_unique().alias("unique_source_words")
        ])
    )

    mo.md(f"""
    ## Vocabulary Coverage

    {mo.as_html(mo.ui.table(unique_targets, selection=None))}
    """)
    return


if __name__ == "__main__":
    app.run()
