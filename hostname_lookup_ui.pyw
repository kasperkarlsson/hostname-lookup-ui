import datetime
import html
import re
import requests
import urllib3

from appJar import gui
from subprocess import Popen

# Configuration
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Settings:
    VERSION = "0.2"
    TITLE = "Hostname Lookup GUI v{0}".format(VERSION)

    FILENAME_DEFAULT = "hosts_{}.html"
    REPORT_TEMPLATE_FILE = "resources/report_template.html"
    MAX_TITLE_LENGTH = 50
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"


class HostResult:
    def __init__(self):
        self.status_codes = {"http": "null", "https": "null"}
        self.resp_length = {"http": "null", "https": "null"}
        self.title = {"http": "", "https": ""}


def lookup_hostnames(hostnames: list, filename):
    with open(Settings.REPORT_TEMPLATE_FILE, "r") as in_file:
        report_template = in_file.read()
    with open(filename, "w") as f:
        try:
            f.write(report_template)
            len_hostnames = len(hostnames)
            title_regex = re.compile("<title>(.{0,1000})</title>", re.IGNORECASE)
            for i in range(len_hostnames):
                app.setLabel("Progress", "{0}/{1} ({2:.2%})".format(i+1, len_hostnames, (i+1)/len_hostnames))
                host = hostnames[i]
                print(f"{i+1}/{len_hostnames}", host, end="\t")
                result = HostResult()
                for protocol in ["http", "https"]:
                    try:
                        url = f"{protocol}://{host}/"
                        headers = {"User-Agent": Settings.USER_AGENT}
                        response = requests.get(url, headers=headers, timeout=0.5, verify=False)
                        result.status_codes[protocol] = str(response.status_code)
                        result.resp_length[protocol] = str(len(response.text))
                        # Extract title
                        title = title_regex.search(response.text)
                        if title:
                            title_decoded = html.unescape(title.group(1))
                            title_cut = title_decoded[:Settings.MAX_TITLE_LENGTH]
                            clean_title = title_cut\
                                .replace("\\", "\\\\")\
                                .replace("/", "\\/")\
                                .replace("'", "\\'")
                            result.title[protocol] = clean_title
                    except (requests.exceptions.Timeout,
                            requests.exceptions.ConnectionError,
                            requests.exceptions.TooManyRedirects):
                        pass
                    except Exception as e:
                        print(f"Uncaught exception: {type(e)} - {e}")
                print(f"http:[{result.status_codes['http']} {result.resp_length['http']}]\t"
                      f"https:[{result.status_codes['https']} {result.resp_length['https']}]\t"
                      f"title:['{result.title['http']}' / '{result.title['https']}']")
                f.write("<script>results.push({"
                        f"host:'{host}',"
                        f"http_code:{result.status_codes['http']},"
                        f"http_len:{result.resp_length['http']},"
                        f"https_code:{result.status_codes['https']},"
                        f"https_len:{result.resp_length['https']},"
                        f"http_title:'{result.title['http']}',"
                        f"https_title:'{result.title['https']}'"
                        "});</script>\n")
                f.flush()
        finally:
            f.write("</body>\n"
                    "</html>")


class DomainList:

    def __init__(self, raw_domain_list):
        self.domains = []
        for raw_domain in raw_domain_list:
            assert isinstance(raw_domain, str)
            # Perform some naive cleaning
            domain = raw_domain.lower().replace("https://", "").replace("http://", "")
            for comment_char in [" ", "\t", ":", "/", "?", "#"]:
                comment_index = domain.find(comment_char)
                if comment_index > -1:
                    domain = domain[:comment_index]

            if domain:
                self.domains.append(domain)


# Button handler
def press(button):
    if button == "Close":
        app.stop()
    elif button == "Show":
        Popen("explorer .")
    elif button == "Lookup domains":
        raw_domain_list = app.getTextArea("DomainList")
        domain_list = DomainList(raw_domain_list.splitlines())
        print("Domains:", domain_list.domains)
        filename = app.getEntry("Filename")
        if filename == "":
            filename = Settings.FILENAME_DEFAULT
        filename = filename.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        # Run lookup
        app.thread(lookup_hostnames, domain_list.domains, filename)
        app.setLabel("Status", f"Report filename: '{filename}'")
    else:
        print("Unknown button: '{0}'".format(button))


# Initialize GUI
app = gui(Settings.TITLE, "600x600")

# Create widgets
app.addLabel("title", Settings.TITLE, colspan=2)

app.addLabelEntry("Filename", colspan=2)
app.setEntryDefault("Filename", Settings.FILENAME_DEFAULT)

app.addLabel("Domains", colspan=2)
app.addScrolledTextArea("DomainList", colspan=2)
app.setInputFont(size=9, family="Lucida Console")

# All buttons map to the press function
app.addButtons(["Lookup domains", "Show", "Close"], press, colspan=2)

app.addLabel("Progress", colspan=2)
app.addLabel("Status", colspan=2)

# Start GUI
app.go()
