import gspread


def validate_sheet(gsheet_url, sheet_name, doc=0):
    
    # the credentials should be in the   `%APPDATA%\\Roaming\gspread\credentials.json`
    gc = gspread.oauth()

    try:

        sh = gc.open_by_url(gsheet_url)

        worksheet = sh.worksheet(sheet_name)
        if doc == 1:
            if 'Project Code' not in worksheet.row_values(1) or 'Title' not in worksheet.row_values(1) or 'Team Member Name' not in worksheet.row_values(1) or 'Roll Number' not in worksheet.row_values(1):
                return False, "FORMAT_ERROR"
            return True, "SUCCESS"
        else:
            if str(worksheet.row_values(1)[0]).lower() == "name" and "email" in str(worksheet.row_values(1)[1]).lower():
                last_three_cols = worksheet.col_values(1)[-5:]
                if "Total Completed" in last_three_cols and "Total % Completed" in last_three_cols and "Total Pending" in last_three_cols:

                    return True, "SUCCESS"

                return False, "FORMAT_ERROR"

        return False, "FORMAT_ERROR"

    except Exception as e:
        if len(e.args)>=2:
            d = e.args[0]
        else:
            return False,"Invalid_URL"
        if "status" in d:
            return False, d["status"]
        else:
            return False, f"{sheet_name}_SHEET_NOT_PRESENT"
    return d


if __name__ == "__main__":
    
    
    url = "https://docs.google.com/spreadsheets/d/1kAI4siNQ-0ApPxwydfdeNpdWkrUKElS9R25T87dN_u0/edit#gid=747949193"

    url = "https://drive.google.com/file/d/1rgzNz7PaIzvdg2ckWxZKWGp3yk9gz6E-/view?usp=drivesdk"

    print(validate_sheet(url, "ACF"))
