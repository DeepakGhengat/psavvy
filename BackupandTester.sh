#!/usr/bin/env bash
export DEBIAN_FRONTEND=noninteractive

# Set working directory to the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Define the Tools directory as a subdirectory in the script's location
dir="$SCRIPT_DIR/Tools"
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
    printf "Created %s directory.\n" "$dir"
fi

# Function to install Golang
install_golang() {
    printf "Running: Installing Golang using apt\n\n"
    sudo apt update
    sudo apt install -y golang-go
    if [ $? -ne 0 ]; then
        printf "Failed to install Golang using apt\n"
        return 1
    fi

    # Setting up environment variables in .bashrc
    if ! grep -q 'export GOPATH=$HOME/go' ~/.bashrc; then
        echo "export GOPATH=\$HOME/go" >> ~/.bashrc
    fi
    if ! grep -q 'export PATH=$PATH:/usr/local/go/bin' ~/.bashrc; then
        echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc
    fi
    if ! grep -q 'export PATH=$PATH:$GOPATH/bin' ~/.bashrc; then
        echo "export PATH=\$PATH:\$GOPATH/bin" >> ~/.bashrc
    fi

    source ~/.bashrc

    if go version &>/dev/null; then
        printf "Golang installed and configured successfully\n"
    else
        printf "Failed to install or configure Golang\n"
        return 1
    fi
}

install_golang

# Install snapd if not present and then install dalfox and python3 environment
install_snap_and_dalfox() {
    printf "Running: Checking and Installing snapd and dalfox\n\n"
    if ! command -v snap &>/dev/null; then
        printf "snapd is not installed. Installing snapd...\n"
        if [[ -f /etc/debian_version ]]; then
            sudo apt update
            sudo apt install -y snapd python3 python3-venv
        elif [[ -f /etc/redhat-release ]]; then
            sudo yum install -y epel-release
            sudo yum install -y snapd
        elif [[ -f /etc/arch-release ]]; then
            sudo pacman -Sy --noconfirm snapd
        elif [[ "True" == "$IS_MAC" ]]; then
            brew install snap
        fi
        sudo systemctl enable --now snapd
        sudo ln -s /var/lib/snapd/snap /snap
    fi
    sudo snap install dalfox
    printf "Dalfox installed successfully\n"
}

