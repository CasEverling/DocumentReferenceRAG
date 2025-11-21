# local_run.py
from process_manual import process_manual

def main():
    manual_id = process_manual(
        pdf_path="documento_2.pdf",
        make="Ford",
        model="Crown Victoria",
        year=2010,
        police_or_civil="Police"
    )
    print(f"Manual processed. ID = {manual_id}")

if __name__ == "__main__":
    main()
