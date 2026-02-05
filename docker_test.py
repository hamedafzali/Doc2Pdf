#!/usr/bin/env python3
"""
Docker Socket Access Test Script
Tests various Docker connection methods and permissions
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_docker_socket_permissions():
    """Test Docker socket file permissions"""
    logger.info("=== Testing Docker Socket Permissions ===")
    
    try:
        result = subprocess.run(['ls', '-la', '/var/run/docker.sock'], 
                              capture_output=True, text=True)
        logger.info(f"Docker socket permissions: {result.stdout.strip()}")
        
        # Check if docker group exists
        result = subprocess.run(['getent', 'group', 'docker'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Docker group: {result.stdout.strip()}")
        else:
            logger.warning("Docker group not found")
            
        # Check current user groups
        result = subprocess.run(['groups'], capture_output=True, text=True)
        logger.info(f"Current user groups: {result.stdout.strip()}")
        
    except Exception as e:
        logger.error(f"Error checking permissions: {e}")

def test_docker_python_client():
    """Test Docker Python client connection"""
    logger.info("=== Testing Docker Python Client ===")
    
    try:
        import docker
        
        # Method 1: from_env()
        try:
            logger.info("Testing docker.from_env()...")
            client = docker.from_env()
            client.ping()
            logger.info("✅ docker.from_env() works!")
            return True
        except Exception as e:
            logger.warning(f"❌ docker.from_env() failed: {e}")
        
        # Method 2: Direct unix socket
        try:
            logger.info("Testing direct unix socket...")
            client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
            client.ping()
            logger.info("✅ Direct unix socket works!")
            return True
        except Exception as e:
            logger.warning(f"❌ Direct unix socket failed: {e}")
        
        # Method 3: TCP connection
        try:
            logger.info("Testing TCP connection...")
            client = docker.DockerClient(base_url='tcp://localhost:2376')
            client.ping()
            logger.info("✅ TCP connection works!")
            return True
        except Exception as e:
            logger.warning(f"❌ TCP connection failed: {e}")
            
        return False
        
    except ImportError:
        logger.error("❌ Docker Python library not installed")
        return False

def test_docker_cli():
    """Test Docker CLI commands"""
    logger.info("=== Testing Docker CLI ===")
    
    try:
        # Test docker version
        result = subprocess.run(['docker', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ Docker CLI works")
            logger.info(f"Docker version: {result.stdout.split()[2]}")
        else:
            logger.error(f"❌ Docker CLI failed: {result.stderr}")
            return False
            
        # Test docker ps
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ Docker ps works")
            containers = len(result.stdout.strip().split('\n')) - 1
            logger.info(f"Running containers: {containers}")
        else:
            logger.error(f"❌ Docker ps failed: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Docker CLI test failed: {e}")
        return False

def test_container_operations():
    """Test basic container operations"""
    logger.info("=== Testing Container Operations ===")
    
    try:
        import docker
        
        # Try to connect (use working method from previous test)
        client = None
        try:
            client = docker.from_env()
            client.ping()
        except:
            try:
                client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
                client.ping()
            except:
                logger.error("❌ Cannot connect to Docker")
                return False
        
        # Test listing containers
        containers = client.containers.list()
        logger.info(f"✅ Found {len(containers)} containers")
        
        # Test listing images
        images = client.images.list()
        logger.info(f"✅ Found {len(images)} images")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Container operations failed: {e}")
        return False

def main():
    """Run all Docker tests"""
    logger.info("🐳 Starting Docker Socket Access Tests")
    logger.info("=" * 50)
    
    # Test 1: Socket permissions
    test_docker_socket_permissions()
    print()
    
    # Test 2: Docker CLI
    cli_works = test_docker_cli()
    print()
    
    # Test 3: Python client
    python_works = test_docker_python_client()
    print()
    
    # Test 4: Container operations
    if python_works:
        test_container_operations()
    else:
        logger.warning("⏭️ Skipping container operations (Python client failed)")
    
    print()
    logger.info("=" * 50)
    logger.info("🎯 Test Summary:")
    logger.info(f"Docker CLI: {'✅ Working' if cli_works else '❌ Failed'}")
    logger.info(f"Python Client: {'✅ Working' if python_works else '❌ Failed'}")
    
    if cli_works and not python_works:
        logger.info("💡 Docker CLI works but Python client fails - likely a permissions issue")
    elif not cli_works:
        logger.info("💡 Docker CLI fails - Docker daemon may not be running")
    elif cli_works and python_works:
        logger.info("🎉 Everything works! The web manager should work too.")

if __name__ == "__main__":
    main()
