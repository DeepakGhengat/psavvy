#!/usr/bin/env bash

dir="Tools"
double_check=false

# ARM Detection
ARCH=$(uname -m)
case $ARCH in
    amd64 | x86_64) IS_ARM="False" ;;
    arm64 | armv6l | aarch64) IS_ARM="True" ;;
esac


# Check if Tools directory exists, if not, create it
if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    printf "Created $dir directory.\n"
fi

# Cloning repositories into Tools directory
git clone https://github.com/bing0o/SubEnum.git "$dir/SubEnum"
git clone https://github.com/devanshbatham/ParamSpider.git "$dir/ParamSpider"
git clone https://github.com/Nemesis0U/Subhunter.git "$dir/Subhunter"
git clone https://github.com/0xInfection/xsrfprobe.git "$dir/xsrfprobe"
git clone https://github.com/projectdiscovery/nuclei-templates.git "$dir/nuclei-templates"
git clone https://github.com/defparam/smuggler.git "$dir/smuggler"
git clone https://github.com/commixproject/commix.git "$dir/commix"
git clone https://github.com/vladko312/SSTImap.git "$dir/SSTImap"
git clone https://github.com/hisxo/gitGraber.git "$dir/gitGraber"
git clone https://github.com/obheda12/GitDorker.git "$dir/GitDorker"
git clone https://github.com/r0075h3ll/Oralyzer.git "$dir/Oralyzer"
git clone https://github.com/hemantsolo/Host-Header-Injection-Vulnerability-Scanner.git "$dir/Host-Header-Injection-Vulnerability-Scanner"
git clone https://github.com/OCSAF/freevulnsearch.git "$dir/freevulnsearch"
git clone https://github.com/vulnersCom/nmap-vulners.git "$dir/nmap-vulners"
git clone https://github.com/scipag/vulscan.git "$dir/vulscan"
git clone https://github.com/sqlmapproject/sqlmap.git "$dir/sqlmap"
git clone https://github.com/s0md3v/XSStrike.git "$dir/XSStrike"
git clone https://github.com/OWASP/Nettacker.git "$dir/Nettacker"
git clone https://github.com/PentestPad/subzy.git "$dir/subzy"
git clone https://github.com/blechschmidt/massdns "$dir/massdns"
git clone https://github.com/tomnomnom/gf.git "$dir/gf"
git clone https://github.com/1ndianl33t/Gf-Patterns.git "$dir/Gf-Patterns"
git clone https://github.com/anmolksachan/CVESeeker.git  "$dir/CVESeeker"
git clone https://github.com/Th0h0/autossrf.git "$dir/autossrf"
wget https://github.com/junnlikestea/bulkssrf/releases/download/0.1.2/bulkssrf-0.1.2-x86_64-unknown-linux-musl.tar.gz -P Tools/
wget https://github.com/projectdiscovery/interactsh/releases/download/v1.2.0/interactsh-client_1.2.0_linux_386.zip -P Tools/



#!/bin/bash
#function to install the golang
function install_golang() {
    printf "Running: Installing Golang using apt\n\n"

    # Install Golang using apt
    sudo apt update
    sudo apt install -y golang-go
    if [ $? -ne 0 ]; then
        printf "Failed to install Golang using apt\n"
        return 1
    fi

    # Setting up environment variables
    if ! grep -q 'export GOPATH=$HOME/go' ~/.bashrc; then
        echo "export GOPATH=\$HOME/go" >> ~/.bashrc
    fi
    if ! grep -q 'export PATH=$PATH:/usr/local/go/bin' ~/.bashrc; then
        echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc
    fi
    if ! grep -q 'export PATH=$PATH:$GOPATH/bin' ~/.bashrc; then
        echo "export PATH=\$PATH:\$GOPATH/bin" >> ~/.bashrc
    fi

    # Source the updated .bashrc
    source ~/.bashrc

    # Validate the installation
    if go version &>/dev/null; then
        printf "Golang installed and configured successfully\n"
    else
        printf "Failed to install or configure Golang\n"
        return 1
    fi
}

