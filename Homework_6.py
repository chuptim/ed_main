from datetime import datetime

def split_data(date_str: str):
    *_, date_journal = date_str.strip(" !?.:").split('—', 1)
    date_journal = date_journal.strip(" !?.:")
    return date_journal


def parse_date(date_str: str):
    formats = [
        "%A, %B %d, %Y",
        "%A, %d.%m.%y",
        "%A, %d %B %Y"
    ]

    for format_date in formats:
        try:
            dt = datetime.strptime(date_str, format_date)
            return dt
        except ValueError:
            continue

    return None


def main():
    while (date_str := input("Введи название журнал и дату журнала через '—' (end - закончить): ")) != "end":
        date_str = split_data(date_str)
        date_dt = parse_date(date_str)
        if date_dt is None:
            print("Неправильный формат даты у журнала. Исправьте согласно регламенту")
            continue
        print(date_dt)
    else:
        print("Программа завершена")


if __name__ == "__main__":
    main()