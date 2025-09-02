import pandas as pd
import os
from datetime import datetime


STAŁY_PLIK = r"C:\Users\monst\Documents\Revolut_caly.xlsx"

def wczytaj_dane(filepath):
    if filepath.lower().endswith(".xlsx"):
        try:
            return pd.read_excel(filepath, sheet_name=0)
        except ImportError:
            print("❌ Brakuje biblioteki 'openpyxl'. Zainstaluj ją: pip install openpyxl")
            exit(1)
    elif filepath.lower().endswith(".csv"):
        return pd.read_csv(filepath)
    else:
        print("❌ Nieobsługiwany format pliku. Użyj .xlsx lub .csv")
        exit(1)


def summarize_expenses(od, do, filepath):
    print("\n🔄 Przetwarzanie danych...")

    df = wczytaj_dane(filepath)

    required_columns = {'Started Date', 'Amount', 'Description', 'State'}
    if not required_columns.issubset(set(df.columns)):
        print("❌ Plik nie zawiera wymaganych kolumn:", required_columns)
        return

    df['Started Date'] = pd.to_datetime(df['Started Date'], errors='coerce')
    df['Description'] = df['Description'].astype(str).str.strip().str.lower()

    od = pd.to_datetime(od)
    do = pd.to_datetime(do)

    filtered = df[
        (df['Started Date'] >= od) &
        (df['Started Date'] <= do) &
        (df['Amount'] < 0) &
        (df['State'].str.upper() == 'COMPLETED')
    ]

    if filtered.empty:
        print("ℹ️ Brak wydatków w podanym zakresie dat.")
        return

    # Grupowanie i liczenie transakcji
    summary = filtered.groupby('Description').agg(
        Total_Amount=('Amount', 'sum'),
        Count=('Amount', 'count')
    )

    total = summary['Total_Amount'].sum()

    # Obliczanie procentowego udziału
    summary['Procent'] = (summary['Total_Amount'] / total * 100).abs().round(2)

    # Sortowanie
    summary = summary.sort_values(by='Total_Amount')

    # Zapis do pliku
    os.makedirs("../../csv", exist_ok=True)
    output_file = f"csv/expenses_summary_{od.date()}_to_{do.date()}.csv"
    summary.to_csv(output_file)

    # Wyświetlenie w terminalu
    print("\n📊 PODSUMOWANIE WYDATKÓW")
    print(f"📅 Zakres: {od.date()} do {do.date()}")
    print(f"💰 Suma wszystkich wydatków: {total:.2f} PLN\n")

    for desc, row in summary.iterrows():
        print(f"🛒 {desc}: {row['Total_Amount']:.2f} PLN "
              f"({int(row['Count'])} transakcji, {row['Procent']}%)")

    print(f"\n✅ Zapisano plik: {output_file}")

def main_menu():
    print("=" * 40)
    print("💸 PODSUMOWANIE WYDATKÓW Z PLIKU REVOLUT")
    print("=" * 40)

    # Nie pytamy o plik – używamy STAŁEJ ŚCIEŻKI
    print(f"📂 Plik źródłowy: {STAŁY_PLIK}")

    od = input("🗓 Podaj datę początkową (YYYY-MM-DD): ").strip()
    do = input("🗓 Podaj datę końcową (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(od, "%Y-%m-%d")
        datetime.strptime(do, "%Y-%m-%d")
    except ValueError:
        print("❌ Nieprawidłowy format daty. Użyj: YYYY-MM-DD")
        return

    summarize_expenses(od, do, STAŁY_PLIK)

if __name__ == "__main__":
    main_menu()
