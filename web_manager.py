#!/usr/bin/env python3
"""
Web-based Bot Manager for Doc2Pdf Telegram Bot
Provides a web interface to manage the Docker container
"""

import os
import subprocess
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
import docker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Docker client
import os
import logging

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Docker client with better error handling
docker_client = None
DOCKER_AVAILABLE = False

def init_docker_client():
    """Initialize Docker client with multiple fallback methods"""
    global docker_client, DOCKER_AVAILABLE
    
    try:
        # Method 1: Try environment variables
        logger.info("Attempting Docker connection via environment variables...")
        docker_client = docker.from_env()
        docker_client.ping()
        DOCKER_AVAILABLE = True
        logger.info("Docker client initialized successfully via environment")
        return
    except Exception as e:
        logger.warning(f"Environment method failed: {e}")
        
        try:
            # Method 2: Try direct unix socket
            logger.info("Attempting Docker connection via unix socket...")
            docker_client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
            docker_client.ping()
            DOCKER_AVAILABLE = True
            logger.info("Docker client initialized via unix socket")
            return
        except Exception as e2:
            logger.warning(f"Unix socket method failed: {e2}")
            
            try:
                # Method 3: Try TCP connection
                logger.info("Attempting Docker connection via TCP...")
                docker_client = docker.DockerClient(base_url='tcp://localhost:2376')
                docker_client.ping()
                DOCKER_AVAILABLE = True
                logger.info("Docker client initialized via TCP")
                return
            except Exception as e3:
                logger.error(f"TCP method failed: {e3}")
                DOCKER_AVAILABLE = False
                logger.error("All Docker connection methods failed")
                return

# Initialize Docker client
init_docker_client()

# Configuration
CONTAINER_NAME = "doc2pdf-bot"
IMAGE_NAME = "doc2pdf-bot"

class BotManager:
    def __init__(self):
        self.container_name = CONTAINER_NAME
        self.image_name = IMAGE_NAME
    
    def get_container_status(self):
        """Get current container status"""
        if not DOCKER_AVAILABLE:
            return {"status": "docker_unavailable", "message": "Docker not available"}
        
        try:
            container = docker_client.containers.get(self.container_name)
            status = container.status
            return {
                "status": status,
                "container_id": container.id[:12],
                "created": container.attrs['Created'],
                "image": container.image.tags[0] if container.image.tags else "unknown"
            }
        except docker.errors.NotFound:
            return {"status": "not_found", "message": "Container not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def start_container(self):
        """Start the bot container"""
        if not DOCKER_AVAILABLE:
            return {"success": False, "message": "Docker not available"}
        
        try:
            # Check if container exists
            try:
                container = docker_client.containers.get(self.container_name)
                if container.status == "running":
                    return {"success": False, "message": "Container already running"}
                container.start()
                return {"success": True, "message": "Container started successfully"}
            except docker.errors.NotFound:
                # Container doesn't exist, create it
                env_vars = {
                    'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                    'DEBUG_MODE': os.getenv('DEBUG_MODE', 'false')
                }
                
                if not env_vars['TELEGRAM_BOT_TOKEN']:
                    return {"success": False, "message": "TELEGRAM_BOT_TOKEN not set"}
                
                container = docker_client.containers.run(
                    self.image_name,
                    name=self.container_name,
                    environment=env_vars,
                    volumes={
                        os.path.abspath('debug_output'): {
                            'bind': '/app/debug_output',
                            'mode': 'rw'
                        }
                    },
                    restart_policy={"Name": "unless-stopped"},
                    detach=True
                )
                return {"success": True, "message": f"Container created and started: {container.id[:12]}"}
                
        except Exception as e:
            logger.error(f"Error starting container: {e}")
            return {"success": False, "message": str(e)}
    
    def stop_container(self):
        """Stop the bot container"""
        if not DOCKER_AVAILABLE:
            return {"success": False, "message": "Docker not available"}
        
        try:
            container = docker_client.containers.get(self.container_name)
            container.stop()
            return {"success": True, "message": "Container stopped successfully"}
        except docker.errors.NotFound:
            return {"success": False, "message": "Container not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def restart_container(self):
        """Restart the bot container"""
        stop_result = self.stop_container()
        if not stop_result["success"]:
            return stop_result
        return self.start_container()
    
    def get_container_logs(self, lines=100):
        """Get container logs"""
        if not DOCKER_AVAILABLE:
            return {"success": False, "message": "Docker not available"}
        
        try:
            container = docker_client.containers.get(self.container_name)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            return {"success": True, "logs": logs}
        except docker.errors.NotFound:
            return {"success": False, "message": "Container not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def rebuild_image(self):
        """Rebuild the Docker image"""
        if not DOCKER_AVAILABLE:
            return {"success": False, "message": "Docker not available"}
        
        try:
            # Stop and remove container
            try:
                container = docker_client.containers.get(self.container_name)
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                pass
            
            # Build image
            image, build_logs = docker_client.images.build(
                path=".",
                tag=self.image_name,
                rm=True
            )
            
            return {"success": True, "message": f"Image rebuilt: {image.id[:12]}"}
            
        except Exception as e:
            logger.error(f"Error rebuilding image: {e}")
            return {"success": False, "message": str(e)}

# Initialize bot manager
bot_manager = BotManager()

@app.route('/')
def index():
    """Main dashboard"""
    status = bot_manager.get_container_status()
    return render_template('dashboard.html', status=status)

@app.route('/api/status')
def api_status():
    """Get container status"""
    return jsonify(bot_manager.get_container_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start container"""
    return jsonify(bot_manager.start_container())

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop container"""
    return jsonify(bot_manager.stop_container())

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """Restart container"""
    return jsonify(bot_manager.restart_container())

@app.route('/api/logs')
def api_logs():
    """Get container logs"""
    lines = request.args.get('lines', 100, type=int)
    return jsonify(bot_manager.get_container_logs(lines))

@app.route('/api/rebuild', methods=['POST'])
def api_rebuild():
    """Rebuild Docker image"""
    return jsonify(bot_manager.rebuild_image())

@app.route('/logs')
def logs_page():
    """Logs page"""
    return render_template('logs.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
