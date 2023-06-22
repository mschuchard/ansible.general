packer {
  required_plugins {
    docker = {
      version = "~> 1.0.8"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "example" {
  image = "centos:7"
}

build {
  sources = ["source.docker.example"]
}