# Determine sudo usage
if [[ $(id -u) -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

install_apt() {
    $SUDO apt update -y
    $SUDO apt install -y python3 python3-pip python3-virtualenv build-essential gcc cmake ruby whois git curl libpcap-dev wget zip python3-dev pv dnsutils libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev nmap jq apt-transport-https lynx medusa xvfb libxml2-utils procps bsdmainutils libdata-hexdump-perl libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon-x11-0 libxcomposite-dev libxdamage1 libxrandr2 libgbm-dev libpangocairo-1.0-0 libasound2 -y
    curl https://sh.rustup.rs -sSf | sh -s -- -y >/dev/null 2>&1
    source "${HOME}/.cargo/env"
    cargo install ripgen
}

install_yum() {
    $SUDO yum groupinstall -y "Development Tools"
    $SUDO yum install -y python3 python3-pip gcc cmake ruby git curl libpcap-dev wget whois zip python3-devel pv bind-utils libopenssl-devel libffi-devel libxml2-devel libxslt-devel zlib-devel nmap jq lynx medusa xorg-x11-server-xvfb
    curl https://sh.rustup.rs -sSf | sh -s -- -y >/dev/null 2>&1
    source "${HOME}/.cargo/env"
    cargo install ripgen
}

install_pacman() {
    $SUDO pacman -Sy --noconfirm python python-pip base-devel gcc cmake ruby git curl libpcap whois wget zip pv bind openssl libffi libxml2 libxslt zlib nmap jq lynx medusa xorg-server-xvfb
    curl https://sh.rustup.rs -sSf | sh -s -- -y >/dev/null 2>&1
    source "${HOME}/.cargo/env"
    cargo install ripgen
}

git config --global --unset http.proxy
git config --global --unset https.proxy

# Install pip using get-pip.py
wget -N -c https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
rm -f get-pip.py

printf "Running: Setting up tools\n\n"

# Clone repositories into the Tools directory
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
git clone https://github.com/anmolksachan/CVESeeker.git "$dir/CVESeeker"
git clone https://github.com/Th0h0/autossrf.git "$dir/autossrf"
wget https://github.com/junnlikestea/bulkssrf/releases/download/0.1.2/bulkssrf-0.1.2-x86_64-unknown-linux-musl.tar.gz -P "$dir"
wget https://github.com/projectdiscovery/interactsh/releases/download/v1.2.0/interactsh-client_1.2.0_linux_386.zip -P "$dir"

# Setting up shuffledns
wget https://github.com/projectdiscovery/shuffledns/releases/download/v1.1.0/shuffledns_1.1.0_linux_386.zip -P "$dir"
echo "Setting up shuffledns"
unzip -o "$dir/shuffledns_1.1.0_linux_386.zip" -d "$dir"
sudo mv "$dir/shuffledns" /usr/bin/shuffledns
rm "$dir/shuffledns_1.1.0_linux_386.zip"

# Setting up anew
wget https://github.com/tomnomnom/anew/releases/download/v0.1.1/anew-linux-386-0.1.1.tgz -P "$dir"
echo "Setting up anew"
tar -xzf "$dir/anew-linux-386-0.1.1.tgz" -C "$dir"
sudo mv "$dir/anew" /usr/bin/anew
rm "$dir/anew-linux-386-0.1.1.tgz"

# Setting up dnsx
wget https://github.com/projectdiscovery/dnsx/releases/download/v1.2.1/dnsx_1.2.1_linux_386.zip -P "$dir"
echo "Setting up dnsx"
unzip -o "$dir/dnsx_1.2.1_linux_386.zip" -d "$dir"
sudo mv "$dir/dnsx" /usr/bin/dnsx
rm "$dir/dnsx_1.2.1_linux_386.zip"

# Setting up httpx
wget https://github.com/projectdiscovery/httpx/releases/download/v1.6.7/httpx_1.6.7_linux_386.zip -P "$dir"
echo "Setting up httpx"
unzip -o "$dir/httpx_1.6.7_linux_386.zip" -d "$dir"
sudo mv "$dir/httpx" /usr/bin/httpx
rm "$dir/httpx_1.6.7_linux_386.zip"

# Setting up gau
wget https://github.com/lc/gau/releases/download/v2.2.3/gau_2.2.3_linux_386.tar.gz -P "$dir"
echo "Setting up gau"
tar -xzf "$dir/gau_2.2.3_linux_386.tar.gz" -C "$dir"
sudo mv "$dir/gau" /usr/bin/gau
rm "$dir/gau_2.2.3_linux_386.tar.gz"

# Setting up nuclei
wget https://github.com/projectdiscovery/nuclei/releases/download/v3.3.0/nuclei_3.3.0_linux_386.zip -P "$dir"
echo "Setting up nuclei"
unzip -o "$dir/nuclei_3.3.0_linux_386.zip" -d "$dir"
sudo mv "$dir/nuclei" /usr/bin/nuclei
rm "$dir/nuclei_3.3.0_linux_386.zip"

# Setting up ssrfuzz
wget https://github.com/ryandamour/ssrfuzz/releases/download/v1.2/ssrfuzz_1.2_linux_386.tar.gz -P "$dir"
echo "Setting up ssrfuzz"
tar -xzf "$dir/ssrfuzz_1.2_linux_386.tar.gz" -C "$dir"
sudo mv "$dir/ssrfuzz" /usr/bin/ssrfuzz
rm "$dir/ssrfuzz_1.2_linux_386.tar.gz"

# Setting up nosqli
wget https://github.com/Charlie-belmer/nosqli/releases/download/v0.5.4/nosqli_linux_x86_v0.5.4 -P "$dir"
echo "Setting up nosqli"
chmod +x "$dir/nosqli_linux_x86_v0.5.4"
sudo mv "$dir/nosqli_linux_x86_v0.5.4" /usr/bin/nosqli
rm "$dir/nosqli_linux_x86_v0.5.4"

# Setting up Gxss
wget https://github.com/KathanP19/Gxss/releases/download/v4.1/Gxss_4.1_Linux_i386.tar.gz -P "$dir"
echo "Setting up Gxss"
tar -xzf "$dir/Gxss_4.1_Linux_i386.tar.gz" -C "$dir"
sudo mv "$dir/Gxss" /usr/bin/Gxss
rm "$dir/Gxss_4.1_Linux_i386.tar.gz"

# Setting up interactsh-client
wget https://github.com/projectdiscovery/interactsh/releases/download/v1.2.0/interactsh-client_1.2.0_linux_386.zip -P "$dir"
echo "Setting up interactsh-client"
if [ -f "$dir/interactsh-client_1.2.0_linux_386.zip" ]; then
    unzip -o "$dir/interactsh-client_1.2.0_linux_386.zip" -d "$dir"
    if [ -d "$dir/interactsh-client" ]; then
        sudo mv "$dir/interactsh-client" /usr/bin/interactsh-client
    else
        echo "Directory $dir/interactsh-client not found after unzip."
    fi
    rm "$dir/interactsh-client_1.2.0_linux_386.zip"
else
    echo "File $dir/interactsh-client_1.2.0_linux_386.zip not found. Skipping interactsh-client setup."
fi

# -------------------- Dependency Setups --------------------

# SubEnum
if [ -d "$dir/SubEnum" ]; then
    echo "Setting up SubEnum."
    cd "$dir/SubEnum" || { echo "Failed to cd into $dir/SubEnum"; exit 1; }
    chmod +x setup.sh
    ./setup.sh
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/SubEnum not found. Skipping SubEnum setup."
fi

# ParamSpider
if [ -d "$dir/ParamSpider" ]; then
    echo "Setting up ParamSpider."
    cd "$dir/ParamSpider" || { echo "Failed to cd into $dir/ParamSpider"; exit 1; }
    pip install --break-system-packages .
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/ParamSpider not found. Skipping ParamSpider setup."
fi

# gitGraber
if [ -d "$dir/gitGraber" ]; then
    echo "Setting up gitGraber."
    cd "$dir/gitGraber" || { echo "Failed to cd into $dir/gitGraber"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/gitGraber not found. Skipping gitGraber setup."
fi

# GitDorker
if [ -d "$dir/GitDorker" ]; then
    echo "Setting up GitDorker."
    cd "$dir/GitDorker" || { echo "Failed to cd into $dir/GitDorker"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/GitDorker not found. Skipping GitDorker setup."
fi

# Oralyzer
if [ -d "$dir/Oralyzer" ]; then
    echo "Setting up Oralyzer."
    cd "$dir/Oralyzer" || { echo "Failed to cd into $dir/Oralyzer"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/Oralyzer not found. Skipping Oralyzer setup."
fi

# Nettacker
if [ -d "$dir/Nettacker" ]; then
    echo "Setting up Nettacker."
    cd "$dir/Nettacker" || { echo "Failed to cd into $dir/Nettacker"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/Nettacker not found. Skipping Nettacker setup."
fi

# subzy
if [ -d "$dir/subzy" ]; then
    echo "Setting up subzy."
    cd "$dir/subzy" || { echo "Failed to cd into $dir/subzy"; exit 1; }
    go build
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/subzy not found. Skipping subzy setup."
fi

# autossrf (SSTImap)
if [ -d "$dir/autossrf" ]; then
    echo "Setting up autossrf."
    cd "$dir/autossrf" || { echo "Failed to cd into $dir/autossrf"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/autossrf not found. Skipping autossrf setup."
fi

# xsrfprobe (system-wide install, no cd required)
echo "Setting up xsrfprobe."
pip3 install --break-system-packages xsrfprobe

# SSTImap
if [ -d "$dir/SSTImap" ]; then
    echo "Setting up SSTImap."
    cd "$dir/SSTImap" || { echo "Failed to cd into $dir/SSTImap"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/SSTImap not found. Skipping SSTImap setup."
fi

# XSStrike
if [ -d "$dir/XSStrike" ]; then
    echo "Setting up XSStrike."
    cd "$dir/XSStrike" || { echo "Failed to cd into $dir/XSStrike"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/XSStrike not found. Skipping XSStrike setup."
fi

# massdns
if [ -d "$dir/massdns" ]; then
    echo "Setting up Massdns."
    cd "$dir/massdns" || { echo "Failed to cd into $dir/massdns"; exit 1; }
    make
    cd bin/
    sudo mv massdns /usr/bin/massdns
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/massdns not found. Skipping massdns setup."
fi

# Subhunter
if [ -d "$dir/Subhunter" ]; then
    echo "Setting up Subhunter."
    cd "$dir/Subhunter" || { echo "Failed to cd into $dir/Subhunter"; exit 1; }
    go build subhunter.go
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/Subhunter not found. Skipping Subhunter setup."
fi

# gf
if [ -d "$dir/gf" ]; then
    echo "Setting up gf."
    cd "$dir/gf" || { echo "Failed to cd into $dir/gf"; exit 1; }
    go build main.go
    sudo mv main /usr/bin/gf
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/gf not found. Skipping gf setup."
fi

# Gf-Patterns
if [ -d "$dir/Gf-Patterns" ]; then
    echo "Setting up Gf-Patterns."
    cd "$dir/Gf-Patterns" || { echo "Failed to cd into $dir/Gf-Patterns"; exit 1; }
    mkdir -p ~/.gf
    mv *.json ~/.gf
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/Gf-Patterns not found. Skipping Gf-Patterns setup."
fi

# CVESeeker
if [ -d "$dir/CVESeeker" ]; then
    echo "Setting up CVESeeker."
    cd "$dir/CVESeeker" || { echo "Failed to cd into $dir/CVESeeker"; exit 1; }
    pip3 install --break-system-packages -r requirements.txt
    pip3 install --break-system-packages colorama
    cd "$SCRIPT_DIR"
else
    echo "Directory $dir/CVESeeker not found. Skipping CVESeeker setup."
fi

echo "All setup tasks completed."
