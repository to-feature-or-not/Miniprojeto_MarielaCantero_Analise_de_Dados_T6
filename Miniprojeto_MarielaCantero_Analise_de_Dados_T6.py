"""
Mini Desafio Semana 7 — Análise de Vendas do Setor Varejista.

Este script realiza a análise exploratória de dados de vendas de uma
rede de supermercados, cobrindo o período de 2019 a 2022. Inclui
limpeza, tratamento de datas, agrupamento de duplicatas e geração
automática de gráficos e relatórios.

Autor: Mariela Cantero (@to-feature-or-not)
Data: 2026-09-10
Curso: SCTEC — Etapa Profissionalizar

Uso:
    python Miniprojeto_MarielaCantero_Analise_de_Dados_T6.py

Dependências:
    pip install -r requirements.txt

Saídas geradas:
    - data/processed/varejo_final.csv  (dados limpos)
    - data/output/run_*.log            (log da execução)
    - data/output/grafico_*.png        (gráficos)
"""

# ==========================================
# IMPORTS
# ==========================================
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from io import StringIO
from pathlib import Path
import textwrap

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# CONFIGURATION
# ==========================================
#Paths
BASE_DIR = Path(__file__).parent

# Input
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DATA_FILE = RAW_DIR / "varejo.csv"

# Output
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

# Plotting style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Portuguese month names (for chart labels)
MONTH_NAMES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

# ==========================================
# FUNÇÕES
# ==========================================

def setup_directories() -> None:
    """Create necessary directories if they don't exist."""
    print("📁 Setting up directories...")

    for directory in [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"   • {directory.relative_to(BASE_DIR)}")

    print("✅ Directories ready")

def run_with_log(func, log_path: Path) -> None:
    """Run a function capturing all output to a log file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_path = log_path.parent / f"{log_path.stem}_{timestamp}{log_path.suffix}"
    
    buffer = StringIO()

    with redirect_stdout(buffer), redirect_stderr(buffer):
        try:
            func()
        except Exception as e:
            print(f"\n❌ ERROR: {e}")

    # Write to file
    output = buffer.getvalue()
    versioned_path.write_text(output, encoding="utf-8")

    # Print to terminal too
    print(output)

    print(f"\n📝 Log saved to {versioned_path.name}")

def load_data(path: Path) -> pd.DataFrame:
    """
    Load sales data from a CSV file.

    Args:
        path: Path to the CSV file.

    Returns:
        DataFrame with sales data.
    """
    print(f"📂 Loading data from {path.name}...")

    df = pd.read_csv(path, sep=";")

    print(f"✅ {len(df)} records loaded ({df.shape[1]} columns)")
    return df

def explore_data(df: pd.DataFrame) -> None:
    """
    Show DataFrame structure and sample.

    Args:
        df: DataFrame to explore.

    Returns:
        None. Only prints information to the terminal.
    """
    print("\n🔍 Exploring data structure...")

    print("\n   DataFrame summary:")
    df.info()

    print("\n   First rows:")
    print(df.head())

    print("\n✅ Exploration complete")

def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns where ALL values are null.

    Args:
        df: Original DataFrame.

    Returns:
        DataFrame without completely empty columns.
    """
    print("\n🗑️  Removing empty columns...")

    columns_before = df.shape[1]
    df = df.dropna(axis=1, how="all")
    columns_after = df.shape[1]
    removed = columns_before - columns_after

    if removed > 0:
        print(f"   • {removed} column(s) removed")
        print(f"   • Before: {columns_before} | After: {columns_after}")
    else:
        print("   • No empty columns found")

    print("\n✅ Cleanup complete")
    return df

def investigate_missing_values(
    df: pd.DataFrame,
    markers: list[str] | None = None,
) -> dict:
    """
    Investigate missing values in the DataFrame.

    Args:
        df: DataFrame to investigate.
        markers: Markers to search (default: common ones).

    Returns:
        Dictionary with:
        - 'nan_count': total NaN in the DataFrame
        - 'markers_found': dict of {marker: count} found
        - 'primary_marker': most common marker (or None)
    """
    if markers is None:
        markers = ["#N/D", "N/A", "null", "None", "-", "?"]

    print("\n🔍 Checking missing values...")

    # 1. pandas NaN values
    print("\n   [1/2] NaN values (pandas nulls):")
    total_nan = df.isnull().sum(axis=None)
    print(f"   Total: {total_nan}")

    if total_nan > 0:
        print("   • By column:")
        print(textwrap.indent(df.isnull().sum()[df.isnull().sum() > 0].to_string(),"   "))

    # 2. Text markers of absence
    print("\n   [2/2] Text markers of absence:")

    markers_found = {}
    for marker in markers:
        count = df.isin([marker]).sum(axis=None)
        if count > 0:
            markers_found[marker] = count
            print(f"      '{marker}': {count}")

    if not markers_found:
        print("   • No markers found")

    print("\n✅ Check complete")
    
    # Determine primary marker (most common)
    primary_marker = None
    if markers_found:
        primary_marker = max(markers_found, key=markers_found.get)

    return {
        "nan_count": total_nan,
        "markers_found": markers_found,
        "primary_marker": primary_marker,
    }

def investigate_missing_category(
    df: pd.DataFrame,
    category_column: str = "PR_CAT",
    id_column: str = "PR_ID",
    missing_markers: list[str] | None = None,
) -> dict:
    """
    Investigate records with missing category in a column.

    Args:
        df: DataFrame to investigate.
        category_column: Name of the column to check.
        id_column: Name of the ID column (for grouping).
        missing_markers: List of values that represent missing data.

    Returns:
        Dictionary with investigation results.
    """
    if missing_markers is None:
        missing_markers = ["#N/D"]

    markers_str = ", ".join(f"'{m}'" for m in missing_markers)
    print(f"\n🔍 Investigating {markers_str} in '{category_column}'...")

    # 1. Overview
    missing_df = df[df[category_column].isin(missing_markers)]
    total_missing = len(missing_df)
    total_records = len(df)
    percentage = total_missing / total_records * 100 if total_records > 0 else 0

    unique_ids = missing_df[id_column].nunique() if id_column in df.columns else 0

    print(f"\n   [1/5] Overview:")
    print(f"   • Total records: {total_records:,}")
    print(f"   • Records with missing category: {total_missing:,}")
    print(f"   • Percentage of total: {percentage:.2f}%")
    print(f"   • Unique {id_column}: {unique_ids}")

    if total_missing == 0:
        print("\n✅ No missing values found")
        return {
            "total_records": total_records,
            "total_missing": 0,
            "percentage": 0,
            "unique_ids": 0,
            "ids_100": [],
            "ids_partial": [],
            "lines_100": 0,
            "lines_partial": 0,
        }

    # 2. Sample
    print(f"\n   [2/5] Sample of affected records:")
    sample_columns = ["DATA", "CO_ID", "CL_ID", id_column, category_column, "PR_NOME"]
    sample_columns = [c for c in sample_columns if c in df.columns]
    print(missing_df[sample_columns].head(5).to_string(index=False))

    # 3. Per-marker breakdown (in this column)
    print(f"\n   [3/5] Breakdown by marker in '{category_column}':")
    for marker in missing_markers:
        count = df[category_column].isin([marker]).sum()
        if count > 0:
            pct = count / total_records * 100
            print(f"   • '{marker}': {count:,} ({pct:.2f}%)")

    # 4. All columns with any marker
    print(f"\n   [4/5] All columns with any marker:")
    all_marker_counts = {
        col: df[col].isin(missing_markers).sum()
        for col in df.columns
    }
    all_marker_counts = {c: n for c, n in all_marker_counts.items() if n > 0}

    if all_marker_counts:
        for column, count in all_marker_counts.items():
            print(f"   • {column}: {count:,}")
    else:
        print("   • No markers found")

    # 5. By ID
    print(f"\n   [5/5] {id_column} by missing percentage:")
    total_by_id = df[id_column].value_counts()
    missing_by_id = missing_df[id_column].value_counts()
    ratio = (missing_by_id / total_by_id * 100).dropna()

    ids_100 = ratio[ratio == 100].index.tolist()
    ids_partial = ratio[(ratio > 0) & (ratio < 100)].index.tolist()

    lines_100 = len(df[df[id_column].isin(ids_100)])
    lines_partial = len(df[df[id_column].isin(ids_partial)])

    print(f"   • {id_column} with 100% missing: {len(ids_100)}")
    print(f"     → {lines_100:,} lines ({lines_100/total_records*100:.2f}%)")
    print(f"   • {id_column} with partial missing: {len(ids_partial)}")
    print(f"     → {lines_partial:,} lines ({lines_partial/total_records*100:.2f}%)")

    print("\n✅ Investigation complete")

    return {
        "total_records": total_records,
        "total_missing": total_missing,
        "percentage": percentage,
        "unique_ids": unique_ids,
        "ids_100": ids_100,
        "ids_partial": ids_partial,
        "lines_100": lines_100,
        "lines_partial": lines_partial,
    }

def analyze_missing_by_dimension(
    df: pd.DataFrame,
    dimension: str,
    category_column: str = "PR_CAT",
    missing_markers: list[str] | None = None,
    top_n: int = 10,
    concentration_threshold: float = 50.0,
) -> dict:
    """
    Analyze missing category distribution by a dimension.

    Args:
        df: DataFrame to analyze.
        dimension: Column to group by (e.g., 'DATA', 'CO_ID', 'CL_SEG').
        category_column: Name of the category column.
        missing_markers: List of values that represent missing data.
        top_n: Number of top values to show.
        concentration_threshold: Percentage above which we consider
            the distribution "concentrated".

    Returns:
        Dictionary with distribution data.
    """
    if missing_markers is None:
        missing_markers = ["#N/D"]

    required = [dimension]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}
    
    markers_str = ", ".join(f"'{m}'" for m in missing_markers)
    print(f"\n   📊 Missing ({markers_str}) by '{dimension}':")

    missing_df = df[df[category_column].isin(missing_markers)]
    total = len(missing_df)

    if total == 0:
        print("   • No records found")
        return {}

    distribution = missing_df[dimension].value_counts()

    # Show top N
    for value, count in distribution.head(top_n).items():
        pct = count / total * 100
        print(f"   • {value}: {count:,} ({pct:.1f}%)")

    # Concentration check
    top_value = distribution.index[0]
    top_pct = distribution.iloc[0] / total * 100

    print()
    if top_pct > concentration_threshold:
        print(f"   ⚠️  Concentrated in '{top_value}' ({top_pct:.1f}%)")
    else:
        print(f"   ✅ Distributed across multiple values")

    return {
        "dimension": dimension,
        "total": total,
        "distribution": distribution,
        "top_value": top_value,
        "top_percentage": top_pct,
    }

