Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "mwd-dev"

  config.vm.network "forwarded_port", guest: 80, host: 8000

  #config.vm.provision :fabric do |fabric|
  #  fabric.fabfile_path = "./fabfile.py"
  #  fabric.tasks = ["host_type", ]
  #end

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      "modifyvm", :id,
      "--cpus", 2,
      "--memory", "256",
    ]
  end
end
