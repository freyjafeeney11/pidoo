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
ollama serve > /dev/null 2>&1 & 
sleep 3
ollama pull llama3.2:3b

# 3. Create a hidden directory for Pidoo in the user's home folder
mkdir -p ~/.pidoo

# 4. Set up a Python Virtual Environment and install dependencies
echo "Setting up Python environment..."
python3 -m venv ~/.pidoo/venv
~/.pidoo/venv/bin/pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    ~/.pidoo/venv/bin/pip install -r requirements.txt
else
    ~/.pidoo/venv/bin/pip install requests
fi

# 5. Copy the main script to the hidden folder
if [ -f "pidoo.py" ]; then
    cp pidoo.py ~/.pidoo/
else
    echo "⚠️ Warning: pidoo.py not found in current directory. Make sure it's placed there."
fi

# 6. Create an executable command wrapper in ~/.local/bin
mkdir -p ~/.local/bin
cat << 'EOF' > ~/.local/bin/pidoo
#!/bin/bash
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
fi
~/.pidoo/venv/bin/python ~/.pidoo/pidoo.py "$@"
EOF

chmod +x ~/.local/bin/pidoo

# 7. Force add ~/.local/bin to her Zsh PATH permanently
if ! grep -q ".local/bin" ~/.zshrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
fi
export PATH="$HOME/.local/bin:$PATH"

echo ""
echo "🎉 Pidoo is successfully installed!"
echo "To wake Pidoo up, just open a brand new terminal window and type:"
echo ""
echo "    pidoo"
echo ""
