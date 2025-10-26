#!/bin/bash

# TerraMind setup script
# AI for sustainable agriculture platform

echo "setting up TerraMind, THE AI for sustainable agriculture"
echo "========================================================"

# check if python is installed
if ! command -v python3 &> /dev/null; then
    echo "python 3 is required but not installed. please install python 3.8+ and try again"
    exit 1
fi

# check if node.js is installed
if ! command -v node &> /dev/null; then
    echo "node.js is required but not installed. please install node.js 16+ and try again"
    exit 1
fi

echo "python and node.js are installed"

# create necessary directories
echo "creating project directories..."
mkdir -p reports data models logs

# backend setup
echo "setting up python backend..."
cd backend

# create virtual environment
python3 -m venv venv
source venv/bin/activate

# install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "backend dependencies installed"

# frontend setup
echo "setting up react frontend..."
cd ../frontend

# install node.js dependencies
npm install

echo "frontend dependencies installed"

# create environment file
echo "creating environment configuration..."
cd ../backend
if [ ! -f .env ]; then
    cp env.example .env
    echo "created .env file. please update with your API keys:"
    echo "   - OPENWEATHER_API_KEY"
    echo "   - SENTINEL_HUB_KEY"
    echo "   - LANDSAT_API_KEY"
fi

cd ..

# create startup scripts
echo "creating startup scripts..."

# backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x start_backend.sh

# frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm start
EOF
chmod +x start_frontend.sh

# docker setup (optional)
if command -v docker &> /dev/null; then
    echo "docker detected. creating docker setup..."
    echo "   run 'docker-compose up' to start with docker"
fi

echo ""
echo "TerraMind setup completed!"
echo ""
echo "next steps:"
echo "1. update backend/.env with your API keys"
echo "2. start the backend: ./start_backend.sh"
echo "3. start the frontend: ./start_frontend.sh"
echo "4. open http://localhost:3000 in your browser"
echo ""
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "happy farming with TerraMind!"