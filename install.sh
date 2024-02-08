#!/bin/bash

echo "1. Install; 2. Uninstall"
read -p "Select an option [1|2]: " OPTION

PERPLEXITY_PATH="$HOME/.local/bin/perplexity-cli"

function setup() {
  sudo apt install -y python3 python3-pip python3-venv
  python3 -m venv ppl-ai-venv
  source ppl-ai-venv/bin/activate
  pip install -r requirements.txt
  deactivate
}
function install() {
  setup
  mkdir -p $HOME/.local/bin
  cat << EOF > $PERPLEXITY_PATH
#!/bin/bash
source  $PWD/ppl-ai-venv/bin/activate
python3 $PWD/perplexity.ai-cli.py
deactivate
EOF
  chmod +x $PERPLEXITY_PATH
}

function uninstall() {
rm $PERPLEXITY_PATH
}

case $OPTION in
  "1")
    echo "installing... $PERPLEXITY_PATH"
    install
    ;;
  "2")
    echo "removing... $PERPLEXITY_PATH"
    uninstall
    ;;
esac
