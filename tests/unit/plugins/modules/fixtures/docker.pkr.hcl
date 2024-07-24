packer {
  required_plugins {
    docker = {
      version = "~> 1.0"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "example" {
  image = "hashicorp/packer"
}

build {
  sources = ["source.docker.example"]
}