# Call the function to install Golang
install_golang


# Install snapd if not present and then install dalfox and python3 env
function install_snap_and_dalfox() {
    printf "Running: Checking and Installing snapd and dalfox\n\n"
    if ! command -v snap &>/dev/null; then
        printf "snapd is not installed. Installing snapd...\n"
        if [[ -f /etc/debian_version ]]; then
            $SUDO apt update
            $SUDO apt install snapd -y
	          $SUDO  apt install python3 python3-venv -y
        elif [[ -f /etc/redhat-release ]]; then
            $SUDO yum install epel-release -y
            $SUDO yum install snapd -y
        elif [[ -f /etc/arch-release ]]; then
            $SUDO pacman -Sy snapd --noconfirm
        elif [[ "True" == "$IS_MAC" ]]; then
            brew install snap
        fi
        $SUDO systemctl enable --now snapd
        $SUDO ln -s /var/lib/snapd/snap /snap
    fi
    sudo snap install dalfox
    printf "Dalfox installed successfully\n"
}

if [[ $(id -u | grep -o '^0$') == "0" ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

install_apt() {
    $SUDO apt update -y
    $SUDO DEBIAN_FRONTEND="noninteractive" apt install python3 python3-pip python3-virtualenv build-essential gcc cmake ruby whois git curl libpcap-dev wget zip python3-dev pv dnsutils libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev nmap jq apt-transport-https lynx medusa xvfb libxml2-utils procps bsdmainutils libdata-hexdump-perl libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon-x11-0 libxcomposite-dev libxdamage1 libxrandr2 libgbm-dev libpangocairo-1.0-0 libasound2 -y
    curl https://sh.rustup.rs -sSf | sh -s -- -y >/dev/null 2>&1
    source "${HOME}/.cargo/env"
    cargo install ripgen
}

install_yum() {
    $SUDO yum groupinstall "Development Tools" -y
    $SUDO yum install python3 python3-pip gcc cmake ruby git curl libpcap-dev wget whois zip python3-devel pv bind-utils libopenssl-devel libffi-devel libxml2-devel libxslt-devel zlib-devel nmap jq lynx medusa xorg-x11-server-xvfb -y
    curl https://sh.rustup.rs -sSf | sh -s -- -y >/dev/null 2>&1
    source "${HOME}/.cargo/env"
    cargo install ripgen
}

install_pacman() {
    $SUDO pacman -Sy install python python-pip base-devel gcc cmake ruby git curl libpcap whois wget zip pv bind openssl libffi libxml2 libxslt zlib nmap jq lynx medusa xorg-server-xvfb -y
    curl https://sh.rustup.rs -sSf | sh -s -- -y >/dev/null 2>&1
    source "${HOME}/.cargo/env"
    cargo install ripgen
}

git config --global --unset http.proxy
git config --global --unset https.proxy



wget -N -c https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
rm -f get-pip.py

# Last check and tool setup
printf "Running: Setting up tools\n\n"
for repo in "${!repos[@]}"; do
    tool_dir="${dir}/${repo}"
    if [ -d "$tool_dir" ]; then
        cd "$tool_dir" || { echo "Failed to cd into $tool_dir"; exit 1; }
    fi
done

# Download and install shuffledns binary from release
function install_shuffledns() {
    printf "Running: Downloading and installing shuffledns\n\n"
    wget https://github.com/projectdiscovery/shuffledns/releases/download/v1.1.0/shuffledns_1.1.0_linux_386.zip -O /tmp/shuffledns.zip
    unzip /tmp/shuffledns.zip -d /tmp/
    $SUDO mv /tmp/shuffledns /usr/bin/shuffledns
    rm /tmp/shuffledns.zip
    echo "shuffledns installed to /usr/bin/shuffledns"
}

# Download and install anew binary from release
function install_anew() {
    printf "Running: Downloading and installing anew\n\n"
    wget https://github.com/tomnomnom/anew/releases/download/v0.1.1/anew-linux-386-0.1.1.tgz -O /tmp/anew.tgz
    tar -xzf /tmp/anew.tgz -C /tmp/
    $SUDO mv /tmp/anew /usr/bin/anew
    rm /tmp/anew.tgz
    echo "anew installed to /usr/bin/anew"
}

# Download and install dnsx binary from release
function install_dnsx() {
    printf "Running: Downloading and installing dnsx\n\n"
    wget https://github.com/projectdiscovery/dnsx/releases/download/v1.2.1/dnsx_1.2.1_linux_386.zip -O /tmp/dnsx.zip
    unzip /tmp/dnsx.zip -d /tmp/
    $SUDO mv /tmp/dnsx /usr/bin/dnsx
    rm /tmp/dnsx.zip
    echo "dnsx installed to /usr/bin/dnsx"
}

# Download and install httpx binary from release
function install_httpx() {
    printf "Running: Downloading and installing httpx\n\n"
    wget https://github.com/projectdiscovery/httpx/releases/download/v1.6.7/httpx_1.6.7_linux_386.zip -O /tmp/httpx.zip
    unzip /tmp/httpx.zip -d /tmp/
    $SUDO mv /tmp/httpx /usr/bin/httpx
    rm /tmp/httpx.zip
    echo "httpx installed to /usr/bin/httpx"
}

# Download and install gau binary from release
function install_gau() {
    printf "Running: Downloading and installing gau\n\n"
    wget https://github.com/lc/gau/releases/download/v2.2.3/gau_2.2.3_linux_386.tar.gz -O /tmp/gau.tar.gz
    tar -xzf /tmp/gau.tar.gz -C /tmp/
    $SUDO mv /tmp/gau /usr/bin/gau
    rm /tmp/gau.tar.gz
    echo "gau installed to /usr/bin/gau"
}

# Download and install nuclei binary from release
function install_nuclei() {
    printf "Running: Downloading and installing nuclei\n\n"
    wget https://github.com/projectdiscovery/nuclei/releases/download/v3.3.0/nuclei_3.3.0_linux_386.zip -O /tmp/nuclei.zip
    unzip /tmp/nuclei.zip -d /tmp/
    $SUDO mv /tmp/nuclei /usr/bin/nuclei
    rm /tmp/nuclei.zip
    echo "nuclei installed to /usr/bin/nuclei"
}

# Download and install ssrfuzz binary from release
function install_ssrfuzz() {
    printf "Running: Downloading and installing ssrfuzz\n\n"
    wget https://github.com/ryandamour/ssrfuzz/releases/download/v1.2/ssrfuzz_1.2_linux_386.tar.gz -O /tmp/ssrfuzz.tar.gz
    tar -xzf /tmp/ssrfuzz.tar.gz -C /tmp/
    $SUDO mv /tmp/ssrfuzz /usr/bin/ssrfuzz
    rm /tmp/ssrfuzz.tar.gz
    echo "ssrfuzz installed to /usr/bin/ssrfuzz"
}

# Download and install nosqli binary from release
function install_nosqli() {
    printf "Running: Downloading and installing nosqli\n\n"
    wget https://github.com/Charlie-belmer/nosqli/releases/download/v0.5.4/nosqli_linux_x86_v0.5.4 -O /tmp/nosqli
    chmod +x /tmp/nosqli
    $SUDO mv /tmp/nosqli /usr/bin/nosqli
    echo "nosqli installed to /usr/bin/nosqli"
}


#
# Download and install Gxss binary from release
function install_Gxss() {
    printf "Running: Downloading and installing Gxss\n\n"
    wget https://github.com/KathanP19/Gxss/releases/download/v4.1/Gxss_4.1_Linux_i386.tar.gz -O /tmp/gxss.tar.gz
    tar -xzf /tmp/gxss.tar.gz -C /tmp/
    $SUDO mv /tmp/Gxss /usr/bin/Gxss
    rm /tmp/gxss.tar.gz
    echo "Gxss installed to /usr/bin/Gxss"
}

## Function to install gf and Gf-Patterns
function install_gf_and_patterns() {
    # Install gf by Tomnomnom
    printf "Running: Installing gf by Tomnomnom\n\n"
    git clone https://github.com/tomnomnom/gf.git "${dir}/gf"
    cd "${dir}/gf"
    go build main.go
    mv main /usr/bin/gf
    echo "gf installed and moved to /usr/local/bin as 'gf'"

    # Install Gf-Patterns by 1ndianl33t
    printf "Running: Installing Gf-Patterns by 1ndianl33t\n\n"
    git clone https://github.com/1ndianl33t/Gf-Patterns.git
    sudo mkdir -p ~/.gf
    sudo mv Gf-Patterns/*.json ~/.gf
    echo "Gf-Patterns installed and JSON patterns moved to ~/.gf"
}

#Setting up Dependencies
# Setting up SubEnum
echo "Setting up SubEnum."
cd "Tools/SubEnum" || exit
chmod +x setup.sh
./setup.sh
cd ../../  # Move back to the Tools directory

# Setting up ParamSpider
echo "Setting up ParamSpider."
cd "Tools/ParamSpider" || exit
pip install .
cd ../../  # Move back to the Tools directory



# Setting up gitGraber
echo "Setting up gitGraber."
cd "Tools/gitGraber" || exit
pip3 install -r requirements.txt
cd ../../  # Move back to the Tools directory

# Setting up GitDorker
echo "Setting up GitDorker."
cd "Tools/GitDorker" || exit
pip3 install -r requirements.txt
cd ../../  # Move back to the Tools directory

# Setting up Oralyzer
echo "Setting up Oralyzer."
cd "Tools/Oralyzer" || exit
pip3 install -r requirements.txt
cd ../../  # Move back to the Tools directory

# Setting up Nettacker
echo "Setting up Nettacker."
cd "Tools/Nettacker" || exit
pip3 install -r requirements.txt
cd ../../# Move back to the Tools directory

# Setting up subzy
cd "Tools/subzy" || exit
go build
cd ../../   # Move back to the Tools directory

echo "Setting up SSTImap."
cd "Tools/autossrf" || exit
pip3 install -r requirements.txt
cd ../../


# Install xsrfprobe
echo "Setting up xsrfprobe."
pip3 install xsrfprobe



# Setting up SSTImap
echo "Setting up SSTImap."
cd "Tools/SSTImap" || exit
pip3 install -r requirements.txt
cd ../../  # Move back to the Tools directory


# Setting up XSStrike
echo "Setting up XSStrike."
cd "Tools/XSStrike" || exit
pip3 install -r requirements.txt
cd ../../  # Move back to the Tools directory

# Setting up massdns
echo "Setting up Massdns."
cd "Tools/massdns" || exit
make
cd bin/
mv massdns /usr/bin/massdns
cd ../../../  # Move back to the Tools directory
cd ../../../  # Move back to the Tools directory

echo "Setting up Subhunter."
cd "Tools/Subhunter" || exit
go build subhunter.go
cd ../../

echo "Setting up gf."
cd "Tools/gf" || exit
go build main.go
mv main /usr/bin/gf
cd ../../

echo "Setting up Gf-Patterns"
cd "Tools" || exit
mkdir -p ~/.gf
mv Gf-Patterns/*.json ~/.gf
cd ../../

echo "Setting up CVESeeker"
cd "Tools/CVESeeker" || exit
pip3 install -r requirements.txt
pip3 install colorama
cd ../../

echo "Setting up interactsh-client"
unzip interactsh-client_1.2.0_linux_386.zip
mv interactsh-client /usr/bin/interactsh-client
cd ../../



echo "Setting up Bulkssrf"
cd Tools/
tar -xvf bulkssrf-0.1.2-x86_64-unknown-linux-musl.tar.gz
mv bulkssrf-0.1.2-x86_64-unknown-linux-musl/bssrf /usr/bin/bssrf
rm -rf bulkssrf-0.1.2-x86_64-unknown-linux-musl.tar.gz
rm -rf bulkssrf-0.1.2-x86_64-unknown-linux-musl/


printf "\n\n#######################################################################\n"