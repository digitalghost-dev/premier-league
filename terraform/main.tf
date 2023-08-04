terraform {
    required_providers {
    google = {
        source = "hashicorp/google"
        version = "4.51.0"
        }
    }
}

# ------ Variables ------
variable "email_address" {
    type        = string
    description = "email address"
}

variable "user" {
    type        = string
    description = "user name"
}

variable "public_key_path" {
    type        = string
    description = "path to public key"
}

variable "private_key_path" {
    type        = string
    description = "path to private key"
}

variable "project_id" {
    type        = string
    description = "project id"
}

# ------ Compute Engine Resource ------
resource "google_compute_instance" "premier-league-vm" {
    name         = "premier-league-vm"
    machine_type = "e2-small"
    zone         = "us-central1-a"
    project      = var.project_id
    tags         = ["premier-league", "virtual-machine", "http", "https"]

    metadata =  {
        ssh-keys = "${var.user}:${file(var.public_key_path)}"
    }

    boot_disk {
        initialize_params {
            image = "debian-cloud/debian-11"
        }
    }

    network_interface {
        network = "https://www.googleapis.com/compute/v1/projects/${var.project_id}/global/networks/default"
        subnetwork         = "https://www.googleapis.com/compute/v1/projects/${var.project_id}/regions/us-central1/subnetworks/default"
        subnetwork_project = var.project_id
        access_config {
        // Ephemeral public IP
        }
    }

    service_account {
        email  = var.email_address
        scopes = ["cloud-platform"]
    }

    provisioner "remote-exec" {
        connection {
            type        = "ssh"
            user        = var.user
            host        = google_compute_instance.premier-league-vm.network_interface[0].access_config[0].nat_ip
            private_key = file(var.private_key_path)
        }
        script = "./installations.sh"
        # inline = [
           
        # ]
    }
}