def analyze_missing_by_product(
    df: pd.DataFrame,
    category_column: str = "PR_CAT",
    missing_markers: list[str] | None = None,
    id_column: str = "PR_ID",
    top_n: int = 10,
) -> dict:
    """
    Analyze missing category by product.

    Distinguishes products with 100% missing from those with
    partial missing (which could be filled from valid records).

    Args:
        df: DataFrame to analyze.
        category_column: Name of the category column.
        missing_markers: List of values that represent missing data.
        id_column: Name of the ID column.
        top_n: Number of top products to show.

    Returns:
        Dictionary with product analysis.
    """
    if missing_markers is None:
        missing_markers = ["#N/D"]

    markers_str = ", ".join(f"'{m}'" for m in missing_markers)
    print(f"\n   📦 Analyzing ({markers_str}) by '{id_column}':")

    missing_df = df[df[category_column].isin(missing_markers)]
    total = len(missing_df)

    if total == 0:
        print("   • No records found")
        return {"ids_100": [], "ids_partial": [], "lines_100": 0, "lines_partial": 0}

    # Ratio by ID
    total_by_id = df[id_column].value_counts()
    missing_by_id = missing_df[id_column].value_counts()
    ratio = (missing_by_id / total_by_id * 100).dropna()

    # Top IDs by missing count
    print(f"\n   Top {top_n} {id_column} by missing count:")
    for id_val, count in missing_by_id.head(top_n).items():
        total_for_id = total_by_id[id_val]
        pct = ratio[id_val]
        print(f"   • {id_val}: {count:,}/{total_for_id:,} ({pct:.0f}% missing)")

    # Split 100% vs partial
    ids_100 = ratio[ratio == 100].index.tolist()
    ids_partial = ratio[(ratio > 0) & (ratio < 100)].index.tolist()

    lines_100 = len(df[df[id_column].isin(ids_100)])
    lines_partial = len(df[df[id_column].isin(ids_partial)])

    print(f"\n   Summary:")
    print(f"   • {id_column} with 100% missing: {len(ids_100)}")
    print(f"     → {lines_100:,} lines ({lines_100/len(df)*100:.2f}%)")
    print(f"   • {id_column} with partial missing: {len(ids_partial)}")
    print(f"     → {lines_partial:,} lines ({lines_partial/len(df)*100:.2f}%)")

    return {
        "ids_100": ids_100,
        "ids_partial": ids_partial,
        "lines_100": lines_100,
        "lines_partial": lines_partial,
        "ratio": ratio,
    }

def decide_missing_strategy(
    investigation: dict,
    product_analysis: dict | None = None,
    threshold: float = 5.0,
    prefer_fill: bool = False,
) -> str:
    """
    Decide the best strategy for handling missing values.

    Args:
        investigation: Dict from investigate_missing_category().
        product_analysis: Optional dict from analyze_missing_by_product().
        threshold: Percentage threshold to choose between remove/fill.
        prefer_fill: If True, prefer filling over removing when
            the strategy is ambiguous.

    Returns:
        Strategy name: 'remove', 'fill_unknown', or 'fill_from_valid'.
    """
    print("\n🧠 Deciding missing value strategy...")

    percentage = investigation.get("percentage", 0)
    products_partial = product_analysis.get("ids_partial", []) if product_analysis else []

    print(f"\n   • Missing percentage: {percentage:.2f}%")
    print(f"   • Products with partial missing: {len(products_partial)}")
    print(f"   • Threshold: {threshold}%")

    # Decision logic
    if len(products_partial) > 0:
        strategy = "fill_from_valid"
        reason = "Some products have valid category elsewhere"

    elif percentage < threshold:
        if prefer_fill:
            strategy = "fill_unknown"
            reason = f"Missing < {threshold}%, but prefer_fill=True"
        else:
            strategy = "remove"
            reason = f"Missing < {threshold}%, removing is safe"

    else:
        strategy = "fill_unknown"
        reason = f"Missing >= {threshold}%, keeping records"

    print(f"\n   ✅ Strategy: {strategy.upper()}")
    print(f"   • Reason: {reason}")

    return strategy

def handle_missing_category(
    df: pd.DataFrame,
    strategy: str,
    category_column: str = "PR_CAT",
    missing_markers: list[str] | None = None,
    fallback_value: str = "UNKNOWN",
    id_column: str = "PR_ID",
) -> pd.DataFrame:
    """
    Handle missing values in a category column.

    Args:
        df: DataFrame to handle.
        strategy: 'remove', 'fill_unknown', or 'fill_from_valid'.
        category_column: Name of the category column.
        missing_markers: List of values that represent missing data.
        fallback_value: Value to use when no valid value is available.
        id_column: Column used to find valid categories for fill_from_valid.

    Returns:
        DataFrame with missing values handled.
    """
    if missing_markers is None:
        missing_markers = ["#N/D"]

    print(f"\n🛠️  Handling missing category (strategy: {strategy})...")

    lines_before = len(df)

    if strategy == "remove":
        # Remove rows where category is IN the missing markers
        mask = df[category_column].isin(missing_markers)
        df = df[~mask].copy()
        removed = lines_before - len(df)
        print(f"   • Removed {removed:,} records")

    elif strategy == "fill_unknown":
        # Replace all missing markers with fallback value
        mask = df[category_column].isin(missing_markers)
        filled = mask.sum()
        df.loc[mask, category_column] = fallback_value
        print(f"   • Filled {filled:,} records with '{fallback_value}'")

    elif strategy == "fill_from_valid":
        # Get valid category for each ID (rows NOT in missing_markers)
        valid = (
            df[~df[category_column].isin(missing_markers)]
            .groupby(id_column)[category_column]
            .first()
        )

        # Fill missing rows with valid category from same ID
        mask = df[category_column].isin(missing_markers)
        df.loc[mask, category_column] = df.loc[mask, id_column].map(valid)

        # Remaining NaN (IDs with no valid category) → fallback
        remaining = df[category_column].isna().sum()
        df[category_column] = df[category_column].fillna(fallback_value)

        filled_valid = mask.sum() - remaining
        print(f"   • Filled {filled_valid:,} using valid categories")
        if remaining > 0:
            print(f"   • Filled {remaining:,} with '{fallback_value}'")

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    print(f"   • Lines before: {lines_before:,}")
    print(f"   • Lines after: {len(df):,}")

    print("\n✅ Handling complete")
    return df

def validate_clean_data(
    df: pd.DataFrame,
    columns_to_check: list[str] | None = None,
    markers: list[str] | None = None,
    raise_on_failure: bool = False,
) -> bool:
    """
    Validate that data is clean (no missing markers).

    Args:
        df: DataFrame to validate.
        columns_to_check: Columns to check (default: all).
        markers: Markers to look for (default: common ones).
        raise_on_failure: If True, raises ValueError when data is dirty.

    Returns:
        True if clean, False otherwise.
    """
    if markers is None:
        markers = ["#N/D", "N/A", "null", "None", "-", "?"]

    columns = columns_to_check or df.columns.tolist()
    columns = [c for c in columns if c in df.columns]

    print("\n🔍 Final validation...")
    print("\n   Cleanup was already applied. Confirming nothing was left behind.")
    print(f"\n   • Columns to check: {len(columns)}")
    print(f"   • Markers to search: {markers}")

    # Check markers
    found_per_marker = {}
    for marker in markers:
        count = df[columns].isin([marker]).sum().sum()
        if count > 0:
            found_per_marker[marker] = count

    # Check pandas NaN
    nan_count = df[columns].isnull().sum().sum()

    # Determine clean
    total_found = sum(found_per_marker.values()) + nan_count
    is_clean = total_found == 0

    # Report
    if is_clean:
        print("\n   ✅ Cleanup successful: no missing values remain")
    else:
        print("\n   ⚠️  Cleanup incomplete: missing values still present")
        for marker, count in found_per_marker.items():
            print(f"      - '{marker}': {count:,}")
        if nan_count > 0:
            print(f"      - pandas NaN: {nan_count:,}")

    print("\n✅ Validation complete")

    if not is_clean and raise_on_failure:
        raise ValueError(f"Data is not clean: {total_found} missing values found")

    return is_clean

def save_data(
    df: pd.DataFrame,
    path: Path,
    separator: str = ";",
    description: str = "data",
) -> None:
    """
    Save DataFrame to a CSV file.

    Args:
        df: DataFrame to save.
        path: Full path (including filename) to save to.
        separator: CSV separator.
        description: Description for the log message.

    Returns:
        None.
    """
    print(f"\n💾 Saving {description} to {path.name}...")

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep=separator, index=False)  #se você não passar index=False, o pandas salva uma coluna extra com o índice (0, 1, 2...) que vira "lixo" no CSV.

    print(f"   • Rows: {len(df):,}")
    print(f"   • Columns: {df.shape[1]}")
    print(f"   • Path: {path.relative_to(BASE_DIR)}")
    print("✅ Save complete")

def handle_nan_values(
    df: pd.DataFrame,
    strategy: str = "remove",
    threshold: float = 5.0,
    fill_value: dict | None = None,
) -> pd.DataFrame:
    """
    Handle NaN values across the DataFrame.

    Strategies:
        - 'remove': drop rows with any NaN (if below threshold).
        - 'fill': fill NaN with values from fill_value dict.
        - 'auto': drop rows if missing < threshold, else raise error.

    Args:
        df: DataFrame to handle.
        strategy: 'remove', 'fill', or 'auto'.
        threshold: Max percentage of rows to auto-remove.
        fill_value: Dict mapping column → value to fill NaN.

    Returns:
        DataFrame with NaN handled.
    """
    print(f"\n🛠️  Handling NaN values (strategy: {strategy})...")

    total_nan = df.isnull().sum().sum()
    if total_nan == 0:
        print("   ✅ No NaN values found")
        return df

    total_rows = len(df)
    rows_with_nan = df.isnull().any(axis=1).sum()
    pct = rows_with_nan / total_rows * 100

    print(f"   • Total NaN: {total_nan:,}")
    print(f"   • Rows with NaN: {rows_with_nan:,} ({pct:.2f}%)")

    # Show columns
    nan_by_column = df.isnull().sum()
    nan_by_column = nan_by_column[nan_by_column > 0]
    print(f"   • Columns affected:")
    for col, count in nan_by_column.items():
        print(f"      - {col}: {count:,}")

    # Auto strategy
    if strategy == "auto":
        if pct < threshold:
            strategy = "remove"
            print(f"   • Auto: below {threshold}% → remove rows")
        else:
            strategy = "fill"
            print(f"   • Auto: above {threshold}% → fill values")

    # Apply
    if strategy == "remove":
        df = df.dropna().copy()
        print(f"   • Removed {total_rows - len(df):,} rows")
        print(f"   • Remaining: {len(df):,} rows")

    elif strategy == "fill":
        if fill_value is None:
            raise ValueError("fill_value must be provided for 'fill' strategy")

        for col, val in fill_value.items():
            if col in df.columns:
                count = df[col].isnull().sum()
                if count > 0:
                    df[col] = df[col].fillna(val)
                    print(f"   • Filled {count:,} NaN in '{col}' with '{val}'")

        # Any remaining NaN?
        remaining = df.isnull().sum().sum()
        if remaining > 0:
            print(f"   ⚠️  {remaining:,} NaN still present (columns not in fill_value)")

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    print("\n✅ Handling complete")
    return df

