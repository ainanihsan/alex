FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Install Node.js and system dependencies for Chromium
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y \
    nodejs \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and its browsers globally
# Install the MCP server package which will use these browsers
RUN npm install -g @playwright/mcp
RUN npx -y playwright install chromium

# Set environment variables for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Install Python package manager
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Install Python dependencies during build
# uv will automatically install packages for the container's architecture (linux/amd64)
RUN uv sync --frozen --no-install-project

# Copy application code
COPY *.py ./

# Expose port
EXPOSE 8000

# Run the application (dependencies already installed)
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]