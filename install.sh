#!/bin/bash

echo "🐾 Installing Pidoo..."

# 1. Check for Ollama, install if missing
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama is already installed."
fi

# 2. Make sure Ollama is running, then pull the model
echo "Pulling the brain (llama3.2:3b)... this might take a minute..."
# Start ollama in the background just in case it isn't running
ollama serve > /dev/null 2>&1 & 
sleep 3
ollama pull llama3.2:3b

# 3. Create a hidden directory for Pidoo in the user's home folder
mkdir -p ~/.pidoo

# 4. Set up a Python Virtual Environment and install dependencies
echo "Setting up Python environment..."
python3 -m venv ~/.pidoo/venv
~/.pidoo/venv/bin/pip install -r requirements.txt

# 5. Copy the main script to the hidden folder
cp pidoo.py ~/.pidoo/

# 6. Create an executable command in ~/.local/bin
mkdir -p ~/.local/bin
cat << 'EOF' > ~/.local/bin/pidoo
#!/bin/bash
# Automatically start ollama in the background if it's not running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
fi
~/.pidoo/venv/bin/python ~/.pidoo/pidoo.py "$@"
EOF

chmod +x ~/.local/bin/pidoo

echo ""
echo "🎉 Pidoo is successfully installed!"
echo "Make sure ~/.local/bin is in your system's PATH."
echo "To wake Pidoo up, just open a new terminal and type:"
echo ""
echo "    pidoo"
echo ""