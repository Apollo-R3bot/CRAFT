from datetime import datetime
import getpass
import os
import json
import socket
import platform
import winreg
import requests

CLEAR_PERIOD = {
    0: 'Last hour / Last 15 minutes', 
    1: 'Last 24 hours', 
    2: 'Last 7 days', 
    3: 'Last 4 weeks',
    4: 'All time'
}


def download_profile_picture(url, save_folder, email):
    if not url:
        return ""

    try:
        os.makedirs(save_folder, exist_ok=True)
        safe_email = email.replace("@", "_").replace(".", "_")
        file_name = f"{safe_email}_profile.jpg"
        save_path = os.path.join(save_folder, file_name)

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)

            return save_path

    except Exception as e:
        print(f"Profile picture download error: {e}")

    return ""


def extract_signed_in_accounts(profile, username, output_folder):
    entries = []

    seen_emails = set()
    picture_folder = os.path.join(output_folder,"profile_pictures")

    for prefs_file in ("Preferences","Secure Preferences"):
        prefs_path = os.path.join(profile,prefs_file)
        if not os.path.isfile(prefs_path):
            continue

        try:
            with open(prefs_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)

            accounts = data.get("account_info", [])

            if not accounts:
                acc = (
                    data.get("google", {})
                    .get("services", {})
                    .get("last_account_info", {})
                )

                if acc:
                    accounts = [acc]

            for acc in accounts:
                email = acc.get("email", "")
                if not email:
                    continue

                if email in seen_emails:
                    continue

                seen_emails.add(email)
                full_name = (acc.get("full_name", "")or acc.get("name", ""))
                acct_id = (acc.get("account_id", "")or acc.get("id", ""))
                picture_url = acc.get("picture_url","")

                if not email:
                    continue

                local_picture_path = download_profile_picture(picture_url, picture_folder, email)

                entries.append({
                    "email": email,
                    "full_name": full_name,
                    "account_id": acct_id,
                    "picture_url": picture_url,
                    "local_picture_path": local_picture_path,
                    "source": prefs_file,
                    "profile_user": username
                })

            if accounts:
                break

        except Exception as e:
            print(f"Preferences parse error: {e}")

    local_state = os.path.join(
        os.path.dirname(profile),
        "Local State"
    )

    if os.path.isfile(local_state):
        try:
            with open(local_state,"r",encoding="utf-8",errors="replace") as f:
                data = json.load(f)

            info_cache = (data.get("profile", {}).get("info_cache", {}))

            for profile_name, info in info_cache.items():
                email = info.get("user_name","").strip()
                if not email:
                    continue

                if email in seen_emails:
                    continue

                seen_emails.add(email)
                full_name = info.get("gaia_name","")
                acct_id = info.get("gaia_id","")
                picture_url = info.get("last_downloaded_gaia_picture_url_with_size","")

                local_picture_path = (
                    download_profile_picture(picture_url,picture_folder,email)
                )

                entries.append({
                    "email": email,
                    "full_name": full_name,
                    "account_id": acct_id,
                    "picture_url": picture_url,
                    "local_picture_path": local_picture_path,
                    "source": "Local State",
                    "profile_user": username
                })

        except Exception as e:
            print(
                f"Local State parse error: {e}"
            )

    return entries

def get_windows_version_string():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )

        # product_name = winreg.QueryValueEx(key,"ProductName")[0]
        edition = winreg.QueryValueEx(key,"EditionID")[0]
        current_build = winreg.QueryValueEx(key,"CurrentBuild")[0]
        ubr = winreg.QueryValueEx(key,"UBR")[0]
        architecture = ("x64"if platform.machine().endswith("64")else "x86")

        return (
            # f"{product_name} "
            f"{edition} "
            f"{architecture} "
            f"(Build {current_build}.{ubr})"
        )

    except Exception:
        return "Unknown Windows Version"
    
def get_machine_info():
    return {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os_version": f"{platform.system()} {platform.release()} {get_windows_version_string()}"
    }

    
def extract_browser_info(browser_type, profile_path, output_folder, username, accounts_data=None):
    browser_info = {
        "browser_info": {
            "browser_type": browser_type.title(),
            "browser_version": "Unknown",
            "installed_date": "Unknown",
            "profile_user": username,
            "source": ""
        },
        "machine_info": get_machine_info(),
        "signed_in_accounts": accounts_data or []
    }

    try:
        # CHROME / EDGE / OPERA
        if browser_type.lower() in ["chrome", "edge", "opera"]:
            user_data_path = os.path.dirname(profile_path)

            local_state_path = os.path.join(
                user_data_path,
                "Local State"
            )

            if os.path.exists(local_state_path):
                with open(local_state_path,"r",encoding="utf-8",errors="replace") as f:
                    data = json.load(f)

                def find_version(json_data):
                    if isinstance(json_data, dict):
                        if "last_version" in json_data:
                            return json_data["last_version"]
                        for key, value in json_data.items():
                            result = find_version(value)
                            if result is not None:
                                return result
                    return None
                browser_version_raw = find_version(data)

                # Format the data cleanly into your required string format
                if isinstance(browser_version_raw, list):
                    browser_version = ".".join(str(num) for num in browser_version_raw)
                elif browser_version_raw is not None:
                    browser_version = str(browser_version_raw)
                else:
                    browser_version = "Unknown"

                # Installed Date (using file creation time)
                created_time = os.path.getctime(local_state_path)
                browser_info["browser_info"]["installed_date"] = datetime.fromtimestamp(
                    created_time
                ).strftime("%Y-%m-%d %H:%M:%S")

                browser_info["browser_info"]["browser_version"] = browser_version
                browser_info["browser_info"]["source"] = "Local State"
                browser_info["machine_info"] = get_machine_info()

            preferences_path = os.path.join(
                profile_path,
                "Preferences"
            )

            if os.path.exists(preferences_path):
                with open(preferences_path, "r", encoding="utf-8", errors="replace") as f:
                    prefs = json.load(f)

                time_period = (
                    prefs.get("browser", {})
                        .get("clear_data", {})
                        .get("time_period")
                )

                browser_info["browser_info"]["last_selected_clear_data_range"] = (
                    CLEAR_PERIOD.get(time_period, "Unknown")
                )

        # FIREFOX
        elif browser_type.lower() == "firefox":
            compatibility_path = os.path.join(
                profile_path,
                "compatibility.ini"
            )

            if os.path.exists(compatibility_path):
                with open(compatibility_path,"r",encoding="utf-8",errors="replace") as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if line.startswith("LastVersion="):
                        version_data = line.split("=", 1)[1]
                        browser_version = version_data.split("_")[0]
                        browser_info["browser_info"]["browser_version"] = browser_version

                    elif line.startswith("LastAppDir="):
                        browser_info["browser_info"]["install_path"] = line.split("=", 1)[1]

                created_time = os.path.getctime(compatibility_path)
                browser_info["browser_info"]["installed_date"] = (
                    datetime.fromtimestamp(created_time)
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                browser_info["browser_info"]["source"] = "compatibility.ini"
                browser_info["machine_info"] = get_machine_info()

        # SAVE JSON
        output_path = os.path.join(
            output_folder,
            "preferences.json"
        )

        with open(output_path,"w",encoding="utf-8") as f:
            json.dump(
                browser_info,
                f,
                indent=4,
                ensure_ascii=False
            )

        return browser_info

    except Exception as e:
        print(f"Browser info extraction error: {e}")
        return browser_info