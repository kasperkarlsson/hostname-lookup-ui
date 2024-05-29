# hostname-lookup-ui
Scan domain list for HTTP(S) responses with live results filtering, with a simple appJar UI.

Intended for evaluating a large number of domains and filtering out "uninteresting" results, like multiple domains showing the same error message, redirecting to the same IdP or similar.

# Usage
1. Run `hostname_lookup_ui.pyw`
2. Paste a list of domains and click `Lookup domains`. The script attempts to connect to the hosts via HTTP and HTTPS and automatically generates a report `hosts.html`.
3. Open `hosts.html` in your browser (this can be done while the script is running). Results can be filtered based on status code and response length.
4. New results can be loaded by refreshing the report in the browser. The filters will be kept.

# Filtering example
* To hide all results with response code `404`, click the value `404` for any domain in columns `HTTP Code` or `HTTPS Code`. This can also be done by entering the value `404` in the input field *Ignore status codes*.
