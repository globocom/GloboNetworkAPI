VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "hashicorp/precise32"
  config.vm.network "private_network", ip:"10.0.0.2"

  config.omnibus.chef_version = :latest
  config.vm.provision :chef_solo do |chef|
    chef.add_recipe "apt"
    chef.add_recipe "mysql::server"
    chef.json = {
      :mysql => {
         server_root_password: "password",
         server_repl_password: "password",
         server_debian_password: "password",
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
