import re
import zipfile
import pandas as pd

def parse_input_file(file):
    try:
        filename = getattr(file, 'name', '')

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

        # Normalize invisible characters (e.g. narrow no-break space)
        data = data.replace('\u202f', ' ').replace('\u200e', '')  # Also remove left-to-right marks

        # Split chat into lines
        lines = data.splitlines()

        # Regex pattern: supports 12-hour and 24-hour time, sender, and content
        pattern = re.compile(
            r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(?:\s?[apAP][mM])?)\s?-\s(.*?):\s(.*)$"
        )

        messages = []
        current_msg = {"date": "", "time": "", "sender": "", "content": ""}

        for line in lines:
            match = pattern.match(line)
            if match:
                # Save previous message before starting a new one
                if current_msg["content"]:
                    messages.append(current_msg.copy())

                current_msg["date"] = match.group(1)
                current_msg["time"] = match.group(2)
                current_msg["sender"] = match.group(3).strip()
                current_msg["content"] = match.group(4).strip()
            else:
                # Continuation of previous message
                current_msg["content"] += "\n" + line.strip()

        # Add the last message
        if current_msg["content"]:
            messages.append(current_msg.copy())

        # Build DataFrame
        parsed = []
        for msg in messages:
            dt = pd.to_datetime(f"{msg['date']} {msg['time']}", dayfirst=True, errors='coerce')
            if pd.notnull(dt):
                parsed.append((dt, msg["sender"], msg["content"]))

        return pd.DataFrame(parsed, columns=["datetime", "sender", "content"])

    except Exception as e:
        print("Error parsing input file:", e)
        return pd.DataFrame()
