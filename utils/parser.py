import re
import zipfile
import pandas as pd
from io import TextIOWrapper

def parse_input_file(file):
    try:
        filename = getattr(file, 'name', None)

        # Read lines from .zip or .txt file
        if filename.endswith(".zip"):
            with zipfile.ZipFile(file, "r") as zip_ref:
                txt_files = [name for name in zip_ref.namelist() if name.endswith('.txt')]
                if not txt_files:
                    return pd.DataFrame()
                with zip_ref.open(txt_files[0]) as txt_file:
                    lines = TextIOWrapper(txt_file, encoding='utf-8').readlines()
        elif filename.endswith(".txt"):
            lines = file.read().decode('utf-8').splitlines()
        else:
            return pd.DataFrame()

        parsed = []
        current_message = ""
        current_sender = ""
        current_datetime = None

        for line in lines:
            if " - " in line and ":" in line.split(" - ", 1)[1]:
                try:
                    # New message found
                    date_time_part, message_part = line.split(" - ", 1)
                    date_str, time_str = date_time_part.split(", ", 1)
                    sender, message = message_part.split(": ", 1)
                    dt = pd.to_datetime(f"{date_str} {time_str}", dayfirst=True, errors='coerce')
                    if pd.notnull(dt):
                        if current_message:
                            parsed.append((current_datetime, current_sender, current_message.strip()))
                        current_datetime = dt
                        current_sender = sender.strip()
                        current_message = message.strip()
                except:
                    continue
            else:
                # Continuation of the previous message
                current_message += "\n" + line.strip()

        # Append last message
        if current_message:
            parsed.append((current_datetime, current_sender, current_message.strip()))

        return pd.DataFrame(parsed, columns=["datetime", "sender", "content"])

    except Exception as e:
        print("Error parsing input file:", e)
        return pd.DataFrame()