def handle_text_markers(
    df: pd.DataFrame,
    strategy: str = "replace",
    markers: list[str] | None = None,
    fallback_value: str = "UNKNOWN",
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Handle text markers of absence across the DataFrame.

    Args:
        df: DataFrame to handle.
        strategy: 'replace' (with fallback) or 'remove' (rows).
        markers: List of markers to handle (default: common ones).
        fallback_value: Value to use when replacing.
        columns: Columns to check (default: all).

    Returns:
        DataFrame with markers handled.
    """
    if markers is None:
        markers = ["#N/D", "N/A", "null", "None", "-", "?"]

    print(f"\n🛠️  Handling text markers (strategy: {strategy})...")

    columns = columns or df.columns.tolist()
    columns = [c for c in columns if c in df.columns]

    total_found = 0
    rows_before = len(df)

    for marker in markers:
        count = df[columns].isin([marker]).sum().sum()
        if count > 0:
            total_found += count

            if strategy == "replace":
                df[columns] = df[columns].replace(marker, fallback_value)
                print(f"   • Replaced {count:,} '{marker}' with '{fallback_value}'")

            elif strategy == "remove":
                mask = df[columns].isin([marker]).any(axis=1)
                df = df[~mask].copy()
                print(f"   • Removed rows with '{marker}'")

    if total_found == 0:
        print("   ✅ No markers found")
    else:
        print(f"   • Total markers handled: {total_found:,}")
        print(f"   • Rows before: {rows_before:,}")
        print(f"   • Rows after: {len(df):,}")

    print("\n✅ Handling complete")
    return df

def convert_dates(
    df: pd.DataFrame,
    date_column: str = "DATA",
    date_format: str = "%d/%m/%Y",
) -> pd.DataFrame:
    """
    Convert a date column to datetime.

    Args:
        df: DataFrame to process.
        date_column: Name of the date column.
        date_format: Expected format (default: DD/MM/YYYY).

    Returns:
        DataFrame with the date column converted to datetime.
    """
    print(f"\n📅 Converting '{date_column}' to datetime...")

    if date_column not in df.columns:
        print(f"   ⚠️  Column '{date_column}' not found. Skipping.")
        return df

    print(f"   • Original dtype: {df[date_column].dtype}")
    print(f"   • Sample: {df[date_column].iloc[0]}")
    print(f"   • Expected format: {date_format}")

    df[date_column] = pd.to_datetime(
        df[date_column],
        format=date_format,
        errors="coerce",
    )

    print(f"   • New dtype: {df[date_column].dtype}")
    print("\n✅ Conversion complete")
    return df

def validate_dates(
    df: pd.DataFrame,
    date_column: str = "DATA",
    min_year: int = 2000,
) -> dict:
    """
    Validate dates in a column.

    Checks for:
    - Invalid dates (NaT after conversion)
    - Dates in the future
    - Dates before a minimum year

    Args:
        df: DataFrame to validate.
        date_column: Name of the date column.
        min_year: Minimum acceptable year.

    Returns:
        Dictionary with validation results.
    """
    print(f"\n🔍 Validating dates in '{date_column}'...")

    if date_column not in df.columns:
        print(f"   ⚠️  Column '{date_column}' not found. Skipping.")
        return {}

    # 1. Invalid dates (NaT)
    invalid_count = df[date_column].isna().sum()
    print(f"\n   [1/4] Invalid dates (NaT):")
    print(f"   • Total: {invalid_count:,}")

    if invalid_count > 0:
        print("   • Sample of invalid dates:")
        sample = df[df[date_column].isna()][date_column].head(5)
        print(textwrap.indent(sample.to_string(), "      "))

    # 2. Period
    print(f"\n   [2/4] Period:")
    valid_dates = df[date_column].dropna()
    if len(valid_dates) > 0:
        print(f"   • Earliest: {valid_dates.min()}")
        print(f"   • Latest: {valid_dates.max()}")
    else:
        print("   • No valid dates to analyze")

    # 3. Future dates
    print(f"\n   [3/4] Future dates:")
    today = pd.Timestamp.now()
    future_count = (df[date_column] > today).sum()
    print(f"   • Count: {future_count:,}")

    if future_count > 0:
        print("   • Sample:")
        future_sample = df[df[date_column] > today][date_column].head(5)
        print(textwrap.indent(future_sample.to_string(), "      "))

    # 4. Old dates
    print(f"\n   [4/4] Dates before {min_year}:")
    cutoff = pd.Timestamp(f"{min_year}-01-01")
    old_count = (df[date_column] < cutoff).sum()
    print(f"   • Count: {old_count:,}")

    if old_count > 0:
        print("   • Sample:")
        old_sample = df[df[date_column] < cutoff][date_column].head(5)
        print(textwrap.indent(old_sample.to_string(), "      "))

    # Summary
    is_valid = invalid_count == 0 and future_count == 0 and old_count == 0

    print()
    if is_valid:
        print("   ✅ All dates are valid")
    else:
        print(f"   ⚠️  Issues found:")
        if invalid_count > 0:
            print(f"      - {invalid_count:,} invalid dates")
        if future_count > 0:
            print(f"      - {future_count:,} future dates")
        if old_count > 0:
            print(f"      - {old_count:,} dates before {min_year}")

    print("\n✅ Validation complete")

    return {
        "invalid_count": invalid_count,
        "future_count": future_count,
        "old_count": old_count,
        "earliest": valid_dates.min() if len(valid_dates) > 0 else None,
        "latest": valid_dates.max() if len(valid_dates) > 0 else None,
        "is_valid": is_valid,
    }

def handle_invalid_dates(
    df: pd.DataFrame,
    validation: dict,
    date_column: str = "DATA",
    threshold: float = 1.0,
    strategy: str = "auto",
) -> pd.DataFrame:
    """
    Handle invalid dates based on validation results.

    Args:
        df: DataFrame to handle.
        validation: Dict from validate_dates().
        date_column: Name of the date column.
        threshold: Max percentage of invalid dates to auto-remove.
        strategy: 'auto', 'remove', 'keep', or 'raise'.

    Returns:
        DataFrame with invalid dates handled.
    """
    print(f"\n🛠️  Handling invalid dates (strategy: {strategy})...")

    total = len(df)
    invalid_count = validation.get("invalid_count", 0)
    future_count = validation.get("future_count", 0)
    old_count = validation.get("old_count", 0)

    total_invalid = invalid_count + future_count + old_count

    if total_invalid == 0:
        print("   ✅ No invalid dates to handle")
        return df

    percentage = total_invalid / total * 100
    print(f"   • Invalid dates: {total_invalid:,} ({percentage:.2f}%)")

    # Auto strategy
    if strategy == "auto":
        if percentage < threshold:
            strategy = "remove"
            print(f"   • Auto: below {threshold}% threshold → remove")
        else:
            strategy = "raise"
            print(f"   • Auto: above {threshold}% threshold → raise error")

    # Apply strategy
    if strategy == "remove":
        mask = (
            df[date_column].isna()
            | (df[date_column] > pd.Timestamp.now())
            | (df[date_column] < pd.Timestamp("2000-01-01"))
        )
        df = df[~mask].copy()
        removed = total - len(df)
        print(f"   • Removed {removed:,} records")
        print(f"   • Remaining: {len(df):,} records")

    elif strategy == "keep":
        print("   • Keeping invalid dates (no change)")

    elif strategy == "raise":
        raise ValueError(
            f"Invalid dates found: {total_invalid:,} ({percentage:.2f}%)"
        )

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    print("\n✅ Handling complete")
    return df

def add_date_parts(
    df: pd.DataFrame,
    date_column: str = "DATA",
    parts: list[str] | None = None,
) -> pd.DataFrame:
    """
    Add date-part columns extracted from a datetime column.

    Args:
        df: DataFrame to process.
        date_column: Name of the datetime column.
        parts: List of parts to extract. Options:
            'year', 'month', 'day', 'weekday', 'quarter'.
            Default: ['year', 'month'].

    Returns:
        DataFrame with new columns.
    """
    print(f"\n📅 Extracting date parts from '{date_column}'...")

    if date_column not in df.columns:
        print(f"   ⚠️  Column '{date_column}' not found. Skipping.")
        return df

    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        print(f"   ⚠️  '{date_column}' is not datetime. Convert first.")
        return df

    if parts is None:
        parts = ["year", "month"]

    # Map of part name → (column name, accessor)
    part_map = {
        "year": ("YEAR", "year"),
        "month": ("MONTH", "month"),
        "day": ("DAY", "day"),
        "weekday": ("WEEKDAY", "dayofweek"),
        "quarter": ("QUARTER", "quarter"),
    }

    created = []
    for part in parts:
        if part in part_map:
            col_name, accessor = part_map[part]
            df[col_name] = getattr(df[date_column].dt, accessor)
            created.append(col_name)

    print(f"   • Created columns: {', '.join(created)}")

    if "year" in parts and "YEAR" in df.columns:
        years = sorted(int(y) for y in df["YEAR"].unique())
        print(f"   • Years: {years}")

    if "month" in parts and "MONTH" in df.columns:
        months = sorted(int(m) for m in df["MONTH"].unique())
        print(f"   • Months: {months}")

    print("\n✅ Extraction complete")
    return df

def check_duplicates(
    df: pd.DataFrame,
    key_columns: list[str] | None = None,
    top_n: int = 5,
) -> dict:
    """
    Check for duplicate records in a DataFrame.

    Checks both complete duplicates (all columns) and duplicates
    by a key (specific columns).

    Args:
        df: DataFrame to check.
        key_columns: Columns that define a unique record.
            Default: ['DATA', 'CO_ID', 'PR_ID'].
        top_n: Number of sample duplicates to show.

    Returns:
        Dictionary with duplicate information.
    """
    if key_columns is None:
        key_columns = ["DATA", "CO_ID", "PR_ID"]

    print("\n🔍 Checking duplicates...")

    total = len(df)

    # 1. Complete duplicates (all columns)
    complete_dups = df.duplicated().sum()
    print(f"\n   [1/2] Complete duplicates (all columns):")
    print(f"   • Count: {complete_dups:,} ({complete_dups/total*100:.2f}%)")

    if complete_dups > 0:
        print(f"   • Sample:")
        sample = df[df.duplicated(keep=False)].head(top_n)
        print(textwrap.indent(sample.to_string(index=False), "      "))

    # 2. Duplicates by key
    valid_keys = [c for c in key_columns if c in df.columns]
    if len(valid_keys) < len(key_columns):
        missing = set(key_columns) - set(valid_keys)
        print(f"\n   ⚠️  Missing key columns: {missing}")

    if valid_keys:
        key_dups = df.duplicated(subset=valid_keys).sum()
        print(f"\n   [2/2] Duplicates by key {valid_keys}:")
        print(f"   • Count: {key_dups:,} ({key_dups/total*100:.2f}%)")

        if key_dups > 0:
            print(f"   • Sample:")
            sample = df[df.duplicated(subset=valid_keys, keep=False)].sort_values(by=valid_keys).head(top_n)
            print(textwrap.indent(sample.to_string(index=False), "      "))

    print("\n✅ Check complete")

    return {
        "total": total,
        "complete_duplicates": complete_dups,
        "key_duplicates": key_dups if valid_keys else 0,
        "key_columns": valid_keys,
    }

def create_quantity_column(
    df: pd.DataFrame,
    key_columns: list[str] | None = None,
    quantity_column: str = "QUANTITY",
) -> pd.DataFrame:
    """
    Create a QUANTITY column by grouping duplicate records.

    Records that are identical (except for the implicit quantity)
    are grouped, and the count becomes the QUANTITY.

    Args:
        df: DataFrame to process.
        key_columns: Columns that define a unique record (grouping keys).
            Default: ['DATA', 'CO_ID', 'CL_ID', 'CL_GENERO', 'CL_EC',
            'CL_FHL', 'CL_SEG', 'PR_ID', 'PR_CAT', 'PR_NOME'].
        quantity_column: Name of the new quantity column.

    Returns:
        DataFrame with the new QUANTITY column.
    """
    if key_columns is None:
        key_columns = [
            "DATA", "CO_ID", "CL_ID", "CL_GENERO", "CL_EC", "CL_FHL",
            "CL_SEG", "PR_ID", "PR_CAT", "PR_NOME","YEAR", "MONTH", "WEEKDAY"
        ]

    # Keep only columns that exist
    key_columns = [c for c in key_columns if c in df.columns]

    print(f"\n📊 Creating '{quantity_column}' column...")
    print(f"   • Grouping by: {len(key_columns)} columns")

    lines_before = len(df)

    # Group and count
    df_grouped = (
        df.groupby(key_columns)
        .size()
        .reset_index(name=quantity_column)
    )

    lines_after = len(df_grouped)
    grouped = lines_before - lines_after

    print(f"   • Lines before: {lines_before:,}")
    print(f"   • Lines after: {lines_after:,}")
    print(f"   • Lines grouped: {grouped:,}")
    print(f"   • Reduction: {grouped/lines_before*100:.2f}%")

    # Stats about QUANTITY
    print(f"\n   • QUANTITY stats:")
    print(f"      - Min: {df_grouped[quantity_column].min()}")
    print(f"      - Max: {df_grouped[quantity_column].max()}")
    print(f"      - Mean: {df_grouped[quantity_column].mean():.2f}")
    print(f"      - Median: {df_grouped[quantity_column].median():.0f}")

    print("\n✅ Column created")
    return df_grouped

def validate_quantity(
    df: pd.DataFrame,
    quantity_column: str = "QUANTITY",
    original_count: int | None = None,
) -> None:
    """
    Validate the QUANTITY column.

    Args:
        df: DataFrame to validate.
        quantity_column: Name of the quantity column.
        original_count: Original number of lines (before grouping).
            If provided, checks that sum of QUANTITY matches.

    Returns:
        None. Only prints information.
    """
    print(f"\n🔍 Validating '{quantity_column}' column...")

    if quantity_column not in df.columns:
        print(f"   ⚠️  Column '{quantity_column}' not found.")
        return

    total_quantity = df[quantity_column].sum()
    total_records = len(df)

    print(f"   • Records: {total_records:,}")
    print(f"   • Sum of {quantity_column}: {total_quantity:,}")

    # Check if matches original
    if original_count is not None:
        match = "✅" if total_quantity == original_count else "❌"
        print(f"   • Original lines: {original_count:,}")
        print(f"   • {match} Match: {total_quantity == original_count}")

    # Distribution
    print(f"\n   • Distribution (top 5 + rest):")
    dist = df[quantity_column].value_counts().sort_index()
    # Top 5
    for qty, count in dist.head(5).items():
        pct = count / total_records * 100
        print(f"      - {qty}: {count:,} ({pct:.2f}%)")

    # Rest
    if len(dist) > 5:
        rest_count = dist.iloc[5:].sum()
        pct = rest_count / total_records * 100
        print(f"      - 6+: {rest_count:,} ({pct:.2f}%)")

    # Check for zero/negative
    invalid = (df[quantity_column] <= 0).sum()
    if invalid > 0:
        print(f"\n   ⚠️  {invalid:,} records with QUANTITY <= 0")
    else:
        print(f"\n   ✅ All values are positive")

    print("\n✅ Validation complete")

def analyze_sales_by_month(
    df: pd.DataFrame,
    quantity_column: str = "QUANTITY",
    month_column: str = "MONTH",
) -> dict:
    """
    Analyze sales by month (seasonality).

    Args:
        df: DataFrame with sales data.
        quantity_column: Name of the quantity column.
        month_column: Name of the month column.

    Returns:
        Dictionary with monthly sales data.
    """
    print("\n📈 Analyzing sales by month...")

    required = [month_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    # Group by month
    by_month = (
        df.groupby(month_column)[quantity_column]
        .sum()
        .sort_index()
    )

    # Stats
    total = by_month.sum()
    best_month = by_month.idxmax()
    worst_month = by_month.idxmin()

    # Month names (Portuguese)
    month_names = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }

    print(f"\n   • Sales by month:")
    for month, qty in by_month.items():
        name = month_names.get(month, str(month))
        pct = qty / total * 100
        print(f"      - {name}: {qty:,} ({pct:.1f}%)")

    print(f"\n   • 🏆 Best month: {month_names[best_month]} ({by_month[best_month]:,})")
    print(f"   • 📉 Worst month: {month_names[worst_month]} ({by_month[worst_month]:,})")
    print(f"   • Total: {total:,}")

    print("\n✅ Analysis complete")

    return {
        "by_month": by_month,
        "total": total,
        "best_month": best_month,
        "best_month_name": month_names[best_month],
        "best_month_value": by_month[best_month],
        "worst_month": worst_month,
        "worst_month_name": month_names[worst_month],
        "worst_month_value": by_month[worst_month],
    }

def analyze_top_products(
    df: pd.DataFrame,
    product_column: str = "PR_NOME",
    quantity_column: str = "QUANTITY",
    top_n: int = 10,
) -> dict:
    """
    Analyze top products by quantity.

    Args:
        df: DataFrame with sales data.
        product_column: Name of the product column.
        quantity_column: Name of the quantity column.
        top_n: Number of top products to show.

    Returns:
        Dictionary with top products data.
    """
    print(f"\n🏆 Analyzing top {top_n} products...")

    required = [product_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    top = (
        df.groupby(product_column)[quantity_column]
        .sum()
        .nlargest(top_n)
    )

    total = df[quantity_column].sum()

    print(f"\n   • Top {top_n} products:")
    for i, (product, qty) in enumerate(top.items(), 1):
        pct = qty / total * 100
        print(f"      {i:2d}. {product}: {qty:,} ({pct:.2f}%)")

    print("\n✅ Analysis complete")

    return {
        "top_products": top,
        "total": total,
    }

def analyze_top_categories(
    df: pd.DataFrame,
    category_column: str = "PR_CAT",
    quantity_column: str = "QUANTITY",
) -> dict:
    """
    Analyze top categories by quantity.

    Args:
        df: DataFrame with sales data.
        category_column: Name of the category column.
        quantity_column: Name of the quantity column.

    Returns:
        Dictionary with category data.
    """
    print("\n📊 Analyzing top categories...")

    required = [category_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    by_cat = (
        df.groupby(category_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    total = by_cat.sum()

    print(f"\n   • Sales by category:")
    for category, qty in by_cat.items():
        pct = qty / total * 100
        print(f"      - {category}: {qty:,} ({pct:.1f}%)")

    print("\n✅ Analysis complete")

    return {
        "by_category": by_cat,
        "total": total,
    }

def analyze_sales_by_gender(
    df: pd.DataFrame,
    gender_column: str = "CL_GENERO",
    quantity_column: str = "QUANTITY",
    customer_column: str = "CO_ID",
) -> dict:
    """
    Analyze sales by customer gender.

    Args:
        df: DataFrame with sales data.
        gender_column: Name of the gender column.
        quantity_column: Name of the quantity column.
        customer_column: Name of the customer/purchase ID column.

    Returns:
        Dictionary with gender data.
    """
    print("\n👥 Analyzing sales by gender...")

    required = [gender_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    # Total quantity by gender
    by_gender = (
        df.groupby(gender_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    total = by_gender.sum()

    print(f"\n   • Quantity by gender:")
    for gender, qty in by_gender.items():
        pct = qty / total * 100
        print(f"      - {gender}: {qty:,} ({pct:.1f}%)")

    # Number of purchases by gender
    if customer_column in df.columns:
        purchases = (
            df.groupby(gender_column)[customer_column]
            .nunique()
            .sort_values(ascending=False)
        )
        print(f"\n   • Purchases by gender:")
        for gender, count in purchases.items():
            pct = count / purchases.sum() * 100
            print(f"      - {gender}: {count:,} ({pct:.1f}%)")

    print("\n✅ Analysis complete")

    return {
        "by_gender": by_gender,
        "total": total,
    }

def analyze_sales_by_segment(
    df: pd.DataFrame,
    segment_column: str = "CL_SEG",
    quantity_column: str = "QUANTITY",
) -> dict:
    """
    Analyze sales by customer segment.

    Args:
        df: DataFrame with sales data.
        segment_column: Name of the segment column.
        quantity_column: Name of the quantity column.

    Returns:
        Dictionary with segment data.
    """
    print("\n📊 Analyzing sales by segment...")

    required = [segment_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}
    
    by_seg = (
        df.groupby(segment_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    total = by_seg.sum()

    print(f"\n   • Quantity by segment:")
    for segment, qty in by_seg.items():
        pct = qty / total * 100
        print(f"      - {segment}: {qty:,} ({pct:.1f}%)")

    print("\n✅ Analysis complete")

    return {
        "by_segment": by_seg,
        "total": total,
    }

def plot_sales_by_month(
    df: pd.DataFrame,
    month_column: str = "MONTH",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_sazonalidade.png",
) -> None:
    """
    Plot sales by month as a bar chart (seasonality).

    Highlights the best month (red) and worst month (orange).

    Args:
        df: DataFrame with sales data.
        month_column: Name of the month column.
        quantity_column: Name of the quantity column.
        output_dir: Directory to save the chart.
        filename: Output filename.

    Returns:
        None. Saves the chart to disk.
    """
    print(f"\n📊 Plotting sales by month...")

    required = [month_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    # Group by month
    by_month = df.groupby(month_column)[quantity_column].sum().sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))

    # Colors: default for all, red for best, orange for worst
    colors = ["skyblue"] * len(by_month)
    best_idx = by_month.idxmax() - 1
    worst_idx = by_month.idxmin() - 1
    colors[best_idx] = "crimson"
    colors[worst_idx] = "orange"

    bars = ax.bar(by_month.index, by_month.values, color=colors, edgecolor="navy")

    # Labels
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([MONTH_NAMES_PT[m] for m in range(1, 13)])
    ax.set_xlabel("Mês", fontsize=12)
    ax.set_ylabel("Quantidade Vendida", fontsize=12)
    ax.set_title("Vendas por Mês (Sazonalidade)", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_top_products(
    df: pd.DataFrame,
    product_column: str = "PR_NOME",
    quantity_column: str = "QUANTITY",
    top_n: int = 10,
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_top_produtos.png",
) -> None:
    """
    Plot top N products as a horizontal bar chart.

    Args:
        df: DataFrame with sales data.
        product_column: Name of the product column.
        quantity_column: Name of the quantity column.
        top_n: Number of top products to show.
        output_dir: Directory to save the chart.
        filename: Output filename.

    Returns:
        None. Saves the chart to disk.
    """
    print(f"\n📊 Plotting top {top_n} products...")

    required = [product_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    top = (
        df.groupby(product_column)[quantity_column]
        .sum()
        .nlargest(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.barh(top.index, top.values, color="steelblue", edgecolor="navy")

    ax.set_xlabel("Quantidade Vendida", fontsize=12)
    ax.set_ylabel("Produto", fontsize=12)
    ax.set_title(f"Top {top_n} Produtos Mais Vendidos", fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f" {int(width):,}",
            ha="left",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_top_categories(
    df: pd.DataFrame,
    category_column: str = "PR_CAT",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_categorias.png",
) -> None:
    """
    Plot sales by category as a bar chart.

    Args:
        df: DataFrame with sales data.
        category_column: Name of the category column.
        quantity_column: Name of the quantity column.
        output_dir: Directory to save the chart.
        filename: Output filename.

    Returns:
        None. Saves the chart to disk.
    """
    print(f"\n📊 Plotting categories...")

    required = [category_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    by_cat = (
        df.groupby(category_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(by_cat.index, by_cat.values, color="mediumseagreen", edgecolor="darkgreen")

    ax.set_xlabel("Categoria", fontsize=12)
    ax.set_ylabel("Quantidade Vendida", fontsize=12)
    ax.set_title("Vendas por Categoria", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")

    # Value labels with percentage
    total = by_cat.sum()
    for bar in bars:
        height = bar.get_height()
        pct = height / total * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_sales_by_gender(
    df: pd.DataFrame,
    gender_column: str = "CL_GENERO",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_genero.png",
) -> None:
    """
    Plot sales by gender as a pie chart.

    Args:
        df: DataFrame with sales data.
        gender_column: Name of the gender column.
        quantity_column: Name of the quantity column.
        output_dir: Directory to save the chart.
        filename: Output filename.

    Returns:
        None. Saves the chart to disk.
    """
    print(f"\n📊 Plotting sales by gender...")

    required = [gender_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    by_gender = df.groupby(gender_column)[quantity_column].sum()

    # Map gender codes to labels
    gender_labels = {"F": "Feminino", "M": "Masculino"}
    labels = [gender_labels.get(g, g) for g in by_gender.index]

    fig, ax = plt.subplots(figsize=(8, 8))

    colors = ["#FF6B9D", "#4A90E2"]
    wedges, texts, autotexts = ax.pie(
        by_gender.values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        textprops={"fontsize": 12},
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )

    ax.set_title("Vendas por Gênero", fontsize=14, fontweight="bold")

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_sales_by_segment(
    df: pd.DataFrame,
    segment_column: str = "CL_SEG",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_segmento.png",
) -> None:
    """
    Plot sales by segment as a bar chart.

    Args:
        df: DataFrame with sales data.
        segment_column: Name of the segment column.
        quantity_column: Name of the quantity column.
        output_dir: Directory to save the chart.
        filename: Output filename.

    Returns:
        None. Saves the chart to disk.
    """
    print(f"\n📊 Plotting sales by segment...")

    required = [segment_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    by_seg = df.groupby(segment_column)[quantity_column].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["#E74C3C", "#F39C12", "#27AE60"]
    bars = ax.bar(by_seg.index, by_seg.values, color=colors[:len(by_seg)], edgecolor="black")

    ax.set_xlabel("Segmento", fontsize=12)
    ax.set_ylabel("Quantidade Vendida", fontsize=12)
    ax.set_title("Vendas por Segmento de Cliente", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    # Value labels with percentage
    total = by_seg.sum()
    for bar in bars:
        height = bar.get_height()
        pct = height / total * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_seasonality_heatmap(
    df: pd.DataFrame,
    year_column: str = "YEAR",
    month_column: str = "MONTH",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_heatmap_sazonalidade.png",
) -> None:
    """
    Plot a seasonality heatmap (year × month) using seaborn.

    Shows how sales vary across years and months in a single view.

    Args:
        df: DataFrame with sales data.
        year_column: Name of the year column.
        month_column: Name of the month column.
        quantity_column: Name of the quantity column.
        output_dir: Directory to save the chart.
        filename: Output filename.

    Returns:
        None. Saves the chart to disk.
    """
    print(f"\n📊 Plotting seasonality heatmap (seaborn)...")

    required = [year_column, month_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    # Pivot: rows = MONTH, columns = YEAR
    pivot = df.pivot_table(
        values=quantity_column,
        index=month_column,
        columns=year_column,
        aggfunc="sum",
    )

    # Rename index with month names
    pivot.index = [MONTH_NAMES_PT.get(m, m) for m in pivot.index]

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".0f",
        cmap="YlOrRd",
        linewidths=0.5,
        cbar_kws={"label": "Quantidade Vendida"},
        ax=ax,
    )

    ax.set_title(
        "Sazonalidade: Vendas por Mês e Ano",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Ano", fontsize=12)
    ax.set_ylabel("Mês", fontsize=12)

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def analyze_sales_by_year(
    df: pd.DataFrame,
    quantity_column: str = "QUANTITY",
    year_column: str = "YEAR",
) -> dict:
    """
    Analyze sales by year.

    Args:
        df: DataFrame with sales data.
        quantity_column: Name of the quantity column.
        year_column: Name of the year column.

    Returns:
        Dictionary with yearly sales data.
    """
    print("\n📅 Analyzing sales by year...")

    required = [year_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    by_year = (
        df.groupby(year_column)[quantity_column]
        .sum()
        .sort_index()
    )

    total = by_year.sum()
    best_year = by_year.idxmax()
    worst_year = by_year.idxmin()

    print(f"\n   • Sales by year:")
    for year, qty in by_year.items():
        pct = qty / total * 100
        print(f"      - {year}: {qty:,} ({pct:.1f}%)")

    print(f"\n   • 🏆 Best year: {best_year} ({by_year[best_year]:,})")
    print(f"   • 📉 Worst year: {worst_year} ({by_year[worst_year]:,})")
    print(f"   • Total: {total:,}")

    print("\n✅ Analysis complete")

    return {
        "by_year": by_year,
        "total": total,
        "best_year": best_year,
        "best_year_value": by_year[best_year],
        "worst_year": worst_year,
        "worst_year_value": by_year[worst_year],
    }

def analyze_records_by_year(
    df: pd.DataFrame,
    year_column: str = "YEAR",
) -> dict:
    """
    Count records per year to check data coverage.

    Args:
        df: DataFrame with sales data.
        year_column: Name of the year column.

    Returns:
        Dictionary with record counts per year.
    """
    print("\n📅 Analyzing data coverage by year...")

    required = [year_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}
    
    counts = df[year_column].value_counts().sort_index()

    total = counts.sum()

    print(f"\n   • Records per year:")
    for year, count in counts.items():
        pct = count / total * 100
        print(f"      - {year}: {count:,} ({pct:.1f}%)")

    # Verdict
    print()
    min_count = counts.min()
    max_count = counts.max()
    ratio = min_count / max_count

    if ratio > 0.7:
        print("   ✅ Data is well distributed across years")
        coverage = "balanced"
    elif ratio > 0.3:
        print("   🟡 Some years have fewer records")
        coverage = "moderate"
    else:
        print("   ⚠️  Data is unevenly distributed")
        coverage = "uneven"

    print("\n✅ Analysis complete")

    return {
        "counts": counts,
        "coverage": coverage,
        "min_year": counts.idxmin(),
        "max_year": counts.idxmax(),
    }

def analyze_products_by_gender(
    df: pd.DataFrame,
    gender_column: str = "CL_GENERO",
    product_column: str = "PR_NOME",
    quantity_column: str = "QUANTITY",
    top_n: int = 5,
) -> dict:
    """
    Analyze top products bought by each gender.

    Args:
        df: DataFrame with sales data.
        gender_column: Name of the gender column.
        product_column: Name of the product column.
        quantity_column: Name of the quantity column.
        top_n: Number of top products per gender.

    Returns:
        Dictionary with top products per gender.
    """
    print(f"\n🛍️  Analyzing top {top_n} products by gender...")

    required = [gender_column, product_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}
    results = {}

    for gender in df[gender_column].unique():
        print(f"\n   • Top {top_n} products for {gender}:")

        top = (
            df[df[gender_column] == gender]
            .groupby(product_column)[quantity_column]
            .sum()
            .nlargest(top_n)
        )

        for i, (product, qty) in enumerate(top.items(), 1):
            print(f"      {i}. {product}: {qty:,}")

        results[gender] = top

    print("\n✅ Analysis complete")

    return results

def analyze_product_concentration(
    df: pd.DataFrame,
    product_name: str,
    product_column: str = "PR_NOME",
    quantity_column: str = "QUANTITY",
    customer_column: str = "CL_ID",
    purchase_column: str = "CO_ID",
    top_n: int = 5,
) -> dict:
    """
    Analyze whether a product is sold to many customers or concentrated in a few.

    Args:
        df: DataFrame with sales data.
        product_name: Name of the product to analyze.
        product_column: Name of the product column.
        quantity_column: Name of the quantity column.
        customer_column: Name of the customer ID column.
        purchase_column: Name of the purchase ID column.
        top_n: Number of top customers to show.

    Returns:
        Dictionary with concentration analysis.
    """
    print(f"\n🔬 Analyzing concentration of '{product_name}'...")

    # Filter only this product
    product_df = df[df[product_column] == product_name]

    if len(product_df) == 0:
        print(f"   ⚠️  Product '{product_name}' not found. Skipping.")
        return {}

    # Counts
    total_quantity = product_df[quantity_column].sum()
    unique_customers = product_df[customer_column].nunique()
    unique_purchases = product_df[purchase_column].nunique()

    print(f"\n   • Total quantity: {total_quantity:,}")
    print(f"   • Unique customers: {unique_customers:,}")
    print(f"   • Unique purchases: {unique_purchases:,}")

    # Average quantity per customer
    if unique_customers > 0:
        avg_per_customer = total_quantity / unique_customers
        print(f"   • Average quantity per customer: {avg_per_customer:.2f}")

    # Concentration: top N customers
    by_customer = (
        product_df.groupby(customer_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    top_n_qty = by_customer.head(top_n).sum()
    top_n_pct = top_n_qty / total_quantity * 100

    print(f"\n   • Top {top_n} customers:")
    for i, (cust, qty) in enumerate(by_customer.head(top_n).items(), 1):
        pct = qty / total_quantity * 100
        print(f"      {i}. Customer {cust}: {qty:,} ({pct:.2f}%)")

    print(f"\n   • Top {top_n} customers represent {top_n_pct:.1f}% of total")

    # Verdict
    print()
    if top_n_pct > 50:
        print(f"   ⚠️  Concentrated: a few customers dominate")
        concentration = "concentrated"
    elif top_n_pct > 25:
        print(f"   🟡 Moderately distributed")
        concentration = "moderate"
    else:
        print(f"   ✅ Well distributed across customers")
        concentration = "distributed"

    print("\n✅ Analysis complete")

    return {
        "total_quantity": total_quantity,
        "unique_customers": unique_customers,
        "unique_purchases": unique_purchases,
        "top_customers": by_customer.head(top_n),
        "top_n_pct": top_n_pct,
        "concentration": concentration,
    }

def analyze_purchase_size(
    df: pd.DataFrame,
    purchase_column: str = "CO_ID",
    quantity_column: str = "QUANTITY",
) -> dict:
    """
    Analyze purchase size (items per purchase).

    Args:
        df: DataFrame with sales data.
        purchase_column: Name of the purchase ID column.
        quantity_column: Name of the quantity column.

    Returns:
        Dictionary with purchase size stats.
    """
    print("\n🛒 Analyzing purchase size...")

    # Items per purchase
    items_per_purchase = df.groupby(purchase_column)[quantity_column].sum()

    total_items = items_per_purchase.sum()
    total_purchases = len(items_per_purchase)
    avg_items = items_per_purchase.mean()
    median_items = items_per_purchase.median()
    max_items = items_per_purchase.max()
    min_items = items_per_purchase.min()

    print(f"\n   • Total items: {total_items:,}")
    print(f"   • Total purchases: {total_purchases:,}")
    print(f"   • Average items per purchase: {avg_items:.2f}")
    print(f"   • Median items per purchase: {median_items:.0f}")
    print(f"   • Max items in one purchase: {max_items:,}")
    print(f"   • Min items in one purchase: {min_items:,}")

    # Distribution by ranges
    print(f"\n   • Distribution by ranges:")
    ranges = [0, 5, 10, 20, 50, 100, float("inf")]
    labels = ["1-5", "6-10", "11-20", "21-50", "51-100", "100+"]

    for i, label in enumerate(labels):
        count = len(items_per_purchase[
            (items_per_purchase > ranges[i]) & 
            (items_per_purchase <= ranges[i + 1])
        ])
        if count > 0:
            pct = count / total_purchases * 100
            print(f"      - {label} items: {count:,} purchases ({pct:.1f}%)")

    print("\n✅ Analysis complete")

    return {
        "total_items": total_items,
        "total_purchases": total_purchases,
        "avg_items": avg_items,
        "median_items": median_items,
        "max_items": max_items,
        "min_items": min_items,
    }

def analyze_children(
    df: pd.DataFrame,
    children_column: str = "CL_FHL",
) -> dict:
    """Analyze children count statistics."""
    print("\n👨‍👩‍👧  Analyzing number of children (CL_FHL)...")

    required = [children_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    col = df[children_column]

    print(f"\n   • Statistics:")
    print(f"      - Mean:     {col.mean():.2f}")
    print(f"      - Median:   {col.median():.0f}")
    print(f"      - Mode:     {col.mode()[0]}")
    print(f"      - Std:      {col.std():.2f}")
    print(f"      - Max:      {col.max()}")
    print(f"      - Min:      {col.min()}")
    print(f"      - Count:    {col.count():,}")

    print(f"\n   • Quartiles:")
    print(f"      - 25%: {col.quantile(0.25):.0f}")
    print(f"      - 50%: {col.quantile(0.50):.0f}")
    print(f"      - 75%: {col.quantile(0.75):.0f}")

    print(f"\n   • Distribution:")
    dist = col.value_counts().sort_index()
    for value, count in dist.items():
        pct = count / len(df) * 100
        print(f"      - {value} children: {count:,} ({pct:.1f}%)")

    print("\n✅ Analysis complete")

    return {
        "mean": col.mean(),
        "median": col.median(),
        "mode": col.mode()[0],
        "std": col.std(),
        "max": col.max(),
        "min": col.min(),
        "count": col.count(),
        "q1": col.quantile(0.25),
        "q2": col.quantile(0.50),
        "q3": col.quantile(0.75),
    }

def analyze_sales_by_weekday(
    df: pd.DataFrame,
    weekday_column: str = "WEEKDAY",
    quantity_column: str = "QUANTITY",
) -> dict:
    """Analyze sales by day of week."""
    print("\n📆 Analyzing sales by day of week...")

    required = [weekday_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}
    
    weekday_names = {
        0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
        4: "Sexta", 5: "Sábado", 6: "Domingo",
    }

    by_weekday = (
        df.groupby(weekday_column)[quantity_column]
        .sum()
        .reindex(range(7), fill_value=0)
    )

    total = by_weekday.sum()
    best_day = by_weekday.idxmax()
    worst_day = by_weekday.idxmin()

    print(f"\n   • Sales by weekday:")
    for day, qty in by_weekday.items():
        name = weekday_names.get(day, str(day))
        pct = qty / total * 100 if total > 0 else 0
        print(f"      - {name}: {qty:,} ({pct:.1f}%)")

    print(f"\n   • 🏆 Best day: {weekday_names[best_day]} ({by_weekday[best_day]:,})")
    print(f"   • 📉 Worst day: {weekday_names[worst_day]} ({by_weekday[worst_day]:,})")
    print(f"   • Total: {total:,}")

    print("\n✅ Analysis complete")

    return {
        "by_weekday": by_weekday,
        "total": total,
        "best_day": best_day,
        "best_day_name": weekday_names[best_day],
        "best_day_value": by_weekday[best_day],
        "worst_day": worst_day,
        "worst_day_name": weekday_names[worst_day],
        "worst_day_value": by_weekday[worst_day],
    }

def plot_sales_by_weekday(
    df: pd.DataFrame,
    weekday_column: str = "WEEKDAY",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_dia_semana.png",
) -> None:
    """Plot sales by day of week as a bar chart."""
    print(f"\n📊 Plotting sales by weekday...")

    required = [weekday_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    weekday_names = {
        0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui",
        4: "Sex", 5: "Sáb", 6: "Dom",
    }

    by_weekday = (
        df.groupby(weekday_column)[quantity_column]
        .sum()
        .reindex(range(7), fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["skyblue"] * 7
    best_idx = int(by_weekday.idxmax())
    worst_idx = int(by_weekday.idxmin())
    colors[best_idx] = "crimson"
    colors[worst_idx] = "orange"

    bars = ax.bar(
        [weekday_names[d] for d in by_weekday.index],
        by_weekday.values,
        color=colors,
        edgecolor="navy",
    )

    ax.set_xlabel("Dia da Semana", fontsize=12)
    ax.set_ylabel("Quantidade Vendida", fontsize=12)
    ax.set_title("Vendas por Dia da Semana", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    total = by_weekday.sum()
    for bar in bars:
        height = bar.get_height()
        pct = height / total * 100 if total > 0 else 0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def analyze_customer_pareto(
    df: pd.DataFrame,
    customer_column: str = "CL_ID",
    quantity_column: str = "QUANTITY",
    pareto_threshold: float = 80.0,
) -> dict:
    """Analyze customer concentration using the Pareto principle.

    The Pareto principle (80/20 rule) states that roughly 80% of
    effects come from 20% of causes. In retail, this often means a
    small share of customers drives most of the sales volume.

    This function calculates what percentage of customers account
    for `pareto_threshold`% of total quantity sold."""
    print(f"\n📊 Analyzing customer Pareto ({pareto_threshold:.0f}/{100-pareto_threshold:.0f})...")

    required = [customer_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}
    by_customer = (
        df.groupby(customer_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    total_customers = len(by_customer)
    total_quantity = by_customer.sum()

    if total_quantity == 0:
        print("   ⚠️  No quantity to analyze.")
        return {}

    cumulative_qty = by_customer.cumsum()
    cumulative_pct = cumulative_qty / total_quantity * 100

    customers_to_threshold = (cumulative_pct <= pareto_threshold).sum() + 1
    customers_pct = customers_to_threshold / total_customers * 100

    print(f"\n   • Total customers: {total_customers:,}")
    print(f"   • Total quantity: {total_quantity:,}")
    print(f"\n   • {customers_to_threshold:,} customers ({customers_pct:.1f}%)")
    print(f"     account for {pareto_threshold:.0f}% of sales")

    print(f"\n   • Interpretation:")
    if customers_pct < 30:
        print(f"     ⚠️  Highly concentrated: few customers drive most sales")
        concentration = "high"
    elif customers_pct < 50:
        print(f"     🟡 Moderately concentrated")
        concentration = "moderate"
    else:
        print(f"     ✅ Well distributed across customers")
        concentration = "low"

    print(f"\n   • Top 10 customers:")
    top_10 = by_customer.head(10)
    for i, (cust, qty) in enumerate(top_10.items(), 1):
        pct = qty / total_quantity * 100
        print(f"      {i:2d}. Customer {cust}: {qty:,} ({pct:.2f}%)")

    print("\n✅ Analysis complete")

    return {
        "by_customer": by_customer,
        "cumulative_pct": cumulative_pct,
        "total_customers": total_customers,
        "total_quantity": total_quantity,
        "customers_to_threshold": customers_to_threshold,
        "customers_pct": customers_pct,
        "pareto_threshold": pareto_threshold,
        "concentration": concentration,
        "top_10": top_10,
    }

def plot_customer_pareto(
    df: pd.DataFrame,
    customer_column: str = "CL_ID",
    quantity_column: str = "QUANTITY",
    pareto_threshold: float = 80.0,
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_pareto_clientes.png",
) -> None:
    """Plot customer Pareto curve."""
    print(f"\n📊 Plotting customer Pareto curve...")

    required = [customer_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    by_customer = (
        df.groupby(customer_column)[quantity_column]
        .sum()
        .sort_values(ascending=False)
    )

    total_quantity = by_customer.sum()
    if total_quantity == 0:
        print("   ⚠️  No quantity to plot.")
        return

    cum_qty = by_customer.cumsum()
    cum_pct = cum_qty / total_quantity * 100
    x_pct = [(i + 1) / len(by_customer) * 100 for i in range(len(by_customer))]

    idx_threshold = (cum_pct <= pareto_threshold).sum()
    x_threshold = x_pct[idx_threshold] if idx_threshold < len(x_pct) else x_pct[-1]
    y_threshold = cum_pct.iloc[idx_threshold] if idx_threshold < len(cum_pct) else cum_pct.iloc[-1]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x_pct, cum_pct.values, color="steelblue", linewidth=2)

    ax.axhline(pareto_threshold, color="crimson", linestyle="--", alpha=0.7,
               label=f"{pareto_threshold:.0f}% das vendas")
    ax.axvline(x_threshold, color="crimson", linestyle="--", alpha=0.7,
               label=f"{x_threshold:.1f}% dos clientes")

    ax.scatter([x_threshold], [y_threshold], color="crimson", s=100, zorder=5)
    ax.annotate(
        f"{x_threshold:.1f}% dos clientes\n= {pareto_threshold:.0f}% das vendas",
        xy=(x_threshold, y_threshold),
        xytext=(x_threshold + 15, y_threshold - 20),
        fontsize=10,
        arrowprops=dict(arrowstyle="->", color="crimson"),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="crimson"),
    )

    ax.set_xlabel("% dos Clientes (acumulado)", fontsize=12)
    ax.set_ylabel("% das Vendas (acumulado)", fontsize=12)
    ax.set_title("Curva de Pareto — Concentração de Clientes", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 105)

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def analyze_avg_ticket_by_group(
    df: pd.DataFrame,
    group_column: str,
    quantity_column: str = "QUANTITY",
    purchase_column: str = "CO_ID",
) -> dict:
    """Analyze average ticket (items per purchase) by a group."""
    print(f"\n🎟️  Analyzing average ticket by '{group_column}'...")

    required = [group_column, quantity_column, purchase_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    items_per_purchase = (
        df.groupby([group_column, purchase_column])[quantity_column]
        .sum()
        .reset_index()
    )

    results = {}

    print(f"\n   • Average ticket by {group_column}:")
    for group in sorted(items_per_purchase[group_column].unique()):
        group_df = items_per_purchase[items_per_purchase[group_column] == group]
        ticket = group_df[quantity_column]

        total_qty = ticket.sum()
        n_purchases = len(ticket)
        avg_ticket = ticket.mean()
        median_ticket = ticket.median()
        max_ticket = ticket.max()

        results[group] = {
            "total_quantity": total_qty,
            "n_purchases": n_purchases,
            "avg_ticket": avg_ticket,
            "median_ticket": median_ticket,
            "max_ticket": max_ticket,
        }

        print(f"\n      - {group}:")
        print(f"          • Total quantity: {total_qty:,}")
        print(f"          • Purchases: {n_purchases:,}")
        print(f"          • Average ticket: {avg_ticket:.2f}")
        print(f"          • Median ticket: {median_ticket:.0f}")
        print(f"          • Max ticket: {max_ticket:,}")

    if results:
        best_group = max(results, key=lambda g: results[g]["avg_ticket"])
        print(f"\n   • 🏆 Highest average ticket: {best_group} "
              f"({results[best_group]['avg_ticket']:.2f})")

    print("\n✅ Analysis complete")

    return {
        "by_group": results,
        "group_column": group_column,
    }

def analyze_category_by_segment(
    df: pd.DataFrame,
    category_column: str = "PR_CAT",
    segment_column: str = "CL_SEG",
    quantity_column: str = "QUANTITY",
) -> dict:
    """Analyze quantity of each category by customer segment (cross-tab)."""
    print(f"\n📊 Analyzing '{category_column}' × '{segment_column}'...")

    required = [category_column, segment_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    pivot = df.pivot_table(
        values=quantity_column,
        index=category_column,
        columns=segment_column,
        aggfunc="sum",
        fill_value=0,
    )

    # Add total row/column for reading
    pivot["TOTAL"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=False)

    print(f"\n   • Quantity by category × segment:")
    print(textwrap.indent(pivot.to_string(), "      "))

    # Segment with highest overall demand
    segment_totals = pivot.drop(columns="TOTAL").sum()
    top_segment = segment_totals.idxmax()

    print(f"\n   • 🏆 Top segment overall: {top_segment} "
          f"({segment_totals[top_segment]:,})")

    print("\n✅ Analysis complete")

    return {
        "pivot": pivot,
        "segment_totals": segment_totals,
        "top_segment": top_segment,
    }

def plot_heatmap_category_segment(
    df: pd.DataFrame,
    category_column: str = "PR_CAT",
    segment_column: str = "CL_SEG",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_heatmap_categoria_segmento.png",
) -> None:
    """Plot heatmap crossing category and segment."""
    print(f"\n📊 Plotting heatmap '{category_column}' × '{segment_column}'...")

    required = [category_column, segment_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    pivot = df.pivot_table(
        values=quantity_column,
        index=category_column,
        columns=segment_column,
        aggfunc="sum",
        fill_value=0,
    )
    pivot = pivot.sort_values(by=pivot.columns[0], ascending=False)

    fig, ax = plt.subplots(figsize=(10, max(6, len(pivot) * 0.5)))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".0f",
        cmap="YlGnBu",
        linewidths=0.5,
        cbar_kws={"label": "Quantidade Vendida"},
        ax=ax,
    )

    ax.set_title(
        f"Vendas por Categoria × Segmento",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Segmento", fontsize=12)
    ax.set_ylabel("Categoria", fontsize=12)

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_sales_by_year(
    df: pd.DataFrame,
    year_column: str = "YEAR",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_ano.png",
) -> None:
    """Plot sales by year as a bar chart."""
    print(f"\n📊 Plotting sales by year...")

    required = [year_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    by_year = df.groupby(year_column)[quantity_column].sum().sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        [str(y) for y in by_year.index],
        by_year.values,
        color="mediumpurple",
        edgecolor="navy",
    )

    ax.set_xlabel("Ano", fontsize=12)
    ax.set_ylabel("Quantidade Vendida", fontsize=12)
    ax.set_title("Vendas por Ano", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    total = by_year.sum()
    for bar in bars:
        height = bar.get_height()
        pct = height / total * 100 if total > 0 else 0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_purchase_size(
    df: pd.DataFrame,
    purchase_column: str = "CO_ID",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_tamanho_compra.png",
) -> None:
    """Plot purchase size distribution as a bar chart."""
    print(f"\n📊 Plotting purchase size distribution...")

    required = [purchase_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    items_per_purchase = df.groupby(purchase_column)[quantity_column].sum()

    ranges = [0, 5, 10, 20, 50, 100, float("inf")]
    labels = ["1-5", "6-10", "11-20", "21-50", "51-100", "100+"]

    counts = []
    for i, _ in enumerate(labels):
        n = len(items_per_purchase[
            (items_per_purchase > ranges[i]) &
            (items_per_purchase <= ranges[i + 1])
        ])
        counts.append(n)

    total = sum(counts)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(labels, counts, color="coral", edgecolor="darkred")

    ax.set_xlabel("Itens por Compra", fontsize=12)
    ax.set_ylabel("Número de Compras", fontsize=12)
    ax.set_title("Distribuição do Tamanho das Compras", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        pct = height / total * 100 if total > 0 else 0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def plot_children_distribution(
    df: pd.DataFrame,
    children_column: str = "CL_FHL",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_filhos.png",
) -> None:
    """Plot distribution of children count per record."""
    print(f"\n📊 Plotting children distribution...")

    required = [children_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return

    dist = df[children_column].value_counts().sort_index()
    total = dist.sum()

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        [str(v) for v in dist.index],
        dist.values,
        color="plum",
        edgecolor="purple",
    )

    ax.set_xlabel("Número de Filhos", fontsize=12)
    ax.set_ylabel("Número de Registros", fontsize=12)
    ax.set_title("Distribuição do Número de Filhos", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        pct = height / total * 100 if total > 0 else 0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

def analyze_customer_scatter(
    df: pd.DataFrame,
    customer_column: str = "CL_ID",
    purchase_column: str = "CO_ID",
    quantity_column: str = "QUANTITY",
) -> dict:
    """
    Analyze relationship between purchase frequency and average ticket.

    Each customer is described by:
    - Frequency: number of unique purchases
    - Avg ticket: average items per purchase

    Args:
        df: DataFrame with sales data.
        customer_column: Name of the customer ID column.
        purchase_column: Name of the purchase ID column.
        quantity_column: Name of the quantity column.

    Returns:
        Dictionary with per-customer dataframe and quadrant stats.
    """
    print("\n🔵 Analyzing customer frequency × ticket...")

    required = [customer_column, purchase_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return {}

    # Items per purchase, per customer
    items_per_purchase = (
        df.groupby([customer_column, purchase_column])[quantity_column]
        .sum()
        .reset_index()
    )

    # Aggregate per customer
    per_customer = (
        items_per_purchase
        .groupby(customer_column)[quantity_column]
        .agg(frequency="count", total="sum", avg_ticket="mean")
        .reset_index()
    )

    # Medians (to draw quadrant lines)
    median_freq = per_customer["frequency"].median()
    median_ticket = per_customer["avg_ticket"].median()

    # Quadrants
    q1 = ((per_customer["frequency"] >= median_freq) &
          (per_customer["avg_ticket"] >= median_ticket)).sum()  # VIP
    q2 = ((per_customer["frequency"] >= median_freq) &
          (per_customer["avg_ticket"] < median_ticket)).sum()   # frequente baixo
    q3 = ((per_customer["frequency"] < median_freq) &
          (per_customer["avg_ticket"] >= median_ticket)).sum()  # ocasional alto
    q4 = ((per_customer["frequency"] < median_freq) &
          (per_customer["avg_ticket"] < median_ticket)).sum()   # esporádico

    total = len(per_customer)

    print(f"\n   • Customers: {total:,}")
    print(f"   • Median frequency: {median_freq:.0f} purchases")
    print(f"   • Median ticket: {median_ticket:.2f} items")
    print(f"\n   • Quadrants:")
    print(f"      - VIP (muitas + alto ticket): {q1:,} ({q1/total*100:.1f}%)")
    print(f"      - Frequente baixo ticket:     {q2:,} ({q2/total*100:.1f}%)")
    print(f"      - Ocasional alto ticket:      {q3:,} ({q3/total*100:.1f}%)")
    print(f"      - Esporádico:                 {q4:,} ({q4/total*100:.1f}%)")

    print("\n✅ Analysis complete")

    return {
        "per_customer": per_customer,
        "median_freq": median_freq,
        "median_ticket": median_ticket,
        "quadrants": {"vip": q1, "freq_low": q2, "occ_high": q3, "sporadic": q4},
        "total_customers": total,
    }

def plot_customer_scatter(
    df: pd.DataFrame,
    customer_column: str = "CL_ID",
    purchase_column: str = "CO_ID",
    quantity_column: str = "QUANTITY",
    output_dir: Path = OUTPUT_DIR,
    filename: str = "grafico_scatter_cliente.png",
) -> None:
    """Plot customer scatter: frequency vs average ticket."""
    print(f"\n📊 Plotting customer scatter...")

    required = [customer_column, purchase_column, quantity_column]
    if not all(c in df.columns for c in required):
        print(f"   ⚠️  Missing columns: {[c for c in required if c not in df.columns]}. Skipping.")
        return
    
    analysis = analyze_customer_scatter(df, customer_column, purchase_column, quantity_column)
    if not analysis:
        print("   ⚠️  No analysis data. Skipping.")
        return

    per_customer = analysis["per_customer"]
    median_freq = analysis["median_freq"]
    median_ticket = analysis["median_ticket"]

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.scatter(
        per_customer["frequency"],
        per_customer["avg_ticket"],
        alpha=0.6,
        s=30,
        color="steelblue",
        edgecolor="white",
        linewidth=0.5,
    )
    ax.axvline(median_freq, color="crimson", linestyle="--", alpha=0.6,
               label=f"Mediana frequência ({median_freq:.0f})")
    ax.axhline(median_ticket, color="crimson", linestyle="--", alpha=0.6,
               label=f"Mediana ticket ({median_ticket:.1f})")

    x_max = per_customer["frequency"].max() * 1.15
    y_max = per_customer["avg_ticket"].max() * 1.05

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)

    # Sup. dir. — VIP
    ax.text(x_max * 0.98, y_max * 0.98, "VIP\n(muitas + alto)",
            ha="right", va="top", fontsize=10, fontweight="bold",
            color="darkgreen",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.6))

    # Sup. esq. — Ocasional alto ticket
    ax.text(x_max * 0.02, y_max * 0.98, "Ocasional\nalto ticket",
            ha="left", va="top", fontsize=10, fontweight="bold",
            color="darkorange",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="navajowhite", alpha=0.6))

    # Inf. dir. — Frequente baixo ticket
    ax.text(x_max * 0.98, y_max * 0.02, "Frequente\nbaixo ticket",
            ha="right", va="bottom", fontsize=10, fontweight="bold",
            color="darkblue",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.6))

    # Inf. esq. — Esporádico
    ax.text(x_max * 0.02, y_max * 0.02, "Esporádico",
            ha="left", va="bottom", fontsize=10, fontweight="bold",
            color="gray",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.6))

    ax.set_xlabel("Frequência (número de compras)", fontsize=12)
    ax.set_ylabel("Ticket médio (itens por compra)", fontsize=12)
    ax.set_title("Clientes: Frequência vs Ticket Médio", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"   • Path: {(output_dir / filename).relative_to(BASE_DIR)}")
    print(f"   ✅ Chart saved")

# ==========================================
# ENTRY POINT
# ==========================================

def main() -> None:
    """Run the main analysis workflow."""

    # ==========================================
    # SETUP
    # =========================================
    setup_directories()

    # ==========================================
    # DATA LOADING & EXPLORATION
    # ==========================================
    # 1. Load data
    df = load_data(DATA_FILE)

    # 2. Explore initial structure
    explore_data(df)

    # 3. Remove completely empty columns
    df = remove_empty_columns(df)

    # ==========================================
    # MISSING VALUES
    # ==========================================
    # 4. Investigate missing values
    missing_report = investigate_missing_values(df)

    # 5. Get the list of markers found
    markers_found = list(missing_report["markers_found"].keys())

    if not markers_found:
        print("\n✅ No missing markers to handle. Skipping.")
        markers_found = ["#N/D"]   # default for downstream calls

    print(f"\n📌 Using markers: {markers_found}")

    # 6. Deep investigation of missing values
    investigation = investigate_missing_category(df, missing_markers=markers_found)
    analyze_missing_by_dimension(df, "DATA", missing_markers=markers_found)
    analyze_missing_by_dimension(df, "CO_ID", missing_markers=markers_found)
    analyze_missing_by_dimension(df, "CL_SEG", missing_markers=markers_found)
    product_analysis = analyze_missing_by_product(df, missing_markers=markers_found)

    # 7. Decide strategy and handle missing
    # For this challenge, always fill with "Sem Categoria" (as required)
    strategy = decide_missing_strategy(investigation, product_analysis, prefer_fill=True)
    df = handle_missing_category(df, strategy, missing_markers=markers_found, fallback_value="Sem Categoria")

    # 8. Handle remaining NaN values 
    df = handle_nan_values(df, strategy="auto", threshold=5.0)

    # 9. Handle remaining text markers 
    df = handle_text_markers(df, strategy="replace", markers=markers_found, fallback_value="Sem Categoria")

    # 10. Validate clean data
    validate_clean_data(df, raise_on_failure=True)

    # ==========================================
    # DATES
    # ==========================================
    # 11. Convert dates
    df = convert_dates(df)

    # 12. Validate dates
    date_validation = validate_dates(df)

    # 13. Handle invalid dates
    df = handle_invalid_dates(df, date_validation)

    # 14. Add date parts
    df = add_date_parts(df, parts=["year", "month", "weekday"])

    # ==========================================
    # DUPLICATES & QUANTITY
    # ==========================================
    # 15. Check duplicates
    original_count = len(df)
    duplicates_info = check_duplicates(df)

    # 16. Create QUANTITY column (if duplicates exist)
    if duplicates_info.get("key_duplicates", 0) > 0:
        df = create_quantity_column(df)
        validate_quantity(df, original_count=original_count)
    else:
        print("\n✅ No duplicates to group. Skipping QUANTITY creation.")

    # 17. Save processed data (final)
    save_data(df, PROCESSED_DIR / "varejo_final.csv", description="final data")

    # ==========================================
    # ANALYSIS
    # ==========================================

    # 18. Monthly seasonality
    monthly = analyze_sales_by_month(df)

    # 19. Yearly sales
    yearly = analyze_sales_by_year(df)

    # 20. Data coverage by year         
    coverage = analyze_records_by_year(df)

    # 21. Top products
    top_products = analyze_top_products(df)

    # 22. Top categories
    top_categories = analyze_top_categories(df)

    # 23. Sales by gender
    by_gender = analyze_sales_by_gender(df)

    # 24. Sales by segment
    by_segment = analyze_sales_by_segment(df)

    # 25. Top products per gender
    products_by_gender = analyze_products_by_gender(df)

    # 26. Concentration analysis for top product
    top_product_name = top_products["top_products"].index[0]
    concentration = analyze_product_concentration(df, top_product_name)

    # 27. Purchase size
    purchase_size = analyze_purchase_size(df)

    # 28. Children analysis
    children = analyze_children(df)

    # 29. Weekday analysis
    weekday = analyze_sales_by_weekday(df)

    # 30. Customer Pareto
    pareto = analyze_customer_pareto(df)

    # 31. Average ticket by segment and gender
    ticket_seg = analyze_avg_ticket_by_group(df, "CL_SEG")
    ticket_gen = analyze_avg_ticket_by_group(df, "CL_GENERO")

    # 32. Category × Segment cross-tab
    cat_seg = analyze_category_by_segment(df)

    # ==========================================
    # PLOTTING
    # ==========================================
    # 33. Monthly seasonality
    plot_sales_by_month(df)
    plot_seasonality_heatmap(df)

    # 34. Top products
    plot_top_products(df)

    # 35. Top categories
    plot_top_categories(df)

    # 36. Sales by gender
    plot_sales_by_gender(df)

    # 37. Sales by segment
    plot_sales_by_segment(df)

    # 38. Weekday
    plot_sales_by_weekday(df)

    # 39. Customer Pareto
    plot_customer_pareto(df)

    # 40. Category × Segment heatmap
    plot_heatmap_category_segment(df)

    # 41. Sales by year
    plot_sales_by_year(df)

    # 42. Purchase size
    plot_purchase_size(df)

    # 43. Children distribution
    plot_children_distribution(df)

    # 44. Scatter plot
    plot_customer_scatter(df)

    print("\n🎉 Analysis complete!")

    # ==========================================
    # CONCLUSIONS
    # ==========================================
    print("\n" + "="*60)
    print("📋 CONCLUSIONS")
    print("="*60)

    # Build yearly coverage text
    coverage_lines = "\n".join(
        f"        - {year}: {count:,}"
        for year, count in coverage["counts"].items()
    )
    
    # Determine coverage message based on analysis
    if coverage["coverage"] == "uneven":
        coverage_msg = f"{coverage['min_year']} has significantly fewer records"
    elif coverage["coverage"] == "moderate":
        coverage_msg = f"{coverage['min_year']} has fewer records"
    else:
        coverage_msg = "Data is well distributed across years"

    # Prepare gender products lists
    women_products = "\n".join(
        f"        {i}. {prod}"
        for i, prod in enumerate(products_by_gender["F"].index, 1)
    )
    men_products = "\n".join(
        f"        {i}. {prod}"
        for i, prod in enumerate(products_by_gender["M"].index, 1)
    )

    # Prepare purchase size text
    purchase_avg = purchase_size["avg_items"]
    purchase_median = purchase_size["median_items"]
    purchase_max = purchase_size["max_items"]

    # Prepare Pareto text (safe if analysis returned empty)
    if pareto:
        pareto_txt = (
            f"• Principle: ~80% of sales come from a minority of customers\n"
            f"    • In this dataset: {pareto['customers_pct']:.1f}% of customers "
            f"account for {pareto['pareto_threshold']:.0f}% of sales\n"
            f"    • Verdict: {pareto['concentration'].upper()}"
        )
    else:
        pareto_txt = (
            "• Principle: ~80% of sales come from a minority of customers\n"
            "    • In this dataset: not available\n"
            "    • Verdict: not available"
        )

    # ----- Weekday text -----
    if weekday:
        weekday_txt = (
            f"• Best day: {weekday['best_day_name']} ({weekday['best_day_value']:,} items)\n"
            f"    • Worst day: {weekday['worst_day_name']} ({weekday['worst_day_value']:,} items)\n"
            f"    • Insight: sales concentrate on specific days, allowing targeted "
            f"staffing and promotions"
        )
    else:
        weekday_txt = "• not available"

    # ----- Ticket by segment -----
    if ticket_seg and ticket_seg.get("by_group"):
        seg_data = ticket_seg["by_group"]
        best_seg_name = max(seg_data, key=lambda g: seg_data[g]["avg_ticket"])
        worst_seg_name = min(seg_data, key=lambda g: seg_data[g]["avg_ticket"])
        best_seg_value = seg_data[best_seg_name]["avg_ticket"]
        worst_seg_value = seg_data[worst_seg_name]["avg_ticket"]

        ticket_seg_txt = (
            f"• Highest ticket: {best_seg_name} ({best_seg_value:.2f} items)\n"
            f"    • Lowest ticket: {worst_seg_name} ({worst_seg_value:.2f} items)\n"
            f"    • Insight: segments buy different amounts per visit, even when "
            f"total volume is similar"
        )
    else:
        ticket_seg_txt = "• not available"

    # ----- Ticket by gender -----
    if ticket_gen and ticket_gen.get("by_group"):
        gen_data = ticket_gen["by_group"]
        best_gen_name = max(gen_data, key=lambda g: gen_data[g]["avg_ticket"])
        worst_gen_name = min(gen_data, key=lambda g: gen_data[g]["avg_ticket"])
        best_gen_value = gen_data[best_gen_name]["avg_ticket"]
        worst_gen_value = gen_data[worst_gen_name]["avg_ticket"]

        ticket_gen_txt = (
            f"• Highest ticket: {best_gen_name} ({best_gen_value:.2f} items)\n"
            f"    • Lowest ticket: {worst_gen_name} ({worst_gen_value:.2f} items)"
        )
    else:
        ticket_gen_txt = "• not available"

    # ----- Category × Segment -----
    if cat_seg:
        cat_seg_txt = (
            f"• Top segment overall: {cat_seg['top_segment']}\n"
            f"    • Insight: reveals which segments drive each category, enabling "
            f"targeted assortment decisions"
        )
    else:
        cat_seg_txt = "• not available"

    print(f"""
    🔍 MAIN INSIGHTS:
    =========================
    1. Top product: {top_products['top_products'].index[0]} ({top_products['top_products'].iloc[0]:,} units)
    2. Top category: {top_categories['by_category'].index[0]} ({top_categories['by_category'].iloc[0]:,} units)
    3. Best month: {monthly['best_month_name']} ({monthly['best_month_value']:,} units)
    4. Best year: {yearly['best_year']} ({yearly['best_year_value']:,} units)
    5. Main gender: {by_gender['by_gender'].index[0]} ({by_gender['by_gender'].iloc[0]:,} units)
    6. Main segment: {by_segment['by_segment'].index[0]} ({by_segment['by_segment'].iloc[0]:,} units)

    🛍️  GENDER PREFERENCES:
    =========================
    • Women (F) top products: \n{women_products}
    • Men (M) top products: \n{men_products}
    • Insight: Women prefer cleaning/children items, men prefer beverages/meat

    🛒 PURCHASE SIZE:
    =========================
    • Total purchases: {purchase_size['total_purchases']:,}
    • Average items per purchase: {purchase_avg:.2f}
    • Median items per purchase: {purchase_median:.0f}
    • Max items in one purchase: {purchase_max:,}

    📊 DATA QUALITY NOTES:
    =========================
    • The '#N/D' missing values were ALL from a single product (PR_ID = 107)
    • This product had no name and no category registered
    • It was filled with 'Sem Categoria' (0.44% of total records)
    ⚠️  RECOMMENDATION: Complete the registration of product 107 
    in the source database (needs name and category).

    📅 DATA COVERAGE BY YEAR:
    =========================
    • Records per year: \n{coverage_lines}
    • Verdict: {coverage['coverage'].upper()}
    • Note: {coverage_msg}

    🎯 PRODUCT CONCENTRATION:
    =========================
    Top product ({top_product_name}):
    • Sold to {concentration['unique_customers']:,} unique customers
    • Across {concentration['unique_purchases']:,} unique purchases
    • Top 5 customers represent {concentration['top_n_pct']:.1f}% of total
    • Verdict: {concentration['concentration'].upper()}

     📊 CUSTOMER PARETO (80/20):
    =========================
    {pareto_txt}

    📆 WEEKDAY PATTERN:
    =========================
    • Best day: {weekday['best_day_name']} ({weekday['best_day_value']:,} items)
    • Worst day: {weekday['worst_day_name']} ({weekday['worst_day_value']:,} items)
    • Insight: sales concentrate on specific days → staffing and
      promotions can be targeted to those days

    🎟️ TICKET BY SEGMENT:
    =========================
    • Highest average ticket: {best_seg_name} ({best_seg_value:.2f} items)
    • Lowest average ticket: {worst_seg_name} ({worst_seg_value:.2f} items)
    • Insight: segments differ in how much they buy per visit,
      even if they buy similar total volume

    🎟️ TICKET BY GENDER:
    =========================
    • Highest average ticket: {best_gen_name} ({best_gen_value:.2f} items)
    • Lowest average ticket: {worst_gen_name} ({worst_gen_value:.2f} items)

    🔀 CATEGORY × SEGMENT:
    =========================
    • Top segment overall: {cat_seg['top_segment']}
    • Insight: reveals which segments drive demand for each category,
      enabling targeted assortment decisions
    
    ⚠️  LIMITATIONS:
    =========================
    1. No price column → no revenue analysis
    2. QUANTITY was inferred from duplicates
    3. {coverage_msg}

    📌 RECOMMENDATIONS:
    =========================
    1. Get price data for financial analysis
    2. Validate duplicates with data source
    3. Investigate 2022 data gap
    """)

if __name__ == "__main__":
    run_with_log(main, OUTPUT_DIR / "run.log")