import re
import zipfile
import pandas as pd


def parse_input_file(file):
    try:
        filename = getattr(file, 'name', None)

        # ✅ Use filename directly
        if filename.endswith(".zip"):
            with zipfile.ZipFile(file, "r") as zip_ref:
                txt_files = [name for name in zip_ref.namelist() if name.endswith('.txt')]
                if txt_files:
                    data = zip_ref.read(txt_files[0]).decode('utf-8')
                else:
                    return pd.DataFrame()
        elif filename.endswith(".txt"):
            data = file.read().decode('utf-8')
        else:
            return pd.DataFrame()

        # ✅ Updated regex for your format: "DD/MM/YY, HH:MM - Sender: Message"
        pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.+)$'
        messages = re.findall(pattern, data, flags=re.MULTILINE)

        parsed_messages = []
        for date, time, sender, content in messages:
            try:
                dt = pd.to_datetime(f"{date} {time}", dayfirst=True, errors='coerce')
                if pd.notnull(dt):
                    parsed_messages.append((dt, sender.strip(), content.strip()))
            except:
                continue

        return pd.DataFrame(parsed_messages, columns=["datetime", "sender", "content"])

    except Exception as e:
        print("Error parsing input file:", e)
        return pd.DataFrame()
