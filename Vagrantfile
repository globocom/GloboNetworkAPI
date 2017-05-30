VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "private_network", ip: "10.0.0.2", auto_config: "false"
  config.vm.hostname = "NETWORKAPI"
  config.omnibus.chef_version = "12.16.42" # keep this version, the latest version is with bug
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
  end
  config.vm.provision :chef_solo do |chef|
    chef.add_recipe "apt"
    chef.add_recipe "mysql::server"
    chef.json = {
      :mysql => {
         server_root_password: "",
         server_repl_password: "",
         server_debian_password: "",
         port: '3306',
         package_version: '5.6',
         data_dir: '/data-mysql',
         allow_remote_root: true,
         remove_anonymous_Users: true,
         remove_test_database: true,
      }
    }
  end
  config.vm.provision :shell, path: "vagrant_provision.sh"
end